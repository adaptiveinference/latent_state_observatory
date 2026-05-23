from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, List, Sequence
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import random
import utils


def getHistogram(data, binwidth, ax=None):    
    bins = np.arange(min(data), max(data) + binwidth, binwidth)
    n, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

    if ax:
        ax.bar(bin_centers, n, width=binwidth, edgecolor='black')
    
    return bin_edges, n


@dataclass
class DatasetRecord:
    name: str
    d: int
    N: int
    beta: float
    active_dims: int
    w: np.ndarray
    X: np.ndarray
    p_y1_given_x: np.ndarray
    y: np.ndarray
    H_y_given_x: float
    learnability_true: float
    H_y: float

    def serialize(self):
        return dict(
            name = self.name,
            d    = self.d,
            N    = self.N,
            beta = self.beta,
            active_dims = self.active_dims,
            w           = self.w,
            X           = self.X,
            y           = self.y, 
            H_y         = self.H_y,
            H_y_given_x = self.H_y_given_x,
            learnability_true = self.learnability_true

        )


class BernoulliLearnabilityEnsemble:
    """
    Generate an ensemble of synthetic Bernoulli datasets and compute
    ground-truth learnability for each dataset.

    Model:
        t(X) = beta * w^T X
        p(y=1|x) = sigmoid(t(X))
        y ~ Bernoulli(p(y=1|x))

    Notes
    -----
    - active_dims is the number of nonzero entries in w.
    - If feature_blocks is None, defaults to X ~ N(0, I_d).
    - Otherwise, X is generated blockwise with heterogeneous distributions.
    """

    def __init__(
        self,
        d: int,
        N: int,
        beta: float | Sequence[float],
        active_dims: int | Sequence[int],
        feature_blocks: Sequence[Dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> None:
        if d <= 0:
            raise ValueError("d must be positive.")
        if N <= 0:
            raise ValueError("N must be positive.")

        self.d = int(d)
        self.N = int(N)
        self.betas = self._as_list(beta)
        self.active_dims_list = [int(a) for a in self._as_list(active_dims)]
        self.rng = np.random.default_rng(seed)

        for a in self.active_dims_list:
            if not (1 <= a <= self.d):
                raise ValueError(f"active_dims must be in [1, d]. Got {a} for d={self.d}.")

        # Default: original isotropic Gaussian construction
        if feature_blocks is None:
            feature_blocks = [
                {"dims": self.d, "dist": "gaussian", "scale": 1.0}
            ]

        total_dims = sum(int(block["dims"]) for block in feature_blocks)
        if total_dims != self.d:
            raise ValueError(
                f"Sum of feature_blocks dims must equal d. Got {total_dims} vs d={self.d}."
            )

        self.feature_blocks = list(feature_blocks)
        self.datasets: List[DatasetRecord] = []

    @staticmethod
    def _as_list(x: float | int | Sequence[float] | Sequence[int]) -> List[Any]:
        if isinstance(x, (list, tuple, np.ndarray)):
            return list(x)
        return [x]

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        out = np.empty_like(z, dtype=np.float64)
        pos = z >= 0
        neg = ~pos
        out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
        ez = np.exp(z[neg])
        out[neg] = ez / (1.0 + ez)
        return out

    @staticmethod
    def _binary_entropy_bits(p: np.ndarray) -> np.ndarray:
        return utils._binary_entropy_bits(p)

    @staticmethod
    def _empirical_entropy_bits(y: np.ndarray) -> float:
        p1 = float(np.mean(y))
        p0 = 1.0 - p1
        eps = 1e-12
        p0 = max(p0, eps)
        p1 = max(p1, eps)
        return float(-(p0 * np.log2(p0) + p1 * np.log2(p1)))

    def _make_weight(self, active_dims: int) -> np.ndarray:
        w = np.zeros(self.d, dtype=np.float64)

        idx = self.rng.choice(self.d, size=active_dims, replace=False)
        w[idx] = 1.0

        w /= np.linalg.norm(w)
        return w

    def _generate_X(self) -> np.ndarray:
        """
        Generate X blockwise. Supported block specs:
            {"dims": int, "dist": "gaussian", "scale": float}
            {"dims": int, "dist": "uniform",  "scale": float}
            {"dims": int, "dist": "laplace",  "scale": float}

        For uniform, samples are drawn from [-scale, scale].
        """
        X_blocks = []

        for block in self.feature_blocks:
            dims = int(block["dims"])
            dist = str(block.get("dist", "gaussian")).lower()
            scale = float(block.get("scale", 1.0))

            if dist == "gaussian":
                Xi = self.rng.normal(loc=0.0, scale=scale, size=(self.N, dims))
            elif dist == "uniform":
                Xi = self.rng.uniform(low=-scale, high=scale, size=(self.N, dims))
            elif dist == "laplace":
                Xi = self.rng.laplace(loc=0.0, scale=scale, size=(self.N, dims))
            else:
                raise ValueError(f"Unsupported block distribution: {dist}")

            X_blocks.append(Xi)

        return np.concatenate(X_blocks, axis=1)

    def _generate_one(self, beta: float, active_dims: int, name: str) -> DatasetRecord:
        # _make_weight() has randomness in it - it chooses "active_dims" features.
        # Eg active_dims=3 -> Randomly choose 3 features
        retlist = []

        # for i in range(20):
        for i in range(5):
            w = self._make_weight(active_dims=active_dims)
            X = self._generate_X()
            t = beta * (X @ w)
            p = self._sigmoid(t)
            y = self.rng.binomial(n=1, p=p, size=self.N).astype(np.int64)

            H_y_given_x       = float(np.mean(self._binary_entropy_bits(p)))
            H_y               = self._empirical_entropy_bits(y)
            learnability_true = float(1.0 - H_y_given_x / H_y)

            retlist.append(       DatasetRecord(
                                        name=f"{name}_version{i}",
                                        d=self.d,
                                        N=self.N,
                                        beta=float(beta),
                                        active_dims=int(active_dims),
                                        w=w,
                                        X=X,
                                        p_y1_given_x=p,
                                        y=y,
                                        H_y_given_x=H_y_given_x,
                                        learnability_true=learnability_true,
                                        H_y=H_y,
                                    )
            )
        return retlist

    def generate(self) -> List[DatasetRecord]:
        self.datasets = []
        for i, (beta, active_dims) in enumerate(product(self.betas, self.active_dims_list)):
            name = f"dataset_{i:03d}_beta_{beta}_active_{active_dims}"
            dataset = self._generate_one(beta=float(beta), active_dims=int(active_dims), name=name)
            for j, d in enumerate(dataset):
                self.datasets.append(d)
                yield d

        return self.datasets

    def plot(self):
        summary = self.summary()
        L_true =  summary["L_true"]  #[item["L_true"] for item in summary]
        f = plt.figure()
        ax = f.add_subplot(2, 1, 1)
        getHistogram(L_true, 0.005, ax)
        ax.set_xlabel("Learnability")
        ax.set_ylabel("Histogram")
        ax.set_title("Bernoulli ground truth")
        ax.grid(True)

        L_true_sorted = np.sort(np.array(L_true))
        ax = f.add_subplot(2, 1, 2)
        ax.plot(L_true_sorted)
        ax.grid(True)
        ax.set_xlabel("Dataset Index")
        ax.set_ylabel("Learnability")

        f.tight_layout()

    def summary(self) -> List[Dict[str, float | int | str]]:
        if not self.datasets:
            raise RuntimeError("No datasets generated yet. Call generate() first.")

        rows: List[Dict[str, float | int | str]] = []
        for ds in self.datasets:
            rows.append(
                {
                    "name": ds.name,
                    "d": ds.d,
                    "N": ds.N,
                    "beta": ds.beta,
                    "active_dims": ds.active_dims,
                    "H(Y)": ds.H_y,
                    "H(Y|X)": ds.H_y_given_x,
                    "L_true": ds.learnability_true,
                    "y_mean_empirical": float(np.mean(ds.y)),
                }
            )
        return pd.DataFrame(rows)

    def choose_random(self, L_lambda = lambda L: True):
        filtered = [ dataset for dataset in self.datasets if L_lambda(dataset.learnability_true)]
        N = len(filtered)
        assert N > 0, f"Invalid filter for learnability {L_lambda}"

        idx = random.randint(0, N - 1) 
        return filtered[idx]


# ==============================================        
# Test harness
# ==============================================        
if __name__ == "__main__":

    feature_blocks=[
        {"dims": 4, "dist": "gaussian", "scale": 1.5},   # strong signal region
        {"dims": 2, "dist": "gaussian", "scale": 1.0},   # strong signal region
        {"dims": 3, "dist": "gaussian", "scale": 0.25},  # weak signal region
        {"dims": 5, "dist": "uniform",  "scale": 1.0},   # nuisance / different geometry U(-1, 1)
        {"dims": 5, "dist": "uniform",  "scale": 5.0},   # nuisance / different geometry U(-5, 5)
        {"dims": 6, "dist": "laplace",  "scale": 1.0},   # nuisance / different geometry
    ]
    d = sum([item["dims"] for item in feature_blocks])

    # Learnability controls
    beta        = list(np.logspace(-0.1, 1.0, 100)) 
    active_perc = [10, 20, 30, 40,  50, 60, 70, 80, 90, 100]
    
    
    ensemble = BernoulliLearnabilityEnsemble(
        d    = d,
        N    = 5000,
        beta = beta,
        active_dims    = [int(np.ceil(item * d / 100)) for item in active_perc],
        feature_blocks = feature_blocks,
        seed           = 42,
    )
    datasets = ensemble.generate()

    summary = ensemble.summary()
    print(summary)

    result = summary.groupby(['beta', 'active_dims'])['L_true'].mean().reset_index()
    print(result)

    ensemble.plot()
    plt.show()









