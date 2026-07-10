# Runtime Quality Telemetry and Adaptive Inference Control

## Overview

This project explores runtime quality telemetry for autoregressive large language model (LLM) inference using internal hidden-state analysis, prompt-conditioned divergence metrics, and autoregressive decoding traces.

The goal is to investigate whether internal model dynamics can serve as online indicators of:

* prompt grounding,
* prior-dominant continuation,
* semantic drift,
* hallucination onset,
* and marginal utility of ongoing inference.

The broader motivation is adaptive inference serving:

* dynamically trading off quality, latency, compute cost, and resource utilization during decoding.

---

## Core Idea

At each autoregressive decode step:

```text
  y_t ~ p(y_t | x, y<t )
```
the framework runs two inference paths:

### 1. Prompt-conditioned inference

Normal inference using:

* prompt (x)
* generated history (y < t)
```text
p(y(t) | y<t, x)
```
### 2. Prior-only inference

A shadow inference pass using only generated history:
```text
  p(y(t) | y<t)
```
This approximates a "self-sustaining" continuation where the model ignores the original prompt.
The difference between these distributions provides a proxy for:
* prompt influence,
* grounding strength,
* and autoregressive degeneration.

---

## Current Diagnostics

### Pointwise Mutual Information (PMI)

Per-token answerability / prompt contribution estimate:
```text
r_t = log [ p(y(t) | x , y<t) ÷ p( y(t) | y<t) ]
```

Rolling statistics are tracked online:

* rolling mean,
* rolling variance,
* cumulative prompt influence.

---

### Hidden-State Layer Analysis

For every hidden layer:

* hidden states are intercepted,
* projected into vocabulary space,
* and compared between prompted vs prior-only inference.

Current metrics:

* cosine similarity,
* Jensen-Shannon divergence.

This produces a temporal layer-by-layer heatmap of:

* prompt-conditioned behavior,
* vs self-sustaining autoregressive continuation.

---

## Current Hypothesis

Preliminary experiments suggest:

* grounded responses exhibit more stable prompt-conditioned dynamics,
* while semantically unstable or hallucinated continuations exhibit:

  * increased PMI variance,
  * abrupt prompt-influence collapse,
  * and stronger convergence toward prior-only continuation.

The framework currently investigates:

* temporal prompt influence,
* layer-wise grounding propagation,
* and degradation onset during generation.

---

## Long-Term Direction

The intended long-term direction is not merely hallucination detection.

The broader goal is:

### Runtime Quality Telemetry

Treat internal model-state dynamics as online telemetry signals for inference systems.

Potential applications:

* adaptive early stopping,
* verifier escalation,
* retrieval triggering,
* dynamic routing,
* compute-aware decoding,
* and resource-aware inference control.

---

## Proposed Serving Architecture

### Offline calibration

Train lightweight sidecar probes using:

* hidden states,
* divergence metrics,
* benchmark datasets,
* and runtime traces.

Potential datasets:

* TruthfulQA
* HaluEval
* adversarial grounding benchmarks

### Online deployment

Use lightweight probes during decoding to estimate:

* grounding quality,
* degeneration risk,
* marginal utility of continued generation.

Combine quality telemetry with system telemetry:

* KV-cache pressure,
* latency constraints,
* queue depth,
* GPU utilization,
* memory bandwidth pressure.

The serving controller can then dynamically choose actions such as:

* continue generation,
* early terminate,
* invoke retrieval,
* trigger verifier models,
* route to stronger models,
* or reduce decode budget.

---

## Current Implementation

Implemented:

* paired prompted/prior-only inference
* hidden-state extraction
* vocabulary-space projections
* Jensen-Shannon divergence heatmaps
* rolling PMI statistics
* PDF report generation
* layer telemetry visualization

Experimental:

* prompt influence heatmaps
* grounding variance analysis
* layer-wise degeneration tracking

Planned:

* lightweight runtime probes
* decode-time forecasting
* adaptive serving controller
* resource-aware inference policies

---

## Important Caveats

This is an active exploratory research project.

The current implementation:

* does not claim reliable hallucination detection,
* does not establish causal interpretability,
* and has not yet been validated across large-scale benchmarks or production serving environments.

The framework is intended as an investigation into:

* runtime model telemetry,
* adaptive inference control,
* and online quality estimation for autoregressive systems.

## Folder layout

```text
resource_aware_inference/
  pyproject.toml
  requirements.txt
  mech_interp_base.py
  util.py
```

## Install from this folder

```bash
cd resource_aware_inference
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to Run
The tests are located in a separate folder at the root

```bash
cd studies/STUDY_prompt_influence
usage: run.py [-h] [--model MODEL] [--prompt_csv PROMPT_CSV] [--device DEVICE] [--max_output_tokens MAX_OUTPUT_TOKENS]

