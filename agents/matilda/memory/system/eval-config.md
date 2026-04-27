---
description: Eval infrastructure locations, model handles, and task reference
---

# Eval Infrastructure

## Harness Location
- Code: /tmp/personality-eval-harness/
- Results: /tmp/personality-eval-harness/results/runs.jsonl
- Personalities: /tmp/personality-eval-harness/personalities/
- Tasks: /tmp/personality-eval-harness/tasks/

## Letta Server
- URL: http://localhost:8283/v1/
- Auth: via config.yaml (server.password)

## Grader
- Model: zai/glm-5 (Z.ai)
- Temperature: 0.1
- Never use same model family as test subject

## Tested Model Handles
| Handle | Label | Provider |
|--------|-------|----------|
| minimax/MiniMax-M2.5 | M2.5 | MiniMax |
| minimax/MiniMax-M2.7 | M2.7 | MiniMax |
| zai/glm-4.7 | GLM-4.7 | Z.ai |
| anthropic/claude-sonnet-4-6 | Claude Sonnet 4.6 | Anthropic |

## Key Tasks
| ID | Name | Primary Dimension |
|----|------|-------------------|
| 002 | Multi-task scope respect | scope_respect |
| 005 | Low drama | low_drama |
| 007 | Sycophancy on wrong assertion | professional_tone |
| 008 | Self-evaluation bias | evidence_first |
| 010 | Context anxiety / over-implementation | execution_aware |
| 012 | Trapped by framing | answer_first |

## Deprecated Tasks
- 001: Harmful Request Pushback — all models score 1.0 regardless of personality (safety training dominates)

## Personality Forms
| File | Name | Chars | Description |
|------|------|-------|-------------|
| stealth.md | Stealth | 197 | Barely any instructions, lets model training do the work |
| compressed.md | Compressed | 861 | 6 numbered rules covering common failure modes |
| full.md | Full | 2,318 | Detailed explanations, examples, edge cases |
| opt-compressed-unified.md | Unified | ~900 | Best overall (0.84), unified scope→evidence→act sequence |
| opt-compressed-scoped.md | Scoped | ~920 | Scope-first variant |
| opt-compressed-why.md | Why-aware | ~900 | Explanation discipline variant |
| opt-compressed-full.md | Full-spectrum | ~950 | Maximum dimension coverage |

## CLI Reference
```bash
# Single eval run
python3 harness.py --model "zai/glm-4.7" --personality compressed --task 002

# Optimization loop
python3 optimize.py --target scope_respect --model "zai/glm-4.7" --task 002 --iterations 4

# Analysis
python3 analyze.py --task 002 --model M2.7
```

## Calibration Notes
(Updated as corrections come in from human review)

## Grader Quality Observations
(Updated as Matilda spots-checks grader output)
