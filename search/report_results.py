#!/usr/bin/env python3
"""Aggregate eval results into machine-readable regression reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent.parent


def read_results(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open() as fh:
        for line in fh:
            item = json.loads(line)
            if item.get("type") != "result":
                continue
            rows.append(item["result"])
    return rows


def parse_dimensions(grade: dict) -> dict:
    if isinstance(grade.get("dimensions"), dict):
        return grade["dimensions"]
    meta = grade.get("metadata") or {}
    dims = meta.get("dimensions")
    return dims if isinstance(dims, dict) else {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a consolidated regression report from eval result directories.")
    parser.add_argument("result_dirs", nargs="+", help="Result directories (e.g. evals/results-stealth)")
    parser.add_argument("--output", default=str(ROOT / "search" / "reports" / "latest-report.json"))
    args = parser.parse_args()

    reports = []
    for result_dir in args.result_dirs:
        path = Path(result_dir)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        rows = read_results(path / "results.jsonl")
        scores = [row["grade"]["score"] for row in rows]
        report = {
            "run": path.name,
            "avg_score": mean(scores) if scores else 0.0,
            "samples": []
        }
        for row in rows:
            report["samples"].append(
                {
                    "sample_id": row["sample"].get("id"),
                    "task_name": (row["sample"].get("rubric_vars") or {}).get("task_name"),
                    "score": row["grade"]["score"],
                    "dimensions": parse_dimensions(row["grade"]),
                    "rationale": row["grade"].get("rationale", "")
                }
            )
        reports.append(report)

    reports.sort(key=lambda item: item["avg_score"], reverse=True)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (ROOT / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"runs": reports}, indent=2) + "\n")
    print(json.dumps({"runs": [r["run"] for r in reports], "output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()