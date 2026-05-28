import math
from dataclasses import dataclass, asdict, fields
from collections import deque
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import torch
import torch.nn.functional as F
from scipy.spatial import distance
import scipy.stats as sps


#########################################################################
# Generic utilities
#########################################################################
def crossCorrelation(x, y, normalize=True):
    """
    Compute layerwise cross-correlation between two arrays x, and y

    Parameters
    ----------
    x : np.ndarray
        Shape: [nSteps, 1]

    y : np.ndarray
        Shape: [nSteps, 1]

    normalize : bool
        If True, z-normalize each signal before correlation.

    Returns
    -------
    xcorr : np.ndarray
        Shape: [2*nSteps - 1, 1]

    lags : np.ndarray
        Shape: [2*nSteps - 1]
        Negative lag:
            y leads x
        Positive lag:
            x leads y
    """
    assert x.shape == y.shape

    nSteps = x.shape[0]

    # remove mean
    x = x - np.mean(x)
    y = y - np.mean(y)

    # optional normalization
    if normalize:
        x_std = np.std(x)
        y_std = np.std(y)

        if x_std > 0:
            x = x / x_std

        if y_std > 0:
            y = y / y_std

    # full cross-correlation
    corr = np.correlate(x, y, mode='full')

    # optional normalization by sequence length
    corr = corr / nSteps

    lags = np.arange(-(nSteps - 1), nSteps)

    return corr, lags


#########################################################################
# LLM internal breadcrumbs
#########################################################################
class RollingStats:
    def __init__(self, W):
        self.W = W
        self.window = deque(maxlen=W)
        self.sum = 0.0
        self.sum_sq = 0.0
        self.rolling_mean = None
        self.rolling_var = None

    def update_moving_stats(self, r_t):
        if len(self.window) == self.W:
            old_val = self.window[0]
            self.sum -= old_val
            self.sum_sq -= old_val**2

        self.window.append(r_t)
        self.sum += r_t
        self.sum_sq += r_t**2

        n = len(self.window)
        mean = self.sum / n
        variance = (self.sum_sq / n) - (mean**2)

        self.rolling_mean = mean
        self.rolling_var = max(0.0, variance)


@dataclass
class HiddenState:
    layer_idx: int                 # Hidden layer index. 0 = embed residual, 1..n_layers = post-block residuals.
    layer_output_raw: torch.Tensor # Final-LN-normalized residual vector at latest token.
    layer_output_prob: torch.Tensor# Logit-lens vocab distribution for that residual vector.


@dataclass
class LayerStats:
    layer_idx: int
    cosine_sim: float
    D_js: float
    layer_entropy: float


@dataclass
class AttentionSpectralStats:
    layer_idx: int
    head_idx: int
    spectral_entropy: float
    effective_rank: float
    concentration: float
    top_singular_value: float
    singular_value_sum: float


@dataclass
class MLPGatingStats:
    layer_idx: int
    sparsity_l1_l2: float
    activation_entropy: float
    gate_energy: float
    active_fraction: float
    max_activation: float


@dataclass
class ResidualUpdateStats:
    layer_idx: int
    update_norm: float
    residual_norm: float
    cosine_prev_next: float
    directional_change: float
    attn_update_norm: Optional[float] = None
    mlp_update_norm: Optional[float] = None
    attn_mlp_cosine: Optional[float] = None