optional arguments:
  -h, --help            show this help message and exit
  --model MODEL         Open source LLM. Eg (mistralai/Mistral-7B-Instruct-v0.3)
  --prompt_csv PROMPT_CSV
                        CSV file containing prompts. Schema: 'prompt': str, 'hallucinated':str (yes/no)
  --device DEVICE       Device to run on: mps or cpu
  --max_output_tokens MAX_OUTPUT_TOKENS
                        Each prompt generates upto these many tokens
```


## Included model configs

- `Qwen/Qwen2.5-1.5B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`

## Output

Each run writes a JSON record containing emitted tokens, emitted-token probabilities/logprobs, next-token entropy, top-1/top-2 margin, sequence-level summary metrics, wall-clock latency, and tokens/sec.


# TransformerLens API Quick Reference

A compact reference for using TransformerLens as the hidden-state / intervention layer in mechanistic-interpretability experiments.

Canonical sources:

- Main docs: https://transformerlensorg.github.io/TransformerLens/
- GitHub: https://github.com/TransformerLensOrg/TransformerLens
- Main demo / Neel Nanda tutorial: https://transformerlensorg.github.io/TransformerLens/generated/demos/Main_Demo.html
- Intro post: https://www.lesswrong.com/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines

---

## Install

```bash
pip install transformer-lens
```

Older Python versions may need version pinning. Check the official GitHub README for current compatibility.

---

## Core import

```python
import torch
from transformer_lens import HookedTransformer
```

---

## Load a model

```python
model = HookedTransformer.from_pretrained(
    "gpt2-small",
    device="cuda",        # or "mps" / "cpu"
    dtype=torch.float16,
)
model.eval()
```

For experiments where you want residual streams close to the unfactored model computation, use conservative loading flags:

```python
model = HookedTransformer.from_pretrained(
    "gpt2-small",
    device="cuda",
    dtype=torch.float16,
    fold_ln=False,
    center_writing_weights=False,
    center_unembed=False,
)
```

Notes:

- `fold_ln=True` can be convenient for some analysis, but it rewrites parts of the computation algebraically.
- `center_writing_weights` and `center_unembed` can simplify some interpretability math, but may make direct comparison with raw HuggingFace internals less literal.

---

## Tokenization helpers

```python
prompt = "The Eiffel Tower is in"

tokens = model.to_tokens(prompt)       # Tensor: [batch, pos]
text = model.to_string(tokens[0])      # Decode tokens to string
ids = tokens[0].tolist()               # Python token IDs
```

Using the underlying tokenizer directly:

```python
tokenizer = model.tokenizer
text = tokenizer.decode([token_id])
```

---

## Basic forward pass

```python
logits = model(tokens)                 # [batch, pos, d_vocab]
next_logits = logits[:, -1, :]         # next-token logits
next_token = next_logits.argmax(dim=-1)
```

For probabilities:

```python
logprobs = torch.log_softmax(next_logits, dim=-1)
probs = torch.softmax(next_logits, dim=-1)
```

---

## `run_with_cache`: get activations

```python
logits, cache = model.run_with_cache(tokens)
```

This returns:

- `logits`: normal model output, `[batch, pos, d_vocab]`
- `cache`: `ActivationCache`, containing named activations from the forward pass

Common residual-stream entries:

```python
resid_pre_5  = cache[("resid_pre", 5)]   # before block 5
resid_mid_5  = cache[("resid_mid", 5)]   # after attention, before MLP
resid_post_5 = cache[("resid_post", 5)]  # after block 5
embed        = cache["hook_embed"]       # token embedding contribution
pos_embed    = cache["hook_pos_embed"]   # positional embedding contribution, when present
```

Latest-token residual:

```python
resid_latest = cache[("resid_post", 5)][:, -1, :]  # [batch, d_model]
```

---

## Cache only selected activations

Caching everything can be expensive. Use `names_filter`.

```python
def names_filter(name: str) -> bool:
    return name == "hook_embed" or name.endswith("hook_resid_post")

logits, cache = model.run_with_cache(
    tokens,
    names_filter=names_filter,
    remove_batch_dim=False,
)
```

This is the right pattern for your telemetry work if all you need is the residual stream per layer.

---

## Logit lens from an intermediate residual

The logit lens maps an intermediate residual vector into vocabulary space.

```python
resid = cache[("resid_post", layer)][:, -1, :]   # [batch, d_model]

h_normed = model.ln_final(resid.unsqueeze(1))    # [batch, 1, d_model]
logits = model.unembed(h_normed)[:, -1, :]       # [batch, d_vocab]
probs = torch.softmax(logits, dim=-1)
```

This replaces the raw HuggingFace pattern:

```python
h_normed = model.model.norm(h)
logits = model.lm_head(h_normed)
```

---

## Common activation names

TransformerLens exposes activation names through hook points.

For block `L`, common names include:

```python
cache[("resid_pre", L)]
cache[("resid_mid", L)]
cache[("resid_post", L)]
cache[("attn_out", L)]
cache[("mlp_out", L)]
cache[("pattern", L)]
cache[("q", L)]
cache[("k", L)]
cache[("v", L)]
cache[("z", L)]
```

Exact availability can depend on model architecture and cache settings.

To inspect names:

```python
logits, cache = model.run_with_cache(tokens)
print(cache.keys())
```

---

## Attention patterns

```python
pattern = cache[("pattern", layer)]
```

Typical shape:

```text
[batch, n_heads, dest_pos, src_pos]
```

Example:

```python
head_pattern = pattern[0, head_idx]
```

---

## Hooks: intervene during forward pass

A hook function receives `(activation, hook)` and returns the modified activation.

```python
def zero_activation(act, hook):
    return torch.zeros_like(act)

