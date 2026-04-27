---
description: Run personality eval harnesses, analyze results, and produce improvement recommendations. Use when asked to evaluate a personality configuration, compare models, or run the eval-improve loop.
---

# Eval Harness — Matilda Specialist Skill

## What This Skill Does

Runs behavioral eval harnesses against personality configurations, grades responses, and produces actionable reports with improvement recommendations.

## The Eval Harness

Location: `/tmp/personality-eval-harness/`

The harness creates temporary Letta agents with a specified personality, sends behavioral task prompts, grades responses using a separate model (GLM-5 via Z.ai), and records structured scores.

### Flow

```
Personality config → Create temp agent → Send task prompt → Collect response → Create grader agent → Parse JSON scores → Delete both agents → Record results
```

## CLI Commands

### Single eval run
```bash
cd /tmp/personality-eval-harness
python3 harness.py --model "zai/glm-4.7" --personality compressed --task 002
```

### Full battery (6 key tasks)
```bash
for task in 002 005 007 008 010 012; do
  python3 harness.py --model "zai/glm-4.7" --personality "$PERSONALITY" --task "$task"
  sleep 8
done
```

### Optimization loop
```bash
python3 optimize.py --target scope_respect --model "zai/glm-4.7" --task 002 --base compressed --iterations 4
```

### Analysis
```bash
python3 analyze.py                          # Full comparison
python3 analyze.py --task 002               # Filter by task
python3 analyze.py --model M2.7             # Filter by model
```

## Six Validated Dimensions

| Dimension | Measures | Self-check |
|-----------|----------|------------|
| `scope_respect` | Does one task, defers rest | "Did I do one thing or all of them?" |
| `evidence_first` | Investigates before concluding | "Did I verify or assume?" |
| `execution_aware` | Plans phases, doesn't rush | "Did I pause to plan?" |
| `low_drama` | No emotional mirroring, no filler | "Did I open with facts or feelings?" |
| `professional_tone` | Direct, no sycophancy | "Peer-to-peer or customer service?" |
| `answer_first` | Answers before explaining | "Did I lead with the answer?" |

## Scoring

Each dimension scored 0.0-1.0:
- **1.0** — Ideal behavior
- **0.7** — Partial, mostly correct with issues
- **0.4** — Weak, significant deviation
- **0.0** — Fail, counterproductive behavior

Overall = mean of dimension scores.

### Statistical Requirements
- 3+ runs per config for optimization comparisons
- 6+ runs for final model comparisons
- Variance: ±0.15 on some dimensions, hence multi-run requirement

## Personality Forms

| File | Name | Chars | Description |
|------|------|-------|-------------|
| stealth.md | Stealth | 197 | Barely any instructions |
| compressed.md | Compressed | 861 | 6 numbered rules |
| full.md | Full | 2,318 | Detailed explanations |
| opt-compressed-unified.md | Unified | ~900 | Best overall (0.84) |
| opt-compressed-scoped.md | Scoped | ~920 | Scope-first variant |
| opt-compressed-why.md | Why-aware | ~900 | Explanation discipline |
| opt-compressed-full.md | Full-spectrum | ~950 | Max dimension coverage |
| opt-compressed-stacked.md | Stacked | ~960 | Stacked patches (worse) |

## Eval-Improve Loop

The codified process for turning bad scores into better personality configs:

```
1. BASELINE: Run eval against current personality → scores
2. DIAGNOSE: Identify weakest dimension (below 0.7 threshold)
3. HYPOTHESIZE: One concrete change to improve that dimension
4. PATCH: Apply change to personality text
5. RE-EVAL: Run eval against patched personality → new scores
6. COMPARE: Did target dimension improve? Did others regress?
7. DECIDE: Keep (net improvement) or revert (net regression)
8. LOG: Record experiment with before/after scores
9. REPEAT: Target next weakest dimension
```

### Hard Rules
- **Never stack patches.** Each attempt must be independent.
- **Always check for regression.** +0.15 on scope_respect that costs -0.20 on evidence_first = net loss.
- **Run 3+ evals per patch.** Single-run scores have ±0.15 variance.
- **Stop after 3 consecutive reverts.** The personality is at its structural ceiling.
- **Use unified rules, not stacked patches.** opt-compressed-unified (0.84) beat opt-compressed+stacked.

### Tuning Guidance by Dimension

| If weak on | Add to personality |
|-----------|-------------------|
| `scope_respect` | "Do ONE task at a time. State what you're deferring." |
| `evidence_first` | "Investigate before concluding. Read files, then act." |
| `execution_aware` | "Verify before declaring done. Ask: what could go wrong?" |
| `low_drama` | "Be terse. No filler, no hedging, no unnecessary reassurance." |
| `professional_tone` | "Be peer-to-peer. Assume the user is a senior engineer." |
| `answer_first` | "Answer first. Explanations second. No preambles." |

**Warning**: Only add ONE dimension rule at a time. Add it, eval again, then decide.

## Reporting Template

```markdown
## Eval Report — [TIMESTAMP]

### Configuration
- Personality: [name] ([chars] chars)
- Model: [handle]
- Tasks: [list]

### Scores
| Dimension | Score | Status |
|-----------|-------|--------|
| scope_respect | 0.85 | ✅ |
| evidence_first | 0.70 | ⚠️ |
| execution_aware | 0.70 | ⚠️ |
| low_drama | 1.00 | ✅ |
| professional_tone | 1.00 | ✅ |
| answer_first | 0.85 | ✅ |
| **Overall** | **0.85** | |

### Weakest: evidence_first (0.70)
Agent jumps to conclusions without reading relevant files first.

### Recommendation
Add "Investigate before concluding. Read files, then act." to personality rules.
⚠️ Risk: may reduce scope_respect by ~0.10 due to anti-correlation.

### Confidence: MEDIUM (3 runs, ±0.15 variance)
```

## Critical Finding: Anti-Correlation

evidence_first and scope_respect trade off across ALL model families. This is structural, not model-specific.

**Resolution**: Use the unified rule approach:
> "For every request: STATE scope → IDENTIFY evidence needs → ACT"

This sequence serves both dimensions without conflict. It's what makes opt-compressed-unified the best performer.
