from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class MLPConfig:
    input_dim: int
    out_classes: int
    num_hidden_layers: int = 2
    hidden_layer_width: int = 128
    dropout: float = 0.0
    activation: str = "relu"


@dataclass
class GMMConfig:
    input_dim: int
    out_classes: int
    num_mixtures: int = 4
    init_std: float = 1.0
    min_var: float = 1e-4
    class_prior_logits_init: float = 0.0


@dataclass
class TransformerConfig:
    input_dim: int
    out_classes: int
    seq_len: int
    d_model: int = 128
    nhead: int = 8
    num_layers: int = 4
    dim_feedforward: int = 512
    dropout: float = 0.1
    use_learned_pos_emb: bool = True
    input_proj_bias: bool = True


@dataclass
class GBTConfig:
    """
    sklearn HistGradientBoostingClassifier config.
    This is not a torch.nn.Module.
    """
    backend: str = "sklearn_hist"
    out_classes: int = 2
    max_iter: int = 100
    learning_rate: float = 0.08
    max_leaf_nodes: int = 15
    max_depth: int | None = None
    l2_regularization: float = 0.0
    min_samples_leaf: int = 50
    validation_fraction: float | None = 0.1
    n_iter_no_change: int | None = 20
    random_state: int = 42


@dataclass
class LightGBMConfig:
    """
    LightGBM LGBMClassifier config.
    This is not a torch.nn.Module.

    For your Avazu setup, X is expected to be hashed integer features:
        shape = (N, num_fields)
    """
    backend: str = "lightgbm"
    out_classes: int = 2

    n_estimators: int = 700
    learning_rate: float = 0.03
    num_leaves: int = 63
    max_depth: int = -1

    min_child_samples: int = 50
    min_child_weight: float = 1e-3
    reg_alpha: float = 0.0
    reg_lambda: float = 0.3

    subsample: float = 0.9
    subsample_freq: int = 1
    colsample_bytree: float = 0.9

    objective: str = "binary"
    random_state: int = 42
    n_jobs: int = -1
    verbosity: int = -1


@dataclass
class CatBoostConfig:
    backend: str = "catboost"
    out_classes: int = 2

    iterations: int = 700
    learning_rate: float = 0.03
    depth: int = 6
    l2_leaf_reg: float = 5.0

    loss_function: str = "Logloss"
    eval_metric: str = "Logloss"

    random_seed: int = 42
    verbose: bool = False
    thread_count: int = -1


def _get_activation(name: str) -> nn.Module:
    name = name.lower()
    if name == "relu":
        return nn.ReLU()
    if name == "gelu":
        return nn.GELU()
    if name == "tanh":
        return nn.Tanh()
    if name == "silu":
        return nn.SiLU()
    raise ValueError(f"Unsupported activation: {name}")


