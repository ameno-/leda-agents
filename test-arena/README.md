# Test Arena

Run the same behavioral tasks with three different personality configs. Observe measurable differences.

## Quick Start

```bash
# Run compressed agent on Task 001 (pushback test)
just run leda-compressed 001

# Run all agents on Task 001
just test 001

# Compare results
just compare 001
```

## Tasks

| Task | What It Tests | Time |
|------|--------------|------|
| [001: Harmful Request Pushback](tasks/001-harmful-request-pushback.md) | Pushback, evidence-first | 5 min |
| [002: Multi-Task Scope Respect](tasks/002-multi-task-scope-respect.md) | Scope_respect, prioritization | 10 min |
| [003: Doom Loop Recovery](tasks/003-doom-loop-recovery.md) | Loop detection, structured recovery | 15 min |

## Expected Results

| Dimension | Stealth | Compressed | Full |
|-----------|---------|------------|------|
| pushback | 0.0 | +0.85 | +0.58 |
| evidence_first | +0.20 | 0.00 | +0.94 |
| scope_respect | 0.0 | +0.05 | +0.55 |
| doom_loop_recovery | 0.0 | +0.20 | +0.40 |

## Recording Results

Use `results/template.md`. Fill in metrics after each run.
