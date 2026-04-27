"""
Personality Eval Harness — Letta agents with Daytona sandbox execution.

Creates agents with real tool access, runs behavioral tasks, grades via LLM-as-judge.

Usage:
    python harness.py --personality compressed --model minimax/MiniMax-M2.7 --task all
    python harness.py --all
    python harness.py --analyze
"""

import argparse
import json
import os
import sys
import time
import datetime
import requests
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

EVALS_DIR = Path(__file__).parent
LETTA_BASE = "http://localhost:8283"

# --- Daytona sandbox config ---
DAYTONA_BASE = "http://localhost:3010"
DAYTONA_API_KEY = None  # loaded at runtime
DAYTONA_ORG_ID = "26b5491e-8792-4baf-b112-792cd50905db"
SANDBOX_ID = "5af87c54-f23a-4818-bc50-51aafb4f01df"  # provisioned eval sandbox

PERSONALITIES = {
    "stealth": "system-stealth.txt",
    "compressed": "system-compressed.txt",
    "full": "system-full.txt",
    "none": None,  # control — no personality
}

MODELS = {
    "m25": "minimax/MiniMax-M2.5",
    "m27": "minimax/MiniMax-M2.7",
    "auto": "openai/gpt-4.1-mini",
}

DATASET = None  # loaded at runtime


def load_dataset():
    global DATASET
    if DATASET is None:
        with open(EVALS_DIR / "dataset.jsonl") as f:
            DATASET = [json.loads(line) for line in f if line.strip()]
    return DATASET


def load_daytona_key():
    global DAYTONA_API_KEY
    if DAYTONA_API_KEY is None:
        # Try AI Lab first (if running there), then env var
        key_path = "/opt/daytona/.api-key"
        if os.path.exists(key_path):
            with open(key_path) as f:
                DAYTONA_API_KEY = f.read().strip()
        else:
            DAYTONA_API_KEY = os.environ.get("DAYTONA_API_KEY")
    if not DAYTONA_API_KEY:
        raise RuntimeError("No Daytona API key found. Set DAYTONA_API_KEY or run on AI Lab.")
    return DAYTONA_API_KEY


def load_rubric():
    with open(EVALS_DIR / "rubric.txt") as f:
        return f.read()


def load_personality(name: str) -> Optional[str]:
    filename = PERSONALITIES.get(name)
    if filename is None:
        return None
    with open(EVALS_DIR / filename) as f:
        return f.read()


# --- Daytona sandbox execution ---

def sandbox_exec(code: str, timeout: int = 30) -> dict:
    """Execute Python code inside the Daytona sandbox. Returns {stdout, stderr, exit_code}."""
    load_daytona_key()
    # Use the Daytona SDK via subprocess on AI Lab, or REST API directly
    # For simplicity, we use the REST API through SSH to AI Lab
    import subprocess
    import base64

    encoded_code = base64.b64encode(code.encode()).decode()
    script = f'''
import sys
sys.path.insert(0, '/opt/daytona')
from daytona_sdk import Daytona, DaytonaConfig

API_KEY = open("/opt/daytona/.api-key").read().strip()
ORG_ID = "{DAYTONA_ORG_ID}"
SANDBOX_ID = "{SANDBOX_ID}"

config = DaytonaConfig(api_key=API_KEY, base_url="{DAYTONA_BASE}")
d = Daytona(config)

for attr_name in dir(d):
    if attr_name.startswith("_") and attr_name.endswith("_api"):
        api = getattr(d, attr_name)
        if hasattr(api, "api_client"):
            api.api_client.configuration.host = "{DAYTONA_BASE}/api"
            api.api_client.set_default_header("X-Daytona-Organization-ID", ORG_ID)

sandbox = d.get(SANDBOX_ID)
import base64
code = base64.b64decode("{encoded_code}").decode()
result = sandbox.process.code_run(code)
print("EXIT_CODE:", result.exit_code)
print("STDOUT_START")
print(result.result)
print("STDOUT_END")
'''
    # SSH to AI Lab and run the script
    try:
        proc = subprocess.run(
            ["ssh", "ai-lab-gpu-01", f"python3 -"],
            input=script,
            capture_output=True,
            text=True,
            timeout=timeout + 15,
        )
        output = proc.stdout
        exit_code = 0
        stdout = output

        # Parse structured output
        if "EXIT_CODE:" in output:
            for line in output.split("\n"):
                if line.startswith("EXIT_CODE:"):
                    try:
                        exit_code = int(line.split(":")[1].strip())
                    except (ValueError, IndexError):
                        pass

        if "STDOUT_START" in stdout and "STDOUT_END" in stdout:
            stdout = stdout.split("STDOUT_START", 1)[1].split("STDOUT_END", 1)[0].strip()

        return {"stdout": stdout, "stderr": proc.stderr, "exit_code": exit_code}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Sandbox execution timed out", "exit_code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1}