def dataclass_list_to_records(items: Optional[Iterable[Any]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    out = []
    for item in items:
        if hasattr(item, "__dataclass_fields__"):
            out.append(asdict(item))
        elif isinstance(item, dict):
            out.append(dict(item))
        else:
            out.append({name: getattr(item, name) for name in dir(item) if not name.startswith("_")})
    return out


def analyze_layers(H_full, H_prior, d_vocab: int):
    """
    Compare primary prompted hidden states against promptless-prior hidden states.
    Kept in utils.py so different experiment runners can reuse the same telemetry
    definition without depending on InferenceHealthTracker internals.
    """
    if not H_full or not H_prior:
        return None
    assert len(H_full) == len(H_prior), (
        f"Mismatched layer counts between true and prior-only inference "
        f"len(H_full):{len(H_full)} != len(H_prior):{len(H_prior)}"
    )

    layerstats = []
    for l, (h_full, h_prior) in enumerate(zip(H_full, H_prior)):
        a = h_full.layer_output_raw.detach().cpu().double().numpy().reshape(-1)
        b = h_prior.layer_output_raw.detach().cpu().double().numpy().reshape(-1)

        denom = np.linalg.norm(a) * np.linalg.norm(b)
        cosine_sim = np.dot(a, b) / denom if denom > 0 else np.nan

        a_prob = h_full.layer_output_prob.detach().cpu().double().numpy().reshape(-1)
        b_prob = h_prior.layer_output_prob.detach().cpu().double().numpy().reshape(-1)
        js_divergence = distance.jensenshannon(a_prob, b_prob) ** 2

        max_entropy = np.log2(d_vocab)
        layer_entropy = sps.entropy(a_prob, base=2) / max_entropy

        layerstats.append(
            LayerStats(
                layer_idx=l,
                cosine_sim=cosine_sim,
                D_js=js_divergence,
                layer_entropy=layer_entropy,
            )
        )
    return layerstats


class InternalProber:
    """
    TransformerLens-facing internal telemetry collector.

    It is intentionally model-runner agnostic: mech_interp_transformerlens.py only
    needs to ask for the cache names and then pass the resulting ActivationCache
    to collect(). Experiments in run.py can decide which collected fields to use.

    For each generated token and layer this collects the z_{p,t,l}-style metrics
    discussed in the semantic-pathway/eigenmode hypothesis, which is:
    "Semantic meaning may correspond to structured transport flow patterns, not individual low-entropy heads".
    This class collects
      1) attention transport spectrum: singular-value entropy/effective rank/concentration
      2) MLP nonlinear gating: sparsity/entropy/energy/active fraction
      3) residual-state update: norm, turn angle, attn-vs-MLP update coupling
    """
    def __init__(
        self,
        model,
        collect_attention: bool = True,
        collect_mlp: bool = True,
        collect_residual: bool = True,
        eps: float = 1e-12,
    ):
        self.model = model
        self.collect_attention = collect_attention
        self.collect_mlp = collect_mlp
        self.collect_residual = collect_residual
        self.eps = eps

    def cache_names_filter(self, name: str) -> bool:
        if name == "hook_embed" or name.endswith("hook_resid_post"):
            return True
        if self.collect_residual and (
            name.endswith("hook_resid_pre")
            or name.endswith("hook_attn_out")
            or name.endswith("hook_mlp_out")
        ):
            return True
        if self.collect_attention and name.endswith("attn.hook_pattern"):
            return True
        if self.collect_mlp and (
            name.endswith("mlp.hook_post")
            or name.endswith("mlp.hook_pre")
            or name.endswith("mlp.hook_mid")
        ):
            return True
        return False

    def collect(self, cache, position: int = -1) -> Dict[str, List[Any]]:
        return {
            "attention_spectral_stats": self.collect_attention_spectral_stats(cache) if self.collect_attention else [],
            "mlp_gating_stats": self.collect_mlp_gating_stats(cache, position=position) if self.collect_mlp else [],
            "residual_update_stats": self.collect_residual_update_stats(cache, position=position) if self.collect_residual else [],
        }

    def collect_attention_spectral_stats(self, cache) -> List[AttentionSpectralStats]:
        stats: List[AttentionSpectralStats] = []
        for layer in range(self.model.cfg.n_layers):
            pattern = self._safe_cache_get(cache, ("pattern", layer))
            if pattern is None:
                pattern = self._safe_cache_get(cache, f"blocks.{layer}.attn.hook_pattern")
            if pattern is None:
                continue

            # TransformerLens pattern shape is usually [batch, head, dest_pos, src_pos].
            pattern = self._to_metric_tensor(pattern)
            if pattern.ndim == 3:
                pattern = pattern.unsqueeze(0)
            pattern = pattern[0]  # [head, T, T]

            for head in range(pattern.shape[0]):
                A = pattern[head]
                if A.numel() == 0:
                    continue
                svals = torch.linalg.svdvals(A)
                svals = svals.detach().double().numpy()
                entropy, eff_rank, concentration = self._spectral_summary(svals)
                stats.append(
                    AttentionSpectralStats(
                        layer_idx=layer,
                        head_idx=head,
                        spectral_entropy=entropy,
                        effective_rank=eff_rank,
                        concentration=concentration,
                        top_singular_value=float(svals[0]) if len(svals) else np.nan,
                        singular_value_sum=float(np.sum(svals)) if len(svals) else np.nan,
                    )
                )
        return stats

    def collect_mlp_gating_stats(self, cache, position: int = -1) -> List[MLPGatingStats]:
        stats: List[MLPGatingStats] = []
        for layer in range(self.model.cfg.n_layers):
            gate = self._safe_cache_get(cache, ("post", layer, "mlp"))
            if gate is None:
                gate = self._safe_cache_get(cache, f"blocks.{layer}.mlp.hook_post")
            if gate is None:
                # Some gated models expose hook_mid rather than hook_post.
                gate = self._safe_cache_get(cache, f"blocks.{layer}.mlp.hook_mid")
            if gate is None:
                continue

            # Shape usually [batch, pos, d_mlp]. Use latest token position.
            g = self._to_metric_tensor(gate)
            if g.ndim == 3:
                g = g[0, position, :]
            elif g.ndim == 2:
                g = g[position, :]
            else:
                g = g.reshape(-1)
            g_abs = torch.abs(g)
            l1 = torch.sum(g_abs).item()
            l2 = torch.linalg.vector_norm(g).item()
            sparsity = l1 / (l2 + self.eps)
            energy = float(torch.sum(g * g).item())
            max_activation = float(torch.max(g_abs).item()) if g_abs.numel() else np.nan
            active_fraction = float(torch.mean((g_abs > 1e-6).float()).item()) if g_abs.numel() else np.nan

            probs = g_abs / (torch.sum(g_abs) + self.eps)
            activation_entropy = float((-(probs * torch.log(probs + self.eps)).sum()).item())

            stats.append(
                MLPGatingStats(
                    layer_idx=layer,
                    sparsity_l1_l2=float(sparsity),
                    activation_entropy=activation_entropy,
                    gate_energy=energy,
                    active_fraction=active_fraction,
                    max_activation=max_activation,
                )
            )
        return stats

    def collect_residual_update_stats(self, cache, position: int = -1) -> List[ResidualUpdateStats]:
        stats: List[ResidualUpdateStats] = []
        prev = self._safe_cache_get(cache, "hook_embed")
        for layer in range(self.model.cfg.n_layers):
            resid_pre = self._safe_cache_get(cache, ("resid_pre", layer))
            resid_post = self._safe_cache_get(cache, ("resid_post", layer))
            if resid_pre is None:
                resid_pre = self._safe_cache_get(cache, f"blocks.{layer}.hook_resid_pre")
            if resid_post is None:
                resid_post = self._safe_cache_get(cache, f"blocks.{layer}.hook_resid_post")

            # Layer 0 can fall back to embedding as pre-state if resid_pre was not cached.
            if resid_pre is None and layer == 0:
                resid_pre = prev
            if resid_pre is None or resid_post is None:
                continue

            x0 = self._latest_vector(resid_pre, position=position)
            x1 = self._latest_vector(resid_post, position=position)
            delta = x1 - x0
            update_norm = float(torch.linalg.vector_norm(delta).item())
            residual_norm = float(torch.linalg.vector_norm(x0).item())
            cos = self._cosine(x0, x1)

            attn_out = self._safe_cache_get(cache, ("attn_out", layer))
            if attn_out is None:
                attn_out = self._safe_cache_get(cache, f"blocks.{layer}.hook_attn_out")
            mlp_out = self._safe_cache_get(cache, ("mlp_out", layer))
            if mlp_out is None:
                mlp_out = self._safe_cache_get(cache, f"blocks.{layer}.hook_mlp_out")

            attn_update_norm = None
            mlp_update_norm = None
            attn_mlp_cosine = None
            if attn_out is not None:
                a = self._latest_vector(attn_out, position=position)
                attn_update_norm = float(torch.linalg.vector_norm(a).item())
            else:
                a = None
            if mlp_out is not None:
                m = self._latest_vector(mlp_out, position=position)
                mlp_update_norm = float(torch.linalg.vector_norm(m).item())
            else:
                m = None
            if a is not None and m is not None:
                attn_mlp_cosine = self._cosine(a, m)

            stats.append(
                ResidualUpdateStats(
                    layer_idx=layer,
                    update_norm=update_norm,
                    residual_norm=residual_norm,
                    cosine_prev_next=cos,
                    directional_change=float(1.0 - cos) if not np.isnan(cos) else np.nan,
                    attn_update_norm=attn_update_norm,
                    mlp_update_norm=mlp_update_norm,
                    attn_mlp_cosine=attn_mlp_cosine,
                )
            )
        return stats

    def flatten_probe_record(self, probe_record: Optional[Dict[str, List[Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        if not probe_record:
            return {}
        return {k: dataclass_list_to_records(v) for k, v in probe_record.items()}

    def _to_metric_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Move telemetry tensors to CPU float32 before metric calculations.

        This lets the model forward/cache remain on MPS/CUDA while avoiding
        backend-specific numerical issues for SVD, norms, entropy, and cosine
        telemetry.
        """
        return tensor.detach().to(device="cpu", dtype=torch.float32)

    def _spectral_summary(self, values: np.ndarray):
        values = np.asarray(values, dtype=float)
        values = np.abs(values)
        total = float(np.sum(values))
        if total <= self.eps or values.size == 0:
            return np.nan, np.nan, np.nan
        p = values / total
        entropy = float(-np.sum(p * np.log(p + self.eps)))
        eff_rank = float(np.exp(entropy))
        concentration = float(np.max(p))
        return entropy, eff_rank, concentration

    def _latest_vector(self, tensor: torch.Tensor, position: int = -1) -> torch.Tensor:
        x = self._to_metric_tensor(tensor)
        if x.ndim == 3:
            return x[0, position, :].reshape(-1)
        if x.ndim == 2:
            return x[position, :].reshape(-1)
        return x.reshape(-1)

    def _cosine(self, a: torch.Tensor, b: torch.Tensor) -> float:
        denom = torch.linalg.vector_norm(a) * torch.linalg.vector_norm(b)
        if denom.item() <= self.eps:
            return np.nan
        return float(torch.dot(a.reshape(-1), b.reshape(-1)).item() / denom.item())

    def _safe_cache_get(self, cache, key):
        try:
            return cache[key]
        except Exception:
            return None
