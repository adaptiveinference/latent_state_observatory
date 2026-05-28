import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import textwrap
from dataclasses import dataclass, asdict
from scipy.spatial import distance
import scipy.stats as sps
from collections import deque
import pandas as pd
import utils
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
        self.rolling_var  = None

    def update_moving_stats(self, r_t):
        # If the window is full, remove the oldest value from the sums
        if len(self.window) == self.W:
            old_val = self.window[0] # deque handles the pop internally via maxlen
            self.sum -= old_val
            self.sum_sq -= old_val**2
            
        # Add new value
        self.window.append(r_t)
        self.sum += r_t
        self.sum_sq += r_t**2
        
        n = len(self.window)
        mean = self.sum / n
        
        # Population variance: E[X^2] - (E[X])^2
        variance = (self.sum_sq / n) - (mean**2)
        
        # Use max(0, ...) to catch tiny negative results from float precision errors
        self.rolling_mean = mean
        self.rolling_var  = max(0.0, variance)

#########################################################################
# LLM internal breadcrumbs
#########################################################################
@dataclass
class HiddenState:
    layer_idx           : int                # Hidden layer index
    layer_output_raw    : torch.Tensor       # Output tensor for layer
    layer_output_prob   : torch.Tensor       # Output tensor projected onto vocabuluary space


@dataclass
class LayerStats:
    layer_idx            : int                # Hidden layer index
    cosine_sim           : float              # Cosine similary between the tensor for true inference vs prior-only inference
    D_js                 : float              # Jensen Shannon divergence between the tensor for true inference vs prior-only inference
    layer_entropy        : float              # Entropy of the projected vocabulary distribution for the layer.


#########################################################################
# Deep layer inspection for LLM
#########################################################################
class InferenceHealthTracker:
    def __init__(
        self,
        model_name: str,
        device: str = "mps",
        dtype=torch.float16,
        prior_window: int = 128,
    ):
        self.device = device
        self.prior_window = prior_window

        # Maintain a rolling window of these many past tokens
        self.rolling_stat_window = 50       # Maintain a rolling window of these many past tokens
        self.pmi_stats = RollingStats(self.rolling_stat_window)

        # The model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device,
        )
        self.model.eval()

        self.reset()

    def reset(self):
        self.full_input_ids = None          # [prompt + generated]
        self.generated_ids = []             # generated y_1 ... y_t

    @torch.no_grad()
    def start_prompt(self, prompt: str):
        self.reset()
        encoded = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        self.full_input_ids = encoded["input_ids"]
        self.original_prompt_tokens = self.full_input_ids

    @torch.no_grad()
    def _next_token_distribution(self, input_ids):
        outputs = self.model(
            input_ids=input_ids, 
            output_hidden_states=True,    
        )

        # Output logits -> Predictive distribution
        logits = outputs.logits[:, -1, :]
        logprobs = F.log_softmax(logits, dim=-1)

        # Return hidden state tensor for each layer.
        # The model dumps an ever increasing tensor containing all past history, at EACH step.
        # We only need the latest at each step
        hidden_layer_info = []
        for idx, hidden_state in enumerate(outputs.hidden_states):
            h        = hidden_state[:, -1, :]
            h_normed = self.model.model.norm(h)
            logits   = self.model.lm_head(h_normed)
            prob     = F.softmax(logits, dim=-1)
            hidden_layer_info.append( 
                                        HiddenState(
                                            layer_idx         = idx,
                                            layer_output_raw  = h_normed,
                                            layer_output_prob = prob,
                                        )
                                    )            

        return logprobs, hidden_layer_info


    # =================================================================================================
    # Analyze layers
    # H_full : vector of layer information during the full inference pass - one entry per layer
    # H_prior: vector of layer information during the prior-only inference pass - one entry per layer
    # For each layer compare the real inference output, and the prior-only version using:
    #       - Cosine similary (directional alignment)
    #       - Jensen-shannon divergence of the projected distributions. (entropy alignment)
    # =================================================================================================
    @torch.no_grad()
    def analyze_layers(self, H_full, H_prior):
        if not H_full : return None 
        if not H_prior: return None
        assert len(H_full) == len(H_prior), f"Mismatched layer counts between true and prior-only inference len(H_full):{len(H_full)} != len(H_prior):{len(H_prior)} "

        layerstats = []
        for l, (h_full, h_prior)  in enumerate(zip(H_full, H_prior)):
            a, b = h_full.layer_output_raw.detach().cpu().double().numpy().reshape(-1)   , h_prior.layer_output_raw.detach().cpu().double().numpy().reshape(-1)

            # Cosine similarity
            cosine_sim = np.dot(a, b) / ( np.linalg.norm(a) * np.linalg.norm(b) )
            # print(f"Layer {l}")
            # print(f"    cosine_sim : {cosine_sim}")
            # print(f"    h_full     : {a},    norm2 = {np.linalg.norm(a, ord=2)}")
            # print(f"    h_prior    : {b},    norm2 = {np.linalg.norm(b, ord=2)}")

            # Jenken-Shannon divergence
            a, b = h_full.layer_output_prob.detach().cpu().double().numpy().reshape(-1)  , h_prior.layer_output_prob.detach().cpu().double().numpy().reshape(-1)
            js_divergence = distance.jensenshannon(a,b )**2
            # print(f"    JSD    : {js_divergence}")
            # print(f"    p_full : {a}")
            # print(f"    p_prior: {b}")

            # Entropy of the vocabulary distribution (normalized between 0 and 1.0)
            max_entropy   = np.log2( len(self.tokenizer) )
            layer_entropy = sps.entropy(a, base=2) / max_entropy

            layerstats.append(
                LayerStats(
                    layer_idx     = l,
                    cosine_sim    = cosine_sim,
                    D_js          = js_divergence,
                    layer_entropy = layer_entropy,
                )
            )
        return layerstats


    # =======================================================================
    # Run the actual inference.
    # Generate next token. 
    # Return next token, and full predictive distribution (log of it)
    # =======================================================================
    @torch.no_grad()
    def run_true_inference(self, input, temperature):
        # 1. Full prompted distribution: p(y_t | x, y_<t)
        full_logprobs, hidden_layer_info = self._next_token_distribution(self.full_input_ids)

        if temperature == 0.0:
            next_token_id = torch.argmax(full_logprobs, dim=-1, keepdim=True)
        else:
            probs = torch.softmax(full_logprobs / temperature, dim=-1)
            next_token_id = torch.multinomial(probs, num_samples=1)

        token_id = next_token_id.item()

        # 2. Full prompted logprob of chosen token
        logp_full = full_logprobs[0, token_id].item()
        return logp_full, next_token_id, hidden_layer_info

    # ==================================================================================================
    # Run the shadow inference.
    # This deletes the prompt and runs the model in fully autoregressive mode.
    # This represents the case when the model ignores the user prompt (ie does not listen to the user)
    #  and hallucinates its own output. This serves as the reference against which we compare 
    #  the true inference pipeline
    # Return full predictive distribution (log of it) of the prior-only run
    # ==================================================================================================
    @torch.no_grad()
    def run_promptless_inference(self, token_id):
        if len(self.generated_ids) == 0:
            # First output token has no generated-history prior.
            # Use BOS/eos fallback, or skip prior contribution.
            logp_prior = None
            hidden_layer_info = None
        else:
            prior_context_ids = self.generated_ids[-self.prior_window:]
            prior_input_ids = torch.tensor(
                [prior_context_ids],
                dtype=torch.long,
                device=self.device,
            )
            prior_logprobs, hidden_layer_info = self._next_token_distribution(prior_input_ids)
            logp_prior     = prior_logprobs[0, token_id].item()        
        return logp_prior, hidden_layer_info


    # =======================================================================
    # Generates one token from the full prompted model,
    # computes the shadow-prior probability of that same token,
    # and updates the answerability estimate.
    # =======================================================================
    @torch.no_grad()
    def step(self, temperature: float = 0.0):

        # 1. Generate next token
        logp_full, token_id, H_full = self.run_true_inference(self.full_input_ids, temperature)

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


