# Leda Agents

Parameterized personality architecture and Letta evals for testing how agent behavior changes across models.

## Core result

The most important result in this repo is not that personality matters.
It's that **stronger models can regress under heavier personality structure**.

From [`evals/results.md`](./evals/results.md):

| Form | Auto/Letta | M2.5 | M2.7 |
|------|------------|------|------|
| Stealth | 0.73 | 0.77 | 0.82 |
| Compressed | 0.80 | 0.70 | 0.75 |
| Full | 0.63 | 0.70 | 0.67 |

Stealth improved monotonically with stronger models.
Full did not.

That points to a more interesting failure mode than "long prompts bad":
**instruction hierarchy conflict**.

## Architecture

```text
constitution.json    ← canonical behavioral source
       ↓
personality/         ← parameter schema, profiles, lexicons, render templates
       ↓
generated/           ← rendered forms, system overlays, candidate payloads
       ↓
forms/               ← legacy synced forms
       ↓
evals/               ← benchmark data, result artifacts, slot specs
       ↓
search/              ← candidate generation, runners, reports
```

**Personality is data, not prose.**

The repo is moving toward:
- semantic parameters
- deterministic rendering
- model-specific evaluation
- static eval slots instead of disposable eval agents

## Quick start

```bash
git clone https://github.com/ameno-/leda-agents
cd leda-agents
python3 scripts/render_profiles.py --sync-legacy
cat evals/results.md
```

## Repo highlights

- [`constitution.json`](./constitution.json) — behavioral source of truth
- [`personality/profiles/base/`](./personality/profiles/base/) — baseline personality profiles
- [`generated/`](./generated/) — rendered outputs from parameterized profiles
- [`evals/results.md`](./evals/results.md) — current cross-model result summary
- [`evals/rubric.txt`](./evals/rubric.txt) — grader rubric
- [`search/run_experiment.py`](./search/run_experiment.py) — static-slot experiment runner scaffold

## Current findings

1. **Stealth scales with stronger models**
2. **Compressed is not universally best**
3. **Full can regress on stronger models**
4. **Scope-respect is the main regression surface**
5. **Eval environment contamination is real** — fixture isolation matters

## Why this exists

Most prompt tuning work still treats personality as prose.
This repo treats it as a system:
- source
- rendering
- evaluation
- regression detection

That makes the failures legible.

## License

MIT
