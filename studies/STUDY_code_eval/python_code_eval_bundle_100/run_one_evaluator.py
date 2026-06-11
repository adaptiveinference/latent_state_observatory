#!/usr/bin/env python3
"""
Example runner:
  python run_one_evaluator.py prompt_PYC080/unittest.py candidate_response.py
"""
import importlib.util
import json
import sys
from pathlib import Path

evaluator_path = Path(sys.argv[1])
response_path = Path(sys.argv[2])

spec = importlib.util.spec_from_file_location("task_eval", evaluator_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

response = response_path.read_text(encoding="utf-8")
print(json.dumps(mod.evaluate(response), indent=2))
