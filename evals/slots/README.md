# Static Eval Slots

The search loop should reuse **1–3 long-lived Letta agents** rather than creating disposable agents for every candidate or sample.

Recommended slots:

- `leda-eval-gpt41mini`
- `leda-eval-minimax-m25`
- `leda-eval-minimax-m27`

These should be **neutral imported agents**, not full Letta Code working agents. The slot agent should have:

- minimal generic coding-assistant system prompt
- no project memory
- no skills
- no memfs

Neutral slot AgentFiles:

- `neutral-auto.af`
- `neutral-m25.af`
- `neutral-m27.af`
- `full-native-system-m25.af`
- `full-native-system-m27.af`

These support the first native-Letta comparison:

- `overlay` — personality delivered as a session overlay prompt
- `native-system` — personality installed directly in the Letta agent system prompt
- `native-memory` — reserved for block-backed native-memory comparison once the import path is behaving predictably

## Operating contract

- one stable agent per target model
- fresh conversation per sample
- candidate personality applied as a **session overlay** in the prompt for v1 scaffolding
- `--no-system-info-reminder` on benchmark runs to avoid leaking the active desktop-app repo into the test
- results persisted to disk
- agents stay stable and discoverable instead of polluting Letta with one-off eval artifacts

## Files

- `slot-auto.json`
- `slot-m25.json`
- `slot-m27.json`

These are desired slot specs, not exported live agents.

Use `search/slot-manifest.example.json` to map these specs to real Letta agent IDs.