def plotPmi(results,pdf):
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

        logp_full = np.array([
            row["logp_full"]
            for row in trace
        ], dtype=float)

        logp_prior = np.array([
            np.nan if row["logp_prior"] is None
            else row["logp_prior"]
            for row in trace
        ], dtype=float)

        ema_answerability = np.array([
            row["pmi_mean"]
            for row in trace
        ], dtype=float)

        # =====================================================
        # Figure layout
        # =====================================================
        scale = 1.5
        fig = plt.figure(figsize=(11*scale, 8.5*scale))
        gs = fig.add_gridspec(
            4,
            2,
            height_ratios=[1.0, 1.0, 1.0, 1.0],
            width_ratios=[2.5, 1.0],
            hspace=0.25,
            wspace=0.20
        )

        # =====================================================
        # Top subplot: curves
        # =====================================================
        ax1 = fig.add_subplot(gs[0,0])
        ax1.plot(
            steps,
            logp_full,
            linewidth=2,
            label="logp_full",
        )
        ax1.plot(
            steps,
            logp_prior,
            linewidth=2,
            label="logp_prior",
        )
        ax1.set_ylabel("Log probability")
        ax1.grid(True)
        ax2 = ax1.twinx()
        ax2.plot(
            steps,
            ema_answerability,
            linestyle="--",
            linewidth=2,
            label="",
        )
        ax2.set_ylabel("Final prompt influence")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc="best",
        )

        # =====================================================
        # Middle subplot1: Divergence of hidden layer logits
        # =====================================================
        ax_layer = fig.add_subplot(gs[1,0])
        im       = plotHeatmap(result["DJS"], ax_layer)
        divider  = make_axes_locatable(ax_layer)
        cax      = divider.append_axes("right", size="2%", pad=0.1) 

        fig.colorbar(im, cax=cax)
        ax_layer.set_ylabel("Hidden layer index")
        ax_layer.set_title("Prompt influence on generated tokens")
        
        # =====================================================
        # Middle subplot2: Entropy of hidden layer logits
        # =====================================================
        ax_layer = fig.add_subplot(gs[2,0])
        im       = plotHeatmap(result["layer_entropy"], ax_layer)
        divider  = make_axes_locatable(ax_layer)
        cax      = divider.append_axes("right", size="2%", pad=0.1) 

        fig.colorbar(im, cax=cax)
        ax_layer.set_xlabel("Generation step")
        ax_layer.set_ylabel("Hidden layer index")
        ax_layer.set_title("Layer entropy: Primary inference stream")


        # =====================================================
        # Bottom subplot: response text
        # =====================================================
        ax_text = fig.add_subplot(gs[:,1])
        ax_text.axis("off")
        wrapped_prompt = textwrap.fill(
            prompt,
            width=110,
        )
        wrapped_response = textwrap.fill(
            response_text,
            width=110,
        )
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

        # =====================================================
        # Title
        # =====================================================
        fig.suptitle(
            f"Prompt {idx + 1}",
            fontsize=14,
            y=0.98,
        )
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


