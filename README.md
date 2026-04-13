# Leda Agents

Personality-driven Letta agents with measurable behavioral differences. Three agents, three personality configs, same tasks.

## The Three Agents

| Agent | Form | Tokens | Strengths |
|-------|------|--------|-----------|
| **leda-stealth** | Stealth (~100t) | Minimal overhead, fast execution | Token-constrained environments |
| **leda-compressed** | Compressed (~150t) | Pushback, evidence-first, loop recovery | Most development work |
| **leda-full** | Full (~500t) | Complete constitution, orchestration, follow-through | Complex multi-file work |

## Architecture

```
constitution.json    ←  Single source of truth (6 behavioral invariants, 7 composable layers)
       ↓
   forms/            ←  Rendered personality forms (stealth, compressed, full)
       ↓
  agents/            ←  Letta agent configs referencing forms + skills
       ↓
  test-arena/        ←  Behavioral test scenarios + results
```

**Personality is data, not prose.** The constitution defines behavioral invariants (evidence-first, answer-first, pushback, low-drama, execution-aware, scope-respect). Forms render different subsets of these invariants at different token budgets. The test arena measures the differences.

## Quick Start

```bash
git clone https://github.com/ameno-/leda-agents
cd leda-agents

# Run a single agent on a test task
just run leda-compressed 001

# Run all agents on a task
just test 001

# Compare results
just compare 001
```

## Key Findings (MiniMax M2.5, 14 Experiments)

- **Active language beats passive**: "Refuse to implement" improved pushback from +0.20 to +0.85
- **Token budgets are model-specific**: M2.5 handles 500 tokens, M2.7 breaks at 150+
- **Directives compete**: evidence-first and scope-respect conflict when both emphasized
- **Compressed form achieved min_delta = 0.00** — no regressions across all 6 dimensions

## Model Compatibility

| Model | Stealth | Compressed | Full |
|-------|---------|------------|------|
| Claude Opus 4.6 | ✅ | ✅ | ✅ |
| MiniMax M2.5 | ✅ | ✅ | ✅ |
| MiniMax M2.7 | ✅ | ✅ | ❌ |
| GLM-5 Turbo | ⚠️ | ❌ | ❌ |

## Directory Structure

```
leda-agents/
├── constitution.json      # Canonical behavioral source
├── layers.json            # Layer composition rules
├── manifest.json          # Project manifest
├── agents/                # Letta agent definitions (YAML)
├── forms/                 # Rendered personality forms
├── test-arena/            # Behavioral test scenarios
├── skills/                # Agent skills
└── justfile               # Test runner commands
```

## License

MIT
