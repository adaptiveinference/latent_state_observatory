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
  p(y(t) | y<t, x)
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
  configs/
  docs/
  scripts/
  src/modelrunner/
```

## Install from this folder

```bash
cd resource_aware_inference
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Run

```bash
modelrunner \
  --config configs/qwen_1p5b.yaml \
  --prompt "What is 2+2?" \
  --out runs/smoke.json
```

Or:

```bash
./scripts/run_smoke.sh
```

## Included model configs

- `Qwen/Qwen2.5-1.5B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`

## Output

Each run writes a JSON record containing emitted tokens, emitted-token probabilities/logprobs, next-token entropy, top-1/top-2 margin, sequence-level summary metrics, wall-clock latency, and tokens/sec.


