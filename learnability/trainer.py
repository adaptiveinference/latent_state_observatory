import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import utils
import hyper_parameters as hp

# ============================================================
# Dataset Wrapper
# ============================================================
class TorchDataset(Dataset):
    def __init__(self, X, y, x_dtype=None):
        if x_dtype is None:
            x_arr = np.asarray(X)
            x_dtype = torch.long if np.issubdtype(x_arr.dtype, np.integer) else torch.float32
        self.X = torch.tensor(X, dtype=x_dtype)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ============================================================
# Train / Eval Split
# ============================================================
def train_test_split(X, y, test_ratio=0.5):
    N = len(X)
    idx = np.random.permutation(N)
    split = int(N * (1 - test_ratio))
    train_idx = idx[:split]
    test_idx  = idx[split:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


# ============================================================
# Core Trainer
# ============================================================
class Trainer:
    def __init__(
        self,
        model,
        device="cpu",
        lr=1e-3,
        batch_size=256,
        epochs=20,
        weight_decay=0.0,
    ):
        self.is_sklearn_model = getattr(model, "is_sklearn_model", False)
        self.expects_long_input = getattr(model, "expects_long_input", False)
        self.model = model if self.is_sklearn_model else model.to(device)
        self.device = device
        self.epochs = epochs
        self.verbose_ = False
        self.batch_size = batch_size

        if self.is_sklearn_model:
            self.criterion = None
            self.optimizer = None
        else:
            self.criterion = nn.CrossEntropyLoss()
            self.optimizer = torch.optim.Adam(
                self.model.parameters(),
                lr=lr,
                weight_decay=weight_decay,
            )

        self.temperature_ = 1.0

    def _x_dtype(self):
        return torch.long if self.expects_long_input else torch.float32

    def verbose(self, v):
        self.verbose_ = v
        return self

    def _apply_temperature(self, logits, temperature=None):
        T = self.temperature_ if temperature is None else temperature
        T = max(float(T), 1e-6)
        return logits / T

    def _run_epoch(self, loader, train=True):
        total_loss = 0.0
        total = 0
        self.model.train() if train else self.model.eval()

        for X, y in loader:
            X = X.to(self.device)
            y = y.to(self.device)

            if train:
                self.optimizer.zero_grad()

            logits = self.model(X)
            loss = self.criterion(logits, y)

            if train:
                loss.backward()
                self.optimizer.step()

            total_loss += loss.item() * X.size(0)
            total += X.size(0)

        return total_loss / total

    def _sklearn_nll_from_probs(self, probs, y, log_base=2.0):
        y_arr = np.asarray(y, dtype=np.int64)
        probs = np.clip(probs, 1e-12, 1.0)
        p_true = probs[np.arange(len(y_arr)), y_arr]
        nll_nat = -np.log(p_true).mean()
        return nll_nat / np.log(log_base) if log_base != np.e else nll_nat

    def _fit_sklearn(self, X_train, y_train, X_test=None, y_test=None):
        self.model.fit(X_train, y_train)
        history = {"train_loss": [], "test_loss": []}
        if hasattr(self.model, "predict_proba"):
            history["train_loss"].append(
                self._sklearn_nll_from_probs(self.model.predict_proba(X_train), y_train)
            )
            if X_test is not None and y_test is not None:
                history["test_loss"].append(
                    self._sklearn_nll_from_probs(self.model.predict_proba(X_test), y_test)
                )
        return history

    def _sklearn_probabilities(self, X, temperature=None):
        probs = self.model.predict_proba(X)
        probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
        T = self.temperature_ if temperature is None else temperature
        T = max(float(T), 1e-6)
        if probs.shape[1] == 2 and T != 1.0:
            p1 = probs[:, 1]
            logits = np.log(p1 / (1.0 - p1)) / T
            p1_t = 1.0 / (1.0 + np.exp(-logits))
            probs = np.column_stack([1.0 - p1_t, p1_t])
        return probs

    def fit(self, X, y, split = hp.DEFAULT_DATA_SPLIT):
        X_train, X_test, y_train, y_test = train_test_split(X, y, split["train"])

        # Scikit-learn model 
        if self.is_sklearn_model:
            history = self._fit_sklearn(X_train, y_train, X_test, y_test)
            return history, (X_test, y_test)

        # pytorch models
        train_loader = DataLoader(
            TorchDataset(X_train, y_train, x_dtype=self._x_dtype()),
            batch_size=self.batch_size,
            shuffle=True,
        )
        test_loader = DataLoader(
            TorchDataset(X_test, y_test, x_dtype=self._x_dtype()),
            batch_size=self.batch_size,
            shuffle=False,
        )

        history = {"train_loss": [], "test_loss": []}
        for epoch in range(self.epochs):
            train_loss = self._run_epoch(train_loader, train=True)
            test_loss  = self._run_epoch(test_loader, train=False)
            history["train_loss"].append(train_loss)
            history["test_loss"].append(test_loss)
            if self.verbose_:
                print(f"Epoch {epoch:03d} | train={train_loss:.4f} test={test_loss:.4f}")
        return history, (X_test, y_test)

    def fit_temperature(self, X, y, max_iter=50):
        if self.is_sklearn_model:
            probs = self.model.predict_proba(X)
            probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
            p1 = probs[:, 1]
            logits = torch.tensor(np.log(p1 / (1.0 - p1)), dtype=torch.float32, device=self.device)
            labels = torch.tensor(y, dtype=torch.long, device=self.device)
            binary_logits = torch.stack([-logits / 2.0, logits / 2.0], dim=1)
            log_temperature = torch.tensor([0.0], device=self.device, requires_grad=True)
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.LBFGS([log_temperature], lr=0.1, max_iter=max_iter, line_search_fn="strong_wolfe")
            def closure():
                optimizer.zero_grad()
                temperature = torch.exp(log_temperature)
                loss = criterion(binary_logits / temperature, labels)
                loss.backward()
                return loss
            optimizer.step(closure)
            self.temperature_ = max(float(torch.exp(log_temperature).item()), 1e-6)
            if self.verbose_:
                print(f"Learned temperature = {self.temperature_:.6f}")
            return self.temperature_

        loader = DataLoader(
            TorchDataset(X, y, x_dtype=self._x_dtype()),
            batch_size=self.batch_size,
            shuffle=False,
        )
        self.model.eval()
        logits_list = []
        labels_list = []
        with torch.no_grad():
            for Xb, yb in loader:
                Xb = Xb.to(self.device)
                yb = yb.to(self.device)
                logits_list.append(self.model(Xb))
                labels_list.append(yb)
        logits = torch.cat(logits_list, dim=0)
        labels = torch.cat(labels_list, dim=0)

        log_temperature = torch.tensor([0.0], device=self.device, requires_grad=True)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([log_temperature], lr=0.1, max_iter=max_iter, line_search_fn="strong_wolfe")
        def closure():
            optimizer.zero_grad()
            temperature = torch.exp(log_temperature)
            loss = criterion(logits / temperature, labels)
            loss.backward()
            return loss
        optimizer.step(closure)
        self.temperature_ = max(float(torch.exp(log_temperature).item()), 1e-6)
        if self.verbose_:
            print(f"Learned temperature = {self.temperature_:.6f}")
        return self.temperature_

    # =============================================================
    # Negative log-likelihood
    # =============================================================
    def evaluate_nll(self, X, y, log_base=2.0, temperature=None):
        if self.is_sklearn_model:
            probs = self._sklearn_probabilities(X, temperature=temperature)
            nll = self._sklearn_nll_from_probs(probs, y, log_base=log_base)
            y_arr = np.asarray(y, dtype=np.int64)
            Hy = utils._binary_entropy_bits(np.mean(y_arr == 1))
            score = 1.0 - nll / Hy
            return nll, score

        loader = DataLoader(
            TorchDataset(X, y, x_dtype=self._x_dtype()),
            batch_size=self.batch_size,
            shuffle=False,
        )
        self.model.eval()
        total_nll = 0.0
        total = 0
        with torch.no_grad():
            for Xb, yb in loader:
                Xb = Xb.to(self.device)
                yb = yb.to(self.device)
                logits = self._apply_temperature(self.model(Xb), temperature=temperature)
                log_probs = torch.log_softmax(logits, dim=1)
                nll = -log_probs.gather(1, yb.unsqueeze(1)).squeeze(1)
                if log_base == 2.0:
                    nll = nll / torch.log(torch.tensor(2.0, device=nll.device))
                total_nll += nll.sum().item()
                total += Xb.size(0)
        nll = total_nll / total
        Hy = utils._binary_entropy_bits(np.mean(np.asarray(y) == 1))
        score = 1.0 - nll / Hy
        return nll, score


    # =============================================================
    # F1 score
    # =============================================================
    def evaluate_f1(self, X, y):
        if self.is_sklearn_model:
            y_true = np.asarray(y, dtype=np.int64)
            y_pred = self.model.predict(X)
        else:
            loader = DataLoader(
                TorchDataset(X, y, x_dtype=self._x_dtype()),
                batch_size=self.batch_size,
                shuffle=False,
            )
            self.model.eval()
            y_true_parts = []
            y_pred_parts = []
            with torch.no_grad():
                for Xb, yb in loader:
                    Xb = Xb.to(self.device)
                    preds = torch.argmax(self.model(Xb), dim=1)
                    y_true_parts.append(yb.cpu())
                    y_pred_parts.append(preds.cpu())
            y_true = torch.cat(y_true_parts).numpy()
            y_pred = torch.cat(y_pred_parts).numpy()

        tp = ((y_true == 1) & (y_pred == 1)).sum()
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return 2.0 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0


    # =============================================================
    # Area under ROC curve
    # =============================================================
    def evaluate_auc(self, X, y):
        """
        Computes ROC-AUC.

        Returns:
            auc (float)
        """
        from sklearn.metrics import roc_auc_score

        if self.is_sklearn_model:
            # sklearn models already give probabilities
            probs = self.model.predict_proba(X)[:, 1]
            y_true = np.asarray(y, dtype=np.int64)
            return roc_auc_score(y_true, probs)

        # torch branch
        loader = DataLoader(
            TorchDataset(X, y, x_dtype=self._x_dtype()),
            batch_size=self.batch_size,
            shuffle=False,
        )

        self.model.eval()
        probs_list = []
        y_list = []

        with torch.no_grad():
            for Xb, yb in loader:
                Xb = Xb.to(self.device)

                logits = self.model(Xb)
                probs = torch.softmax(logits, dim=1)[:, 1]  # P(y=1)

                probs_list.append(probs.cpu())
                y_list.append(yb.cpu())

        y_true = torch.cat(y_list).numpy()
        probs  = torch.cat(probs_list).numpy()

        return roc_auc_score(y_true, probs)