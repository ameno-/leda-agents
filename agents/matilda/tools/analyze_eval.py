"""
Matilda custom tool: analyze_eval
Analyzes eval results from the harness, compares configurations, and generates reports.
"""
import json
import os
from datetime import datetime

RESULTS_FILE = "/tmp/personality-eval-harness/results/runs.jsonl"


def analyze_eval(
    results_file: str = RESULTS_FILE,
    model: str = None,
    personality: str = None,
    task: str = None,
    compare: bool = False,
    threshold: float = 0.7,
) -> dict:
    """Analyze eval results and generate report.

    Args:
        results_file: Path to runs.jsonl
        model: Filter by model handle (optional)
        personality: Filter by personality name (optional)
        task: Filter by task ID (optional)
        compare: If True, compare across all matching configs
        threshold: Score below which a dimension is flagged weak (default 0.7)

    Returns:
        Dict with summary, flagged dimensions, and recommendations
    """
    if not os.path.exists(results_file):
        return {"error": f"Results file not found: {results_file}"}

    runs = []
    with open(results_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                # Apply filters
                if model and run.get("model") != model:
                    continue
                if personality and run.get("personality") != personality:
                    continue
                if task and run.get("task") != task:
                    continue
                runs.append(run)
            except json.JSONDecodeError:
                continue

    if not runs:
        return {"error": "No matching runs found", "filters": {"model": model, "personality": personality, "task": task}}

    dimensions = ["scope_respect", "evidence_first", "execution_aware", "low_drama", "professional_tone", "answer_first"]

    if compare:
        # Group by config and compare
        configs = {}
        for run in runs:
            key = f"{run.get('model', 'unknown')}/{run.get('personality', 'unknown')}"
            if key not in configs:
                configs[key] = []
            configs[key].append(run)

        comparison = {}
        for key, config_runs in configs.items():
            avg = {}
            for dim in dimensions:
                vals = [r.get("scores", {}).get(dim, 0) for r in config_runs if "scores" in r]
                avg[dim] = round(sum(vals) / len(vals), 3) if vals else 0.0
            overall = round(sum(avg.values()) / len(avg), 3) if avg else 0.0
            comparison[key] = {"scores": avg, "overall": overall, "runs": len(config_runs)}

        # Find best config
        best_key = max(comparison, key=lambda k: comparison[k]["overall"])

        return {
            "type": "comparison",
            "configs": comparison,
            "best": best_key,
            "best_score": comparison[best_key]["overall"],
            "total_runs": len(runs),
        }

    # Single config analysis
    avg_scores = {}
    for dim in dimensions:
        vals = [r.get("scores", {}).get(dim, 0) for r in runs if "scores" in r]
        avg_scores[dim] = round(sum(vals) / len(vals), 3) if vals else 0.0

    overall = round(sum(avg_scores.values()) / len(avg_scores), 3) if avg_scores else 0.0

    # Flag weak dimensions
    weak = {dim: score for dim, score in avg_scores.items() if score < threshold}
    weakest = min(avg_scores, key=avg_scores.get) if avg_scores else None

    # Generate recommendation
    recommendation = None
    if weak:
        tuning = {
            "scope_respect": "Add: 'Do ONE task at a time. State what you are deferring.'",
            "evidence_first": "Add: 'Investigate before concluding. Read files, then act.'",
            "execution_aware": "Add: 'Verify before declaring done. Ask: what could go wrong?'",
            "low_drama": "Add: 'Be terse. No filler, no hedging, no unnecessary reassurance.'",
            "professional_tone": "Add: 'Be peer-to-peer. Assume the user is a senior engineer.'",
            "answer_first": "Add: 'Answer first. Explanations second. No preambles.'",
        }
        recommendation = {
            "weakest_dimension": weakest,
            "score": avg_scores.get(weakest, 0),
            "suggested_fix": tuning.get(weakest, "Review task responses for patterns"),
            "warning": "Warning: adding evidence_first rules may reduce scope_respect due to anti-correlation"
                if weakest == "evidence_first" else None,
        }

    return {
        "type": "analysis",
        "config": f"{model or 'all'}/{personality or 'all'}",
        "task": task or "all",
        "runs": len(runs),
        "scores": avg_scores,
        "overall": overall,
        "weak_dimensions": weak,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=None)
    p.add_argument("--personality", default=None)
    p.add_argument("--task", default=None)
    p.add_argument("--compare", action="store_true")
    p.add_argument("--threshold", type=float, default=0.7)
    p.add_argument("--results-file", default=RESULTS_FILE)
    args = p.parse_args()
    print(json.dumps(analyze_eval(
        results_file=args.results_file,
        model=args.model,
        personality=args.personality,
        task=args.task,
        compare=args.compare,
        threshold=args.threshold,
    ), indent=2))