class MLPClassifier(nn.Module):
    def __init__(self, config: MLPConfig):
        super().__init__()
        if config.num_hidden_layers < 0:
            raise ValueError("num_hidden_layers must be >= 0")
        if config.hidden_layer_width <= 0:
            raise ValueError("hidden_layer_width must be > 0")
        if config.input_dim <= 0 or config.out_classes <= 1:
            raise ValueError("Invalid input_dim or out_classes")

        layers = []
        in_dim = config.input_dim

        for _ in range(config.num_hidden_layers):
            layers.append(nn.Linear(in_dim, config.hidden_layer_width))
            layers.append(_get_activation(config.activation))
            if config.dropout > 0:
                layers.append(nn.Dropout(config.dropout))
            in_dim = config.hidden_layer_width

        layers.append(nn.Linear(in_dim, config.out_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 2:
            raise ValueError(f"MLPClassifier expects x with shape (B, D), got {tuple(x.shape)}")
        return self.network(x)


class GaussianMixtureClassifier(nn.Module):
    def __init__(self, config: GMMConfig):
        super().__init__()
        if config.input_dim <= 0 or config.out_classes <= 1:
            raise ValueError("Invalid input_dim or out_classes")
        if config.num_mixtures <= 0:
            raise ValueError("num_mixtures must be > 0")
        if config.init_std <= 0 or config.min_var <= 0:
            raise ValueError("init_std and min_var must be > 0")

        self.input_dim = config.input_dim
        self.out_classes = config.out_classes
        self.num_mixtures = config.num_mixtures
        self.min_var = config.min_var

        self.mixture_logits = nn.Parameter(torch.zeros(config.out_classes, config.num_mixtures))
        self.means = nn.Parameter(
            0.05 * torch.randn(config.out_classes, config.num_mixtures, config.input_dim)
        )
        init_log_var = math.log(config.init_std ** 2)
        self.log_vars = nn.Parameter(
            torch.full(
                (config.out_classes, config.num_mixtures, config.input_dim),
                fill_value=init_log_var,
            )
        )
        self.class_prior_logits = nn.Parameter(
            torch.full((config.out_classes,), fill_value=config.class_prior_logits_init)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 2:
            raise ValueError(
                f"GaussianMixtureClassifier expects x with shape (B, D), got {tuple(x.shape)}"
            )
        if x.shape[1] != self.input_dim:
            raise ValueError(f"Expected input_dim={self.input_dim}, got D={x.shape[1]}")

        x_exp = x[:, None, None, :]
        means = self.means[None, :, :, :]
        vars_ = F.softplus(self.log_vars) + self.min_var
        vars_ = vars_[None, :, :, :]

        diff = x_exp - means
        mahal = (diff * diff) / vars_
        log_det = torch.log(vars_)

        log_prob_components = -0.5 * (
            mahal.sum(dim=-1)
            + log_det.sum(dim=-1)
            + self.input_dim * math.log(2.0 * math.pi)
        )

        log_mix = F.log_softmax(self.mixture_logits, dim=-1)[None, :, :]
        log_px_given_y = torch.logsumexp(log_mix + log_prob_components, dim=-1)
        log_py = F.log_softmax(self.class_prior_logits, dim=0)[None, :]
        return log_py + log_px_given_y


class TransformerClassifier(nn.Module):
    def __init__(self, config: TransformerConfig):
        super().__init__()
        if config.seq_len <= 0:
            raise ValueError("seq_len must be > 0")
        if config.input_dim <= 0 or config.out_classes <= 1:
            raise ValueError("Invalid input_dim or out_classes")
        if config.d_model % config.nhead != 0:
            raise ValueError("d_model must be divisible by nhead")

        self.seq_len = config.seq_len
        self.input_dim = config.input_dim
        self.d_model = config.d_model

        self.input_proj = nn.Linear(config.input_dim, config.d_model, bias=config.input_proj_bias)

        if config.use_learned_pos_emb:
            self.pos_emb = nn.Parameter(torch.zeros(1, config.seq_len, config.d_model))
            nn.init.normal_(self.pos_emb, mean=0.0, std=0.02)
        else:
            self.register_buffer(
                "pos_emb",
                self._sinusoidal_pos_emb(config.seq_len, config.d_model),
                persistent=False,
            )

        enc_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            batch_first=True,
            norm_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=config.num_layers)
        self.norm = nn.LayerNorm(config.d_model)
        self.head = nn.Linear(config.d_model, config.out_classes)

    @staticmethod
    def _sinusoidal_pos_emb(seq_len: int, d_model: int) -> torch.Tensor:
        position = torch.arange(seq_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10000.0) / d_model)
        )
        pe = torch.zeros(seq_len, d_model, dtype=torch.float32)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 3:
            raise ValueError(
                f"TransformerClassifier expects x with shape (B, T, D), got {tuple(x.shape)}"
            )
        if x.shape[1] != self.seq_len:
            raise ValueError(f"Expected seq_len={self.seq_len}, got T={x.shape[1]}")
        if x.shape[2] != self.input_dim:
            raise ValueError(f"Expected input_dim={self.input_dim}, got D={x.shape[2]}")

        h = self.input_proj(x)
        h = h + self.pos_emb
        h = self.encoder(h)
        h_last = self.norm(h[:, -1, :])
        return self.head(h_last)


