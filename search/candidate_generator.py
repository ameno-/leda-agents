#!/usr/bin/env python3
"""Generate one-factor-at-a-time candidate profiles from a base profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PERSONALITY_DIR = ROOT / "personality"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate candidate profiles from a base profile.")
    parser.add_argument("base_profile", help="Path to a base profile JSON file")
    parser.add_argument("--output-dir", default=str(ROOT / "search" / "candidates"), help="Directory for generated candidates")
    args = parser.parse_args()

    schema = json.loads((PERSONALITY_DIR / "parameter-schema.json").read_text())
    base_path = Path(args.base_profile)
    if not base_path.is_absolute():
        base_path = (ROOT / base_path).resolve()
    profile = json.loads(base_path.read_text())

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    supported = set(schema["forms"][profile["form"]]["supported_parameters"])
    for name, spec in schema["parameters"].items():
        if name not in supported or name not in profile["params"]:
            continue
        current = profile["params"][name]
        for value in spec["values"]:
            if value == current:
                continue
            candidate = json.loads(json.dumps(profile))
            candidate["id"] = f"{profile['canonical_name']}-{name}-{value}"
            candidate["notes"] = f"OAT candidate: vary {name} from {current} to {value}."
            candidate["params"][name] = value
            out_path = out_dir / f"{candidate['id']}.json"
            out_path.write_text(json.dumps(candidate, indent=2) + "\n")
            count += 1

    print(json.dumps({"base_profile": profile["id"], "candidates_written": count, "output_dir": str(out_dir)}, indent=2))


if __name__ == "__main__":
    main()