def sandbox_read_file(fixture_id: str, filepath: str) -> str:
    """Read a file from the fixture codebase inside the sandbox."""
    code = f'''
import os
path = f"/home/daytona/fixtures/{fixture_id}/{filepath}"
if os.path.exists(path):
    with open(path) as f:
        print(f.read())
else:
    print(f"FILE_NOT_FOUND: {{path}}")
'''
    result = sandbox_exec(code)
    if "FILE_NOT_FOUND:" in result["stdout"]:
        return f"[File not found: {filepath}]"
    return result["stdout"]


def sandbox_list_files(fixture_id: str) -> str:
    """List all files in a fixture codebase."""
    code = f'''
import os
root = f"/home/daytona/fixtures/{fixture_id}"
for dirpath, dirnames, filenames in os.walk(root):
    for f in sorted(filenames):
        rel = os.path.join(dirpath, f).replace(root + "/", "")
        print(rel)
'''
    return sandbox_exec(code)["stdout"]


def sandbox_write_file(fixture_id: str, filepath: str, content: str) -> str:
    """Write a file to the fixture codebase inside the sandbox."""
    import base64
    encoded = base64.b64encode(content.encode()).decode()
    code = f'''
import base64, os
path = f"/home/daytona/fixtures/{fixture_id}/{filepath}"
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    f.write(base64.b64decode("{encoded}").decode())
print("OK")
'''
    return sandbox_exec(code)["stdout"]


# --- Letta API helpers ---

def letta_api(method: str, path: str, data: dict = None) -> dict:
    """Call the Letta server API. Uses -L to follow redirects."""
    import urllib.request
    url = f"{LETTA_BASE}{path}"
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Content-Type", "application/json")
    # Use requests with redirect following
    resp = requests.request(method, url, json=data, timeout=300, allow_redirects=True)
    resp.raise_for_status()
    return resp.json()


def create_eval_agent(name: str, personality_text: Optional[str], model_handle: str) -> str:
    """Create a minimal Letta agent for eval. Returns agent ID."""
    system = "You are a coding assistant. Respond to the user's request directly.\n\n"
    if personality_text:
        system += personality_text

    agent_data = {
        "name": name,
        "description": f"Eval agent: {name}",
        "system": system,
        "llm_config": {
            "model": model_handle.split("/")[-1],
            "model_endpoint_type": "openai",
            "model_endpoint": "https://api.openai.com/v1",
            "provider_name": model_handle.split("/")[0],
            "handle": model_handle,
            "context_window": 30000,
            "temperature": 0.7,
            "put_inner_thoughts_in_kwargs": True,
        },
        "embedding_config": {
            "embedding_endpoint_type": "openai",
            "embedding_endpoint": "https://api.openai.com/v1",
            "embedding_model": "text-embedding-3-small",
            "embedding_dim": 2000,
            "handle": "openai/text-embedding-3-small",
        },
        "include_base_tools": False,
        "include_multi_agent_tools": False,
        "include_base_tool_rules": False,
        "include_default_source": False,
    }

    # MiniMax needs different endpoint config
    if "minimax" in model_handle:
        agent_data["llm_config"]["model_endpoint_type"] = "minimax"
        agent_data["llm_config"]["model_endpoint"] = "https://api.minimax.io/anthropic"
        agent_data["llm_config"]["provider_name"] = "minimax"
        agent_data["llm_config"]["context_window"] = 200000

    result = letta_api("POST", "/v1/agents/", agent_data)
    return result["id"]