class SklearnHistGBTClassifier:
    is_sklearn_model = True

    def __init__(self, config: GBTConfig):
        if config.backend != "sklearn_hist":
            raise ValueError(f"GBTConfig backend must be 'sklearn_hist', got {config.backend}")
        if config.out_classes != 2:
            raise ValueError("SklearnHistGBTClassifier currently supports binary classification only")

        from sklearn.ensemble import HistGradientBoostingClassifier

        self.config = config
        self.model = HistGradientBoostingClassifier(
            max_iter=config.max_iter,
            learning_rate=config.learning_rate,
            max_leaf_nodes=config.max_leaf_nodes,
            max_depth=config.max_depth,
            l2_regularization=config.l2_regularization,
            min_samples_leaf=config.min_samples_leaf,
            validation_fraction=config.validation_fraction,
            n_iter_no_change=config.n_iter_no_change,
            random_state=config.random_state,
        )

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)


class LightGBMClassifierWrapper:
    is_sklearn_model = True

    def __init__(self, config: LightGBMConfig):
        if config.backend != "lightgbm":
            raise ValueError(f"LightGBMConfig backend must be 'lightgbm', got {config.backend}")
        if config.out_classes != 2:
            raise ValueError("LightGBMClassifierWrapper currently supports binary classification only")

        try:
            from lightgbm import LGBMClassifier
        except ImportError as e:
            raise ImportError(
                "LightGBM is not installed. Install it with:\n\n"
                "    pip install lightgbm\n"
            ) from e

        self.config = config
        self.model = LGBMClassifier(
            objective=config.objective,
            n_estimators=config.n_estimators,
            learning_rate=config.learning_rate,
            num_leaves=config.num_leaves,
            max_depth=config.max_depth,
            min_child_samples=config.min_child_samples,
            min_child_weight=config.min_child_weight,
            reg_alpha=config.reg_alpha,
            reg_lambda=config.reg_lambda,
            subsample=config.subsample,
            subsample_freq=config.subsample_freq,
            colsample_bytree=config.colsample_bytree,
            random_state=config.random_state,
            n_jobs=config.n_jobs,
            verbosity=config.verbosity,
        )

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)


class CatBoostClassifierWrapper:
    """
    sklearn-style CatBoost wrapper.

    Note:
    - If your Avazu features are already hashed integers, this treats them as numeric.
    - CatBoost is strongest when given raw categorical columns, but this still works.
    """
    is_sklearn_model = True

    def __init__(self, config: CatBoostConfig):
        if config.backend != "catboost":
            raise ValueError(
                f"CatBoostConfig backend must be 'catboost', got {config.backend}"
            )
        if config.out_classes != 2:
            raise ValueError(
                "CatBoostClassifierWrapper currently supports binary classification only"
            )

        try:
            from catboost import CatBoostClassifier
        except ImportError as e:
            raise ImportError(
                "CatBoost is not installed. Install it with:\n\n"
                "    pip install catboost\n"
            ) from e

        self.config = config
        self.model = CatBoostClassifier(
            iterations=config.iterations,
            learning_rate=config.learning_rate,
            depth=config.depth,
            l2_leaf_reg=config.l2_leaf_reg,
            loss_function=config.loss_function,
            eval_metric=config.eval_metric,
            random_seed=config.random_seed,
            verbose=config.verbose,
            thread_count=config.thread_count,
        )

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X).astype(int).reshape(-1)

    def predict_proba(self, X):
        return self.model.predict_proba(X)


def build_model(model_name: str, model_config: Dict[str, Any]):
    model_name = model_name.lower()

    if model_name == "mlp":
        return MLPClassifier(MLPConfig(**model_config))
    if model_name == "gmm":
        return GaussianMixtureClassifier(GMMConfig(**model_config))
    if model_name == "transformer":
        return TransformerClassifier(TransformerConfig(**model_config))
    if model_name in ("gbt", "sklearn_hist", "hist_gbt"):
        return SklearnHistGBTClassifier(GBTConfig(**model_config))
    if model_name in ("lightgbm", "lgbm"):
        return LightGBMClassifierWrapper(LightGBMConfig(**model_config))
    if model_name in ("catboost", "cat"):
        return CatBoostClassifierWrapper(CatBoostConfig(**model_config))
    raise ValueError(f"Unsupported model_name: {model_name}")
