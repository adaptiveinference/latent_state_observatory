# Eval-Friendly Prompt Template

The prompt intentionally avoids numbered rule lists because smaller chat models may continue the list
instead of answering with code.

Template:

Task ID: {task_id}

Return ONLY valid Python code.
Do not use Markdown fences. Do not include prose, explanations, examples, print statements, or tests.

Your code must contain this exact check-token line:
# CHECK_TOKEN: {task_id}

Your code must contain this required symbol:
{required_symbol}

Implement this task:
{task_description}.

Start your answer with the check-token line, then provide the Python implementation.