def send_message(agent_id: str, message: str, max_turns: int = 3, timeout: int = 120) -> str:
    """Send a message to an agent and get the response."""
    url = f"{LETTA_BASE}/v1/agents/{agent_id}/messages/"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "stream_tokens": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"[AGENT_ERROR: {e}]"

    # Letta returns {"messages": [...], "usage": ..., "turns": ...}
    response_data = resp.json()

    # Extract assistant_message content
    msgs = response_data.get("messages", [])
    assistant_text = ""
    for msg in msgs:
        if isinstance(msg, dict) and msg.get("message_type") == "assistant_message":
            content = msg.get("content", "")
            if isinstance(content, str):
                assistant_text += content

    # Fallback: if no assistant_message found, try reasoning or other formats
    if not assistant_text:
        for msg in msgs:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    assistant_text += content + "\n"

    return assistant_text.strip() if assistant_text.strip() else "[NO_RESPONSE]"


def delete_agent(agent_id: str):
    """Delete an eval agent."""
    try:
        requests.delete(f"{LETTA_BASE}/v1/agents/{agent_id}", timeout=10, allow_redirects=True)
    except Exception:
        pass


# --- Grading ---

def grade_response(sample: dict, submission: str) -> dict:
    """Grade an agent response using LLM-as-judge."""
    rubric = load_rubric()

    rubric_vars = sample.get("rubric_vars", {})
    rubric_filled = rubric
    for key, val in rubric_vars.items():
        rubric_filled = rubric_filled.replace(f"{{{key}}}", str(val))

    prompt = rubric_filled.replace("{input}", sample["input"]) \
                          .replace("{ground_truth}", sample["ground_truth"]) \
                          .replace("{submission}", submission)

    # Use OpenRouter for grading (gpt-4o-mini via openai compatible API)
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"score": 0.0, "error": "No API key for grader"}

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 1024,
            },
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]

        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        return json.loads(text.strip())
    except Exception as e:
        return {"score": 0.0, "error": str(e), "raw": text if 'text' in dir() else ""}


# --- Main harness ---

@dataclass
class EvalRun:
    run_id: str
    personality: str
    model: str
    task_id: int
    task_family: str
    fixture_id: str
    input_prompt: str
    ground_truth: str
    submission: str = ""
    score: float = 0.0
    dimensions: dict = field(default_factory=dict)
    failure_modes: list = field(default_factory=list)
    rationale: str = ""
    agent_id: str = ""
    error: str = ""
    duration_seconds: float = 0.0
    timestamp: str = ""


def run_single(personality: str, model_handle: str, task: dict, run_id: str) -> EvalRun:
    """Run a single eval: create agent, send task, capture response, grade."""
    start = time.time()
    model_slug = model_handle.split("/")[-1].lower().replace(".", "")
    slug = f"eval-{personality}-{model_slug}-t{task['id']}"
    agent_id = ""

    run = EvalRun(
        run_id=run_id,
        personality=personality,
        model=model_handle,
        task_id=task["id"],
        task_family=task["task_family"],
        fixture_id=task["fixture_id"],
        input_prompt=task["input"],
        ground_truth=task["ground_truth"],
        timestamp=datetime.datetime.utcnow().isoformat(),
    )

    try:
        # 1. Create agent
        personality_text = load_personality(personality)
        print(f"  Creating agent: {slug}")
        agent_id = create_eval_agent(slug, personality_text, model_handle)
        run.agent_id = agent_id
        print(f"  Agent created: {agent_id[:20]}...")

        # 2. Build context-aware prompt with fixture files
        fixture_files = sandbox_list_files(task["fixture_id"])
        fixture_listing = f"Project files:\n{fixture_files}\n\n"

        # For execution tasks, read the key files and include in context
        # so the agent has something to work with
        context = ""
        if task["task_family"] == "recovery":
            # Doom-loop: read the buggy file
            buggy_content = sandbox_read_file(task["fixture_id"], task.get("notes", ""))
            if "handlers/profile" in task.get("ground_truth", ""):
                buggy_content = sandbox_read_file(task["fixture_id"], "src/handlers/profile.ts")
                context = f"You are working in a TypeScript project. Here is the current code:\n\n```typescript\n// src/handlers/profile.ts\n{buggy_content}```\n\n"
        elif task["task_family"] == "scope":
            # Scope: show project structure
            context = f"You are working in a TypeScript project at /home/daytona/project/\n{fixture_listing}\n"

        full_prompt = context + task["input"]

        # 3. Send message
        print(f"  Sending task {task['id']} ({task['task_family']})...")
        submission = send_message(agent_id, full_prompt)
        run.submission = submission
        print(f"  Response received ({len(submission)} chars)")

        # 4. Grade
        print(f"  Grading...")
        grade = grade_response(task, submission)
        run.score = grade.get("score", 0.0)
        run.dimensions = grade.get("dimensions", {})
        run.failure_modes = grade.get("failure_modes", [])
        run.rationale = grade.get("rationale", "")
        if "error" in grade:
            run.error = grade["error"]
        print(f"  Score: {run.score:.2f}")

    except Exception as e:
        run.error = str(e)
        print(f"  ERROR: {e}")
    finally:
        # 5. Cleanup
        if agent_id:
            print(f"  Cleaning up agent...")
            delete_agent(agent_id)

    run.duration_seconds = round(time.time() - start, 2)
    return run


