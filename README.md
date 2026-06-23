# hiddenstate_labs

## Open Questions I am Curious About
### Interpretability
1. Can we interpret the internal workings of generative language models to extract a useful proxy signal for output token reliability during inference? 
2. If a reliability metric can predict the health of the generated sequence early enough in the pipeline, can we use it to optimize the model architecture and reduce token costs?

[Interpretability Code](resource_aware_inference/README.md)

### Learnability
1. Can we mathematically quantify the quality of datasets used for training frontier models using first principles?
2. Tech note: https://subhadeep1978.github.io/notes/learnability/learnability.pdf 

[Learnability Code](learnability/README.md)



### Research notes, tooling, and experiments focused on:

- Autoregressive inference diagnostics
- Hidden-state observability
- Runtime telemetry for LLM inference
- Adaptive inference and compute-aware serving
- Information-theoretic evaluation of model behavior

This repository contains clean-room research artifacts, synthetic experiments, visualizations, and exploratory tooling related to inference-time behavior in large language models and other stochastic systems.

## Areas of Interest

- Hidden-state probing
- Decoding-time telemetry
- Adaptive inference policies
- KV cache behavior
- Runtime observability
- Learnability and model efficiency
- Simulation-backed evaluation

## Status

Active exploratory research repository.