import torch
import torch.nn.functional as F
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import textwrap
import pandas as pd
import utils

# TransformerLens replaces the manual HuggingFace hidden-state plumbing.
# Install with:
#     pip install transformer-lens
from transformer_lens import HookedTransformer

#########################################################################
# Deep layer inspection for LLM
#########################################################################
class InferenceHealthTracker:
    def __init__(
        self,
        model_name: str,
        device: str = "mps",
        dtype=torch.float32,
        prior_window: int = 128,
        fold_ln: bool = False,
        center_writing_weights: bool = False,
        center_unembed: bool = False,
        internal_prober: utils.InternalProber = None,
        enable_internal_probe: bool = True,
    ):
        self.device = device
        self.prior_window = prior_window

        # Maintain a rolling window of these many past tokens
        self.rolling_stat_window = 50
        self.pmi_stats = utils.RollingStats(self.rolling_stat_window)

        # TransformerLens model. The center/fold flags are set conservatively so
        # cached residuals remain close to the unfactored model computation.
        self.model = HookedTransformer.from_pretrained(
            model_name,
            device=device,
            dtype=dtype,
            fold_ln=fold_ln,
            center_writing_weights=center_writing_weights,
            center_unembed=center_unembed,
        )
        self.model.eval()
        self.tokenizer = self.model.tokenizer

        self.internal_prober = internal_prober
        if self.internal_prober is None and enable_internal_probe:
            self.internal_prober = utils.InternalProber(self.model)

        self.reset()

    def reset(self):
        self.full_input_ids = None          # [prompt + generated]
        self.generated_ids = []             # generated y_1 ... y_t


    @torch.no_grad()
    def format_prompt_for_model(self, tokenizer, prompt):
        if hasattr(tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": prompt}]
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            return prompt

    @torch.no_grad()
    def start_prompt(self, prompt: str):
        self.reset()
        text                        = self.format_prompt_for_model(self.tokenizer, prompt)
        self.full_input_ids         = self.model.to_tokens(text).to(self.device)
        self.original_prompt_tokens = self.full_input_ids

    def _cache_names_filter(self, name: str) -> bool:
        """
        Cache the residual-stream tensors needed for the legacy logit-lens layer
        abstraction, plus optional internal telemetry requested by InternalProber.
        """
        if self.internal_prober is not None:
            return self.internal_prober.cache_names_filter(name)
        return name == "hook_embed" or name.endswith("hook_resid_post")

    @torch.no_grad()
    def _logit_lens_distribution_from_residual(self, residual: torch.Tensor):
        """
        residual: [batch, d_model] at the latest token position.

        Applies the model's final normalization and unembedding to turn an
        intermediate residual stream vector into a vocab distribution. This is
        the TransformerLens replacement for:

            h_normed = self.model.model.norm(h)
            logits   = self.model.lm_head(h_normed)
            prob     = softmax(logits)
        """
        residual_3d = residual.unsqueeze(1)             # [batch, 1, d_model]
        h_normed = self.model.ln_final(residual_3d)     # [batch, 1, d_model]
        logits = self.model.unembed(h_normed)[:, -1, :] # [batch, d_vocab]
        prob = F.softmax(logits, dim=-1)
        return h_normed[:, -1, :], prob

    @torch.no_grad()
    def _next_token_distribution(self, input_ids, collect_internal_states = True):
        """
        Surgical TransformerLens swap-in for your old HuggingFace hidden-state
        extraction path.

        Returns:
            logprobs: [batch, d_vocab] final next-token log-probabilities
            hidden_layer_info: list[utils.HiddenState]
                layer 0        = embedding residual stream at latest token
                layer 1..L     = post-transformer-block residual streams
            internal_probe: dict of z_{p,t,l}-style telemetry collected from cache
        """
        logits, cache = self.model.run_with_cache(
            input_ids,
            names_filter=self._cache_names_filter,
            remove_batch_dim=False,
        )

        # Output logits -> predictive distribution for next token.
        logits = logits[:, -1, :]
        logprobs = F.log_softmax(logits, dim=-1)

        hidden_layer_info = []

        # Layer 0: embedding residual. This preserves the old convention where
        # outputs.hidden_states included an initial embedding state.
        embed_resid = cache["hook_embed"][:, -1, :]
        h_normed, prob = self._logit_lens_distribution_from_residual(embed_resid)
        hidden_layer_info.append(
            utils.HiddenState(
                layer_idx=0,
                layer_output_raw=h_normed,
                layer_output_prob=prob,
            )
        )

        # Layers 1..n_layers: post-block residual streams.
        for layer in range(self.model.cfg.n_layers):
            resid_post = cache[("resid_post", layer)][:, -1, :]
            h_normed, prob = self._logit_lens_distribution_from_residual(resid_post)
            hidden_layer_info.append(
                utils.HiddenState(
                    layer_idx=layer + 1,
                    layer_output_raw=h_normed,
                    layer_output_prob=prob,
                )
            )

        internal_probe = None
        if self.internal_prober is not None and collect_internal_states:
            internal_probe = self.internal_prober.collect(cache, position=-1)

        return logprobs, hidden_layer_info, internal_probe

    # =================================================================================================
    # Analyze layers
    # H_full : vector of layer information during the full inference pass - one entry per layer
    # H_prior: vector of layer information during the prior-only inference pass - one entry per layer
    # For each layer compare the real inference output, and the prior-only version using:
    #       - Cosine similarity (directional alignment)
    #       - Jensen-Shannon divergence of the projected distributions. (entropy alignment)
    # =================================================================================================
    @torch.no_grad()
    def analyze_layers(self, H_full, H_prior):
        return utils.analyze_layers(H_full, H_prior, d_vocab=self.model.cfg.d_vocab)

    # =======================================================================
    # Run the actual inference.
    # Generate next token.
    # Return next token, and full predictive distribution (log of it)
    # =======================================================================
    @torch.no_grad()
    def run_true_inference(self, input, temperature):
        full_logprobs, hidden_layer_info, internal_probe = self._next_token_distribution(self.full_input_ids, collect_internal_states=True)

        if temperature == 0.0:
            next_token_id = torch.argmax(full_logprobs, dim=-1, keepdim=True)
        else:
            probs = torch.softmax(full_logprobs / temperature, dim=-1)
            next_token_id = torch.multinomial(probs, num_samples=1)

        token_id = next_token_id.item()
        logp_full = full_logprobs[0, token_id].item()
        return logp_full, next_token_id, hidden_layer_info, internal_probe

    # ==================================================================================================
    # Run the shadow inference.
    # This deletes the prompt and runs the model in fully autoregressive mode.
    # This represents the case when the model ignores the user prompt and hallucinates its own output.
    # ==================================================================================================
    @torch.no_grad()
    def run_promptless_inference(self, token_id):
        if len(self.generated_ids) == 0:
            logp_prior = None
            hidden_layer_info = None
        else:
            prior_context_ids = self.generated_ids[-self.prior_window:]
            prior_input_ids = torch.tensor(
                [prior_context_ids],
                dtype=torch.long,
                device=self.device,
            )
            prior_logprobs, hidden_layer_info, _ = self._next_token_distribution(prior_input_ids, collect_internal_states = False)
            logp_prior = prior_logprobs[0, token_id].item()
        return logp_prior, hidden_layer_info

    # =======================================================================
    # Generates one token from the full prompted model, computes the shadow-prior
    # probability of that same token, and updates the answerability estimate.
    # =======================================================================
    @torch.no_grad()
    def step(self, temperature: float = 0.0):

        # 1. Generate next token
        logp_full, token_id, H_full, internal_probe = self.run_true_inference(self.full_input_ids, temperature)

        # 2. Run a shadow-pass to extract the promp-less distribution
        logp_prior, H_prior = self.run_promptless_inference(token_id.item())

        # 3. Analysis for current step: 
        # 3.1 Answerability
        #    MI(y1..yt | x) = H(y1...yt) - H(y1...yt | x)
        #   NMI(y1..yt | x) = 1.0 - H(y1...yt | x) / H(y1...yt)
        #                   = 1.0 - E( -log(p(y1..yt)) ) / E( -log(p(y1..yt | x)) )
        #   Pointwise formulation
        #    PMI(y1..yt | x)= -log(p(y1..yt)) ) - ( -log(p(y1..yt | x)) )
        #                   = log(p(y1..yt | x) ) - log(p(y1..yt)
        r_t = logp_full - logp_prior if logp_prior is not None else 0

        # 3.2   Per-layer stats
        layerstats = self.analyze_layers(H_full, H_prior)

        # 4. Update generated sequence
        self.generated_ids.append(token_id.item())
        self.full_input_ids = torch.cat(
            [self.full_input_ids, token_id],
            dim=-1,
        )

        # 5. Update running answerability stats
        self.pmi_stats.update_moving_stats(r_t)

        return {
            "token_id"      : token_id.item(),
            "token_text"    : self.tokenizer.decode([token_id.item()]),
            "logp_full"     : logp_full,
            "logp_prior"    : logp_prior,
            "r_t"           : r_t,
            "pmi_mean"      : self.pmi_stats.rolling_mean,
            "pmi_var"       : self.pmi_stats.rolling_var,
            "layerstats"    : layerstats,
            "internal_probe" : internal_probe,
        }

    def generated_text(self):
        return self.tokenizer.decode(self.generated_ids, skip_special_tokens=True)

    @torch.no_grad()
    def generate(self, prompt: str, max_new_tokens: int = 64, temperature: float = 0.0):
        self.start_prompt(prompt)

        trace = []
        # Each step does the following:
        # 1) A full inference pass to generate the next token.
        # 2) A shadow pass with deleted prior (ablation pass)
        # 3) Collect stats at the final logit layer.
        # 4) Collect stats at each hidden layer.
        for _ in range(max_new_tokens):
            info = self.step(temperature=temperature)
            trace.append(info)

            if info["token_id"] == self.tokenizer.eos_token_id:
                break
        return {
            "text"             : self.generated_text(),
            "trace"            : trace,
            "prompt"           : prompt,
        }



# =====================================================
# Plot
# =====================================================
def plotHeatmap(df, ax):
    # 1. Define custom colormap: 0.0 = deep red, 1.0 = yellow
    colors = ["#8B0000", "#FFFF00"] 
    custom_cmap = LinearSegmentedColormap.from_list("DeepRedYellow", colors)

    # 2. Transpose the DataFrame to put original rows on the X-axis
    data = df.T.values 

    # 3. Create heatmap with imshow
    im = ax.imshow(data, cmap=custom_cmap, vmin=0.0, vmax=1.0, aspect='auto')

    return im


def plotPmi(results, pdf):
    """
    Creates a multi-page PDF.

    Each page contains:
      1. Probability / answerability curves
      2. Nicely formatted generated response text
    """
    for idx, result in enumerate(results):
        prompt = result["prompt"]
        response_text = result["text"]
        trace = result["trace"]
        steps = np.arange(len(trace))

        logp_full = np.array([row["logp_full"] for row in trace], dtype=float)
        logp_prior = np.array([
            np.nan if row["logp_prior"] is None else row["logp_prior"]
            for row in trace
        ], dtype=float)
        ema_answerability = np.array([row["pmi_mean"] for row in trace], dtype=float)

        scale = 1.5
        fig = plt.figure(figsize=(11 * scale, 8.5 * scale))
        gs = fig.add_gridspec(
            4,
            2,
            height_ratios=[1.0, 1.0, 1.0, 1.0],
            width_ratios=[2.5, 1.0],
            hspace=0.25,
            wspace=0.20,
        )

        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(steps, logp_full, linewidth=2, label="logp_full")
        ax1.plot(steps, logp_prior, linewidth=2, label="logp_prior")
        ax1.set_ylabel("Log probability")
        ax1.grid(True)
        ax2 = ax1.twinx()
        ax2.plot(steps, ema_answerability, linestyle="--", linewidth=2, label="")
        ax2.set_ylabel("Final prompt influence")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

        ax_layer = fig.add_subplot(gs[1, 0])
        im = plotHeatmap(result["DJS"], ax_layer)
        divider = make_axes_locatable(ax_layer)
        cax = divider.append_axes("right", size="2%", pad=0.1)
        fig.colorbar(im, cax=cax)
        ax_layer.set_ylabel("Hidden layer index")
        ax_layer.set_title("Prompt influence on generated tokens")

        ax_layer = fig.add_subplot(gs[2, 0])
        im = plotHeatmap(result["layer_entropy"], ax_layer)
        divider = make_axes_locatable(ax_layer)
        cax = divider.append_axes("right", size="2%", pad=0.1)
        fig.colorbar(im, cax=cax)
        ax_layer.set_xlabel("Generation step")
        ax_layer.set_ylabel("Hidden layer index")
        ax_layer.set_title("Layer entropy: Primary inference stream")

        ax_text = fig.add_subplot(gs[:, 1])
        ax_text.axis("off")
        wrapped_prompt = textwrap.fill(prompt, width=110)
        wrapped_response = textwrap.fill(response_text, width=110)
        text_block = (
            "PROMPT:\n"
            f"{wrapped_prompt}\n\n"
            "MODEL RESPONSE:\n"
            f"{wrapped_response}"
        )
        ax_text.text(
            0.01,
            0.99,
            text_block,
            fontsize=9,
            va="top",
            ha="left",
            family="monospace",
            wrap=True,
        )

        fig.suptitle(f"Prompt {idx + 1}", fontsize=14, y=0.98)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig)
        plt.close(fig)

        # # =====================================================
        # # Cross correlation between DJS and layer Entropy
        # # =====================================================
        # f       = plt.figure(figsize=(11, 8.5))
        # nLayers = result["DJS"].shape[1]
        # layers_to_plot = [0, int(nLayers/2) , nLayers-1]
        # nLayersToPlot  = len(layers_to_plot)

        # for idx,layer in enumerate(layers_to_plot):
        #     djs = result["DJS"][layer]
        #     e   = result["layer_entropy"][layer]
        #     xcorr, lags = utils.crossCorrelation(djs, e)
            
        #     ax= f.add_subplot(nLayersToPlot, 1 , idx+1)
        #     ax.plot(lags, np.absolute(xcorr)**2, marker="o" )
        #     ax.grid(True)
        #     ax.set_ylim(bottom=0, top=1.0)
        #     ax.set_ylabel(f"Layer {layer}")

        #     if idx == 0:
        #         ax.set_title(rf"$|CrossCorrelation(DJS, Entropy)|^2$ ")
        #     if idx == (nLayersToPlot-1):
        #         ax.set_xlabel("Token lag")
        # f.tight_layout(rect=[0, 0, 1, 0.96])
        # pdf.savefig(f)            
        # plt.close(f)


