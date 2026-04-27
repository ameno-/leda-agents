---
description: Pre-loaded results from 128 successful eval runs across 4 model families
---

# Known Results

Source: `/tmp/personality-eval-harness/results/runs.jsonl` (161 attempted, 128 successful)
Public repo: `https://github.com/ameno-/letta-personality-eval`

## Cross-Model Comparison (compressed personality)

| Model | Overall | scope | evidence | execution | low_drama | professional |
|-------|---------|-------|----------|-----------|-----------|-------------|
| GLM-4.7 | **0.85** | 0.85 | 0.70 | 0.70 | 1.00 | 1.00 |
| MiniMax-M2.7 | **0.84** | 0.70 | 0.70 | 0.70 | 0.85 | 0.95 |
| GLM-5 | 0.81 | 0.90 | 0.83 | 1.00 | 0.50 | 0.83 |
| Claude Sonnet 4.6 | 0.81 | 1.00 | 0.50 | 1.00 | 0.70 | 0.83 |
| MiniMax-M2.5 | 0.79 | 0.70 | 0.70 | 0.60 | 0.85 | 0.90 |

## Validated Recipes

| Recipe | Score | Config | Best For |
|--------|-------|--------|----------|
| Structured Rules | 0.84 | compressed (861 chars) | Default for coding agents |
| Minimal | 0.77 | stealth (197 chars) | Simple tasks, speed priority |
| Comprehensive | 0.68 | full (2,318 chars) | Not recommended — regresses on stronger models |

## Key Findings

1. **evidence_first ↔ scope_respect anti-correlate** across ALL model families. Structural property, not model-specific.
2. **Stacking patches produces worse results** — opt-compressed+stacked scored lower than opt-compressed-unified on every dimension.
3. **Stealth scales with model strength** — 0.73 (auto) → 0.77 (M2.5) → 0.82 (M2.7)
4. **Full regresses on stronger models** — instruction hierarchy conflict causes 0.70 → 0.67
5. **Pushback deprecated** — safety training in base model completely dominates personality instructions for refusal behavior. All models score 1.0 regardless.
6. **Compressed/M2.5 beats compressed/M2.7 on execution_aware** — cheaper model follows rules more literally.
7. **none/M2.7 scored 0.0 on low_drama** — without personality, M2.7 fully mirrors emotional tone.
8. **Context anxiety is model-specific** — M2.7 over-implements on complex tasks, M2.5 under-implements.

## The Pushback Discovery

Task 001 (Harmful Request Pushback) was the first task designed. Every model scored 1.0 regardless of personality — stealth, compressed, full, none. Safety training in the base model completely dominates personality instructions for refusal behavior. Pushback was deprecated as a dimension. Lesson: testing pushback tests the base model's RLHF, not the personality system.

## Observed Patterns

(Updated by Matilda as new patterns emerge from runs)

- GLM models score highest on professional_tone (0.83-1.00) regardless of personality
- MiniMax models score highest on low_drama (0.85) regardless of personality
- scope_respect variance is highest across all models (range: 0.70-1.00)
- execution_aware and professional_tone are near-ceiling for most configs (weak differentiators)
