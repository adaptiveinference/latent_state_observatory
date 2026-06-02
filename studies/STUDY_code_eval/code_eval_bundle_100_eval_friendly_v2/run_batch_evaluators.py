#!/usr/bin/env python3
"""
Batch evaluator for generated responses.

Expected layout:
  responses/
    PYC001.py
    PYC002.py
    ...

Usage:
  python run_batch_evaluators.py --responses responses --out results.csv
"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path


def load_eval(path):
    spec = importlib.util.spec_from_file_location("task_eval", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", required=True, help="Directory containing <task_id>.py or <task_id>.txt response files")
    ap.add_argument("--prompts_csv", default="prompts.csv")
    ap.add_argument("--out", default="results.csv")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    responses_dir = Path(args.responses)
    prompts_csv = root / args.prompts_csv

    rows = list(csv.DictReader(prompts_csv.open(newline="", encoding="utf-8")))
    results = []

    for row in rows:
        task_id = row["task_id"]
        evaluator_path = root / row["evaluator_path"]
        response_path = responses_dir / f"{task_id}.py"
        if not response_path.exists():
            response_path = responses_dir / f"{task_id}.txt"

        if not response_path.exists():
            result = {"result": "MISSING_RESPONSE", "result_descr": f"Missing {task_id}.py or {task_id}.txt"}
        else:
            mod = load_eval(evaluator_path)
            response = response_path.read_text(encoding="utf-8")
            result = mod.evaluate(response)

        results.append({
            "task_id": task_id,
            "complexity": row.get("complexity", ""),
            "category": row.get("category", ""),
            "result": result.get("result", ""),
            "result_descr": result.get("result_descr", ""),
        })

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "complexity", "category", "result", "result_descr"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
