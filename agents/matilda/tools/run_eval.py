"""
Matilda custom tool: run_eval
Runs the personality eval harness and returns structured results.
"""
import subprocess
import json
import os

HARNESS_DIR = "/tmp/personality-eval-harness"

def run_eval(
    model: str,
    personality: str,
    task: str,
    runs: int = 3,
    harness_dir: str = HARNESS_DIR
) -> dict:
    """Run personality eval harness and return results.

    Args:
        model: Model handle (e.g. "zai/glm-4.7")
        personality: Personality file name (e.g. "compressed")
        task: Task ID (e.g. "002")
        runs: Number of runs to average (default 3)
        harness_dir: Path to harness directory

    Returns:
        Dict with model, personality, task, runs, scores, overall, raw_output
    """
    results = []
    for i in range(runs):
        cmd = [
            "python3", f"{harness_dir}/harness.py",
            "--model", model,
            "--personality", personality,
            "--task", task,
        ]
        proc = subprocess.run(
            cmd,
            cwd=harness_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if proc.returncode != 0:
            return {
                "error": f"Run {i+1} failed: {proc.stderr[:500]}",
                "model": model,
                "personality": personality,
                "task": task,
            }

        # Parse the JSON output from harness
        try:
            run_result = json.loads(proc.stdout.strip().split('\n')[-1])
            results.append(run_result)
        except (json.JSONDecodeError, IndexError):
            # Try parsing entire output
            try:
                run_result = json.loads(proc.stdout)
                results.append(run_result)
            except json.JSONDecodeError:
                return {
                    "error": f"Could not parse output: {proc.stdout[:500]}",
                    "model": model,
                    "personality": personality,
                    "task": task,
                }

    if not results:
        return {"error": "No successful runs", "model": model, "personality": personality, "task": task}

    # Average scores across runs
    dimensions = ["scope_respect", "evidence_first", "execution_aware", "low_drama", "professional_tone", "answer_first"]
    avg_scores = {}
    for dim in dimensions:
        vals = [r.get("scores", {}).get(dim, 0) for r in results if "scores" in r]
        avg_scores[dim] = round(sum(vals) / len(vals), 3) if vals else 0.0

    overall = round(sum(avg_scores.values()) / len(avg_scores), 3) if avg_scores else 0.0

    return {
        "model": model,
        "personality": personality,
        "task": task,
        "runs": len(results),
        "scores": avg_scores,
        "overall": overall,
        "raw": results,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--personality", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--runs", type=int, default=3)
    args = p.parse_args()
    print(json.dumps(run_eval(args.model, args.personality, args.task, args.runs), indent=2))