logits = model.run_with_hooks(
    tokens,
    fwd_hooks=[
        ("blocks.5.hook_resid_post", zero_activation),
    ],
)
```

Zero one attention head output:

```python
def zero_head_z(z, hook):
    # z shape often: [batch, pos, n_heads, d_head]
    z[:, :, 3, :] = 0.0
    return z

logits = model.run_with_hooks(
    tokens,
    fwd_hooks=[
        ("blocks.6.attn.hook_z", zero_head_z),
    ],
)
```

---

## Activation patching pattern

Basic idea:

1. Run clean prompt, cache activations.
2. Run corrupted prompt.
3. During corrupted run, replace one activation with the clean activation.
4. Measure recovery in logits / probability / task score.

Skeleton:

```python
clean_logits, clean_cache = model.run_with_cache(clean_tokens)

hook_name = "blocks.5.hook_resid_post"

def patch_from_clean(corrupt_act, hook):
    return clean_cache[hook_name]

patched_logits = model.run_with_hooks(
    corrupt_tokens,
    fwd_hooks=[(hook_name, patch_from_clean)],
)
```

---

## Residual stream decomposition

TransformerLens can decompose accumulated residual stream contributions.

Useful cache helpers often include methods such as:

```python
cache.accumulated_resid(...)
cache.decompose_resid(...)
cache.stack_head_results(...)
cache.apply_ln_to_stack(...)
```

The exact signatures have changed across versions, so check the generated API docs for your installed version.

Conceptually:

- `accumulated_resid` gives residual stream after each layer.
- `decompose_resid` splits contributions by embedding / attention / MLP components.
- `stack_head_results` separates attention-head contributions.
- `apply_ln_to_stack` normalizes residual stacks before unembedding.

---

## Direct logit attribution

A common pattern:

```python
answer_token = model.to_single_token(" Paris")
logit_dir = model.W_U[:, answer_token]    # [d_model]
```

Then dot residual-like vectors against `logit_dir`:

```python
score = residual @ logit_dir
```

For contrastive attribution between correct and incorrect tokens:

```python
correct = model.to_single_token(" Paris")
wrong = model.to_single_token(" London")
logit_diff_dir = model.W_U[:, correct] - model.W_U[:, wrong]
score = residual @ logit_diff_dir
```

---

## Generation

TransformerLens has generation helpers, but for telemetry you usually want manual token-by-token stepping.

Simple generation:

```python
out = model.generate("The capital of France is", max_new_tokens=20)
```

Manual deterministic next-token step:

```python
logits = model(tokens)
next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
tokens = torch.cat([tokens, next_token], dim=-1)
```

Manual sampling:

```python
temperature = 0.7
logits = model(tokens)[:, -1, :]
probs = torch.softmax(logits / temperature, dim=-1)
next_token = torch.multinomial(probs, num_samples=1)
tokens = torch.cat([tokens, next_token], dim=-1)
```

---


## Practical caveats

1. **Model support varies.** GPT-2-like models are the easiest. Llama/Gemma/Mistral-style models may work, but always verify activations and logits against a known baseline.

2. **LayerNorm folding changes interpretation.** Good for some analyses, less ideal if you want literal comparison with raw model internals.

3. **Tokenization matters.** Always use the same tokenizer path for full and promptless runs.

4. **Caching is memory-heavy.** Use `names_filter` aggressively for long prompts and generation traces.

5. **Compare one known prompt first.** Before trusting a port, run your old HuggingFace version and the TransformerLens version on a tiny model and verify next-token logits/top-k tokens are close enough for your purpose.

---

## Minimal sanity check

```python
import torch
from transformer_lens import HookedTransformer

model = HookedTransformer.from_pretrained(
    "gpt2-small",
    device="cuda" if torch.cuda.is_available() else "cpu",
    fold_ln=False,
    center_writing_weights=False,
    center_unembed=False,
)
model.eval()

tokens = model.to_tokens("The Eiffel Tower is in")
logits, cache = model.run_with_cache(
    tokens,
    names_filter=lambda name: name == "hook_embed" or name.endswith("hook_resid_post"),
)

print(logits.shape)
print(cache[("resid_post", 0)].shape)

next_token = logits[:, -1, :].argmax(dim=-1)
print(model.tokenizer.decode(next_token.tolist()))
```
