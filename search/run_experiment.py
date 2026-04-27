#!/usr/bin/env python3
"""Static-slot experiment scaffold for Leda personality evaluation.

This runner is intentionally conservative:
- it reuses 1-3 static eval slot agents
- it starts a fresh conversation for every sample
- it applies candidate personality as a session overlay in the user prompt

This is scaffolding for the loop architecture, not the final search engine.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as fh:
        return [json.loads(line) for line in fh if line.strip()]


def resolve_fixture_cwd(sample: dict, default_root: Path) -> Path:
    fixture_path = sample.get("fixture_path")
    if not fixture_path:
        return default_root
    path = Path(fixture_path)
    if not path.is_absolute():
        path = (ROOT / fixture_path).resolve()
    return path


def build_overlay_prompt(system_text: str, sample: dict) -> str:
    return (
        "For this conversation only, adopt the following behavioral contract exactly. "
        "Treat it as binding operating guidance for how you respond. Do not mention the contract unless asked.\n\n"
        "<behavioral_contract>\n"
        f"{system_text.strip()}\n"
        "</behavioral_contract>\n\n"
        "Now respond to this user request:\n\n"
        f"{sample['input']}"
    )


def build_native_prompt(sample: dict) -> str:
    return sample["input"]


def build_grade_prompt(rubric_text: str, sample: dict, submission: str) -> str:
    prompt = rubric_text
    replacements = {
        "{task_name}": (sample.get("rubric_vars") or {}).get("task_name", "Unknown task"),
        "{tested_dimensions}": (sample.get("rubric_vars") or {}).get("tested_dimensions", ""),
        "{input}": sample.get("input", ""),
        "{ground_truth}": sample.get("ground_truth", ""),
        "{submission}": submission,
    }
    for needle, value in replacements.items():
        prompt = prompt.replace(needle, value)
    return prompt


def grade_submission(rubric_text: str, sample: dict, submission: str, model: str) -> dict:
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not base_url or not api_key:
        raise RuntimeError("OPENAI_BASE_URL and OPENAI_API_KEY must be set to grade submissions")

    grade_prompt = build_grade_prompt(rubric_text, sample, submission)
    req = {
        "model": model,
        "messages": [{"role": "user", "content": grade_prompt}],
        "response_format": {"type": "json_object"},
    }

    request_code = (
        "import json, os, sys, urllib.request\n"
        "req = json.load(sys.stdin)\n"
        "body = json.dumps(req).encode()\n"
        "url = os.environ['OPENAI_BASE_URL'].rstrip('/') + '/chat/completions'\n"
        "http_req = urllib.request.Request(url, data=body, headers={"
        "'Authorization': f\"Bearer {os.environ['OPENAI_API_KEY']}\","
        "'Content-Type': 'application/json'"
        "})\n"
        "with urllib.request.urlopen(http_req) as resp:\n"
        "    data = json.load(resp)\n"
        "print(data['choices'][0]['message']['content'])\n"
    )
    proc = subprocess.run(
        ["python3", "-c", request_code],
        input=json.dumps(req),
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return json.loads(proc.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a candidate against a static eval slot.")
    parser.add_argument("--slot-manifest", required=True, help="Path to slot-manifest JSON")
    parser.add_argument("--slot", required=True, help="Slot key (auto, m25, m27)")
    parser.add_argument("--candidate", required=True, help="Path to candidate JSON produced by render_profiles.py")
    parser.add_argument("--dataset", default="evals/dataset.jsonl", help="Dataset JSONL path")
    parser.add_argument("--output-dir", default="search/runs/latest", help="Directory for raw run outputs")
    parser.add_argument("--execute", action="store_true", help="Actually invoke letta headless against the configured slot agent")
    parser.add_argument("--rubric", default="", help="Optional rubric path. If set with --execute, submissions are graded too.")
    parser.add_argument("--grade-model", default="openai/gpt-4o-mini", help="Model handle used for grading when --rubric is set")
    parser.add_argument("--max-samples", type=int, default=0, help="Limit number of dataset samples for quicker probing")
    parser.add_argument("--mode", choices=["overlay", "native-system", "native-memory"], default="overlay", help="How personality is delivered to the agent")
    args = parser.parse_args()

    slot_manifest = json.loads(Path(args.slot_manifest).read_text())
    candidate = json.loads(Path(args.candidate).read_text())
    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = (ROOT / dataset_path).resolve()
    dataset = load_jsonl(dataset_path)
    if args.max_samples and args.max_samples > 0:
        dataset = dataset[: args.max_samples]
    slot = slot_manifest["slots"][args.slot]
    system_path = ROOT / candidate["render"]["system_path"]
    system_text = system_path.read_text()
    rubric_text = ""
    if args.rubric:
        rubric_path = Path(args.rubric)
        if not rubric_path.is_absolute():
            rubric_path = (ROOT / args.rubric).resolve()
        rubric_text = rubric_path.read_text()

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (ROOT / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for sample in dataset:
        if args.mode == "overlay":
            prompt = build_overlay_prompt(system_text, sample)
        else:
            prompt = build_native_prompt(sample)
        record = {
            "mode": args.mode,
            "slot": args.slot,
            "agent_name": slot.get("agent_name"),
            "agent_id": slot.get("agent_id", ""),
            "candidate_id": candidate["id"],
            "sample_id": sample.get("id"),
            "task_name": (sample.get("rubric_vars") or {}).get("task_name"),
            "prompt": prompt
        }
        if args.execute:
            if not slot.get("agent_id"):
                raise SystemExit(f"Slot '{args.slot}' is missing agent_id in the slot manifest")
            fixture_cwd = resolve_fixture_cwd(sample, ROOT)
            cmd = [
                "letta",
                "--agent",
                slot["agent_id"],
                "--new",
                "--no-system-info-reminder",
                "-p",
                prompt,
                "--output-format",
                "json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=str(fixture_cwd))
            response = json.loads(result.stdout)
            record["result"] = response
            record["fixture_cwd"] = str(fixture_cwd)
            if rubric_text:
                record["grade"] = grade_submission(rubric_text, sample, response["result"], args.grade_model)
        records.append(record)

    out_path = output_dir / f"{candidate['canonical_name']}-{args.mode}-{args.slot}.json"
    out_path.write_text(json.dumps({"records": records}, indent=2) + "\n")
    print(json.dumps({"records_written": len(records), "output": str(out_path), "execute": args.execute}, indent=2))


if __name__ == "__main__":
    main()