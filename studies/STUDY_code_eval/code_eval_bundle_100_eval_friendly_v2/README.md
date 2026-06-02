# Code Eval Bundle 100 — Eval-Friendly v2

This version keeps the original 100 unit-test harnesses but rewrites `prompts.csv` to be more model-friendly.

Main change:
- Removed numbered "Response rules" lists.
- Replaced them with a short scaffold-style prompt.
- The model is told to start with the check-token line and then output code.

Files:
- `prompts.csv`: task_id, task_description, prompt, check_token, required_symbol, unit_test_code, evaluator_path
- `prompt_<task_id>/unittest.py`: importable evaluator exposing `evaluate(response)`
- `run_one_evaluator.py`: evaluate one response
- `run_batch_evaluators.py`: evaluate a directory of responses
- `PROMPT_TEMPLATE.md`: prompt template

Evaluator result values:
- PASS
- FORMAT_FAIL
- SYNTAX_FAIL
- RUNTIME_FAIL
- TEST_FAIL
- MISSING_RESPONSE, from the batch runner only

Security note:
The evaluators execute model-generated Python code. Run in a sandbox.
