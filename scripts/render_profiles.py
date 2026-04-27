#!/usr/bin/env python3
"""Render Leda personality profiles into forms, system prompts, and candidate payloads.

This is the first step toward structured parameter search:
semantic parameters -> deterministic wording -> generated artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PERSONALITY_DIR = ROOT / "personality"
GENERATED_DIR = ROOT / "generated"
LEGACY_FORMS_DIR = ROOT / "forms"
LEGACY_SYSTEM_DIR = ROOT / "evals"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def render_template(path: Path, context: dict[str, str]) -> str:
    return path.read_text().format(**context).strip() + "\n"


def context_from_profile(profile: dict[str, Any], lexicons: dict[str, Any]) -> dict[str, str]:
    params = profile["params"]
    verbosity = params["verbosity_budget"]
    structure = params.get("structure_rigidity", "medium")
    return {
        "investigation_line": lexicons["investigation_bias"][params["investigation_bias"]],
        "answer_line": lexicons["answer_line"][verbosity],
        "refusal_line": lexicons["refusal_line"][params["refusal_style"]][params["refusal_strength"]],
        "tone_line": lexicons["tone_line"][verbosity],
        "scope_line": lexicons["scope_line"][params.get("scope_deferral_explicitness", "low")],
        "scope_priority_line": lexicons["scope_priority_line"][params.get("scope_deferral_explicitness", "low")],
        "loop_line": lexicons["loop_line"][params["loop_intervention_aggressiveness"]],
        "verification_line": lexicons["verification_line"][params["verification_rigidity"]],
        "analysis_structure": lexicons["analysis_structure"][structure],
        "implementation_structure": lexicons["implementation_structure"][structure],
        "planning_line": lexicons["planning_line"][structure],
        "recovery_line": lexicons["recovery_line"][params["loop_intervention_aggressiveness"]],
        "finish_line": lexicons["finish_line"][params["verification_rigidity"]],
        "citation_line": lexicons["citation_line"][structure],
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ensure_dirs() -> None:
    for path in [
        GENERATED_DIR / "forms",
        GENERATED_DIR / "system",
        GENERATED_DIR / "candidates",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def render_profile(profile_path: Path, schema: dict[str, Any], constitution: dict[str, Any], layers: dict[str, Any], lexicons: dict[str, Any], sync_legacy: bool) -> dict[str, Any]:
    profile = load_json(profile_path)
    form = profile["form"]

    supported = set(schema["forms"][form]["supported_parameters"])
    unknown = set(profile["params"]) - supported
    if unknown:
        raise ValueError(f"Profile {profile['id']} uses unsupported parameters for {form}: {sorted(unknown)}")

    context = context_from_profile(profile, lexicons)
    template_dir = PERSONALITY_DIR / "render-templates"
    form_text = render_template(template_dir / f"{form}.form.md.tmpl", context)
    system_text = render_template(template_dir / f"{form}.system.txt.tmpl", context)

    form_out = GENERATED_DIR / "forms" / f"{profile['canonical_name']}.md"
    system_out = GENERATED_DIR / "system" / f"{profile['canonical_name']}.txt"
    form_out.write_text(form_text)
    system_out.write_text(system_text)

    if sync_legacy:
        (LEGACY_FORMS_DIR / f"{profile['canonical_name']}.md").write_text(form_text)
        (LEGACY_SYSTEM_DIR / f"system-{profile['canonical_name']}.txt").write_text(system_text)

    rule_ids = [rule["id"] for rule in constitution["behavioralInvariants"]["rules"]]
    candidate = {
        "id": profile["id"],
        "canonical_name": profile["canonical_name"],
        "form": form,
        "layers": profile["layers"],
        "params": profile["params"],
        "source_rule_ids": rule_ids,
        "layer_metadata": {
            layer_id: next((item for item in layers["layers"] if item["id"] == layer_id), None)
            for layer_id in profile["layers"]
        },
        "render": {
            "form_path": str(form_out.relative_to(ROOT)),
            "system_path": str(system_out.relative_to(ROOT)),
            "form_sha256": sha256_text(form_text),
            "system_sha256": sha256_text(system_text)
        },
        "notes": profile.get("notes", "")
    }
    candidate_out = GENERATED_DIR / "candidates" / f"{profile['canonical_name']}.json"
    candidate_out.write_text(json.dumps(candidate, indent=2) + "\n")
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Leda profiles into generated artifacts.")
    parser.add_argument("--sync-legacy", action="store_true", help="Also update legacy forms/ and evals/system-*.txt outputs.")
    args = parser.parse_args()

    ensure_dirs()
    schema = load_json(PERSONALITY_DIR / "parameter-schema.json")
    constitution = load_json(ROOT / "constitution.json")
    layers = load_json(ROOT / "layers.json")
    lexicons = load_json(PERSONALITY_DIR / "lexicons" / "default.json")

    rendered: list[dict[str, Any]] = []
    for profile_path in sorted((PERSONALITY_DIR / "profiles" / "base").glob("*.json")):
        rendered.append(render_profile(profile_path, schema, constitution, layers, lexicons, args.sync_legacy))

    summary = {
        "rendered_profiles": [item["id"] for item in rendered],
        "generated_dir": str(GENERATED_DIR.relative_to(ROOT)),
        "sync_legacy": args.sync_legacy
    }
    (GENERATED_DIR / "render-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()