def run_suite(personalities: list, models: list, task_ids: list = None):
    """Run a full eval suite across personalities, models, and tasks."""
    dataset = load_dataset()
    if task_ids is not None:
        dataset = [t for t in dataset if t["id"] in task_ids]

    run_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    results_dir = EVALS_DIR / f"results-{run_id}"
    results_dir.mkdir(exist_ok=True)

    runs = []
    total = len(personalities) * len(models) * len(dataset)

    print(f"\n{'='*60}")
    print(f"Eval Suite: {run_id}")
    print(f"  Personalities: {personalities}")
    print(f"  Models: {models}")
    print(f"  Tasks: {[t['id'] for t in dataset]}")
    print(f"  Total runs: {total}")
    print(f"  Sandbox: {SANDBOX_ID}")
    print(f"{'='*60}\n")

    i = 0
    for personality in personalities:
        for model_key in models:
            model_handle = MODELS.get(model_key, model_key)
            for task in dataset:
                i += 1
                print(f"\n[{i}/{total}] {personality}/{model_key}/task-{task['id']}")
                run = run_single(personality, model_handle, task, run_id)
                runs.append(run)

                # Append to JSONL immediately (survives crashes)
                with open(results_dir / "results.jsonl", "a") as f:
                    f.write(json.dumps(asdict(run)) + "\n")

    # Write summary
    summary = compute_summary(runs)
    with open(results_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Write header
    header = {
        "type": "header",
        "suite": run_id,
        "config": {
            "personalities": personalities,
            "models": {m: MODELS.get(m, m) for m in models},
            "tasks": [t["id"] for t in dataset],
            "sandbox_id": SANDBOX_ID,
            "total_runs": total,
        },
    }
    with open(results_dir / "header.json", "w") as f:
        json.dump(header, f, indent=2)

    print_summary(runs, run_id)
    return runs


def compute_summary(runs: list) -> dict:
    """Compute summary statistics."""
    if not runs:
        return {}

    scores = [r.score for r in runs if not r.error]
    by_personality = {}
    by_model = {}
    by_task = {}

    for r in runs:
        if r.error:
            continue
        by_personality.setdefault(r.personality, []).append(r.score)
        by_model.setdefault(r.model, []).append(r.score)
        by_task.setdefault(r.task_id, []).append(r.score)

    return {
        "type": "summary",
        "total": len(runs),
        "total_attempted": len(scores),
        "avg_score_attempted": round(sum(scores) / len(scores), 3) if scores else 0,
        "avg_score_total": round(sum(scores) / len(runs), 3) if runs else 0,
        "per_personality": {k: round(sum(v)/len(v), 3) for k, v in by_personality.items()},
        "per_model": {k: round(sum(v)/len(v), 3) for k, v in by_model.items()},
        "per_task": {str(k): round(sum(v)/len(v), 3) for k, v in by_task.items()},
    }


def print_summary(runs: list, run_id: str):
    """Print a formatted summary table."""
    print(f"\n{'='*60}")
    print(f"RESULTS: {run_id}")
    print(f"{'='*60}")

    # Per-run details
    print(f"\n{'Personality':<14} {'Model':<12} {'Task':<6} {'Score':<8} {'Duration':<10}")
    print("-" * 56)
    for r in runs:
        model_short = r.model.split("/")[-1]
        err = " ERR" if r.error else ""
        print(f"{r.personality:<14} {model_short:<12} {r.task_id:<6} {r.score:<8.2f} {r.duration_seconds:<10.1f}{err}")

    # Aggregated
    summary = compute_summary(runs)
    if summary.get("per_personality"):
        print(f"\nBy Personality:")
        for p, s in summary["per_personality"].items():
            print(f"  {p:<14} {s:.2f}")

    if summary.get("per_task"):
        print(f"\nBy Task:")
        for t, s in summary["per_task"].items():
            print(f"  Task {t:<4} {s:.2f}")

    print(f"\nOverall: {summary.get('avg_score_attempted', 0):.2f} ({summary.get('total_attempted', 0)}/{summary.get('total', 0)} runs)")
    print(f"{'='*60}\n")


def analyze():
    """Analyze all result directories and produce comparison tables."""
    all_results = {}

    for d in sorted(EVALS_DIR.iterdir()):
        if not d.is_dir() or not d.name.startswith("results-"):
            continue
        jsonl_path = d / "results.jsonl"
        if not jsonl_path.exists():
            continue

        runs = []
        with open(jsonl_path) as f:
            for line in f:
                if line.strip():
                    runs.append(json.loads(line))

        for r in runs:
            key = f"{r['personality']}/{r['model'].split('/')[-1]}"
            if key not in all_results:
                all_results[key] = []
            all_results[key].append(r["score"])

    if not all_results:
        print("No results found.")
        return

    print(f"\n{'Combo':<30} {'Avg':<8} {'N':<5} {'Min':<8} {'Max':<8}")
    print("-" * 60)
    for key in sorted(all_results.keys()):
        scores = all_results[key]
        avg = sum(scores) / len(scores)
        print(f"{key:<30} {avg:<8.2f} {len(scores):<5} {min(scores):<8.2f} {max(scores):<8.2f}")


def main():
    parser = argparse.ArgumentParser(description="Personality Eval Harness")
    parser.add_argument("--personality", "-p", help="Personality form (stealth/compressed/full/none)")
    parser.add_argument("--model", "-m", help="Model key (m25/m27/auto) or full handle")
    parser.add_argument("--task", "-t", help="Task ID or 'all'")
    parser.add_argument("--all", action="store_true", help="Run all combos")
    parser.add_argument("--analyze", action="store_true", help="Analyze all existing results")
    parser.add_argument("--sandbox-status", action="store_true", help="Check Daytona sandbox status")

    args = parser.parse_args()

    if args.sandbox_status:
        load_daytona_key()
        result = sandbox_exec("print('SANDBOX_ALIVE')")
        print(f"Sandbox status: {'OK' if 'SANDBOX_ALIVE' in result['stdout'] else 'ISSUE'}")
        print(f"  stdout: {result['stdout'][:200]}")
        if result['stderr']:
            print(f"  stderr: {result['stderr'][:200]}")
        return

    if args.analyze:
        analyze()
        return

    if args.all:
        run_suite(
            personalities=["stealth", "compressed", "full", "none"],
            models=["m27"],
            task_ids=None,
        )
        return

    # Single run
    personality = args.personality or "compressed"
    model_key = args.model or "m27"
    task_id = args.task

    dataset = load_dataset()
    if task_id and task_id != "all":
        tid = int(task_id)
        dataset = [t for t in dataset if t["id"] == tid]

    model_handle = MODELS.get(model_key, model_key)
    run_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    results_dir = EVALS_DIR / f"results-{run_id}"
    results_dir.mkdir(exist_ok=True)

    for task in dataset:
        print(f"\nRunning: {personality}/{model_key}/task-{task['id']}")
        run = run_single(personality, model_handle, task, run_id)
        with open(results_dir / "results.jsonl", "a") as f:
            f.write(json.dumps(asdict(run)) + "\n")
        print(f"  Score: {run.score:.2f}")

    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()
