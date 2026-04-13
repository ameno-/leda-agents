---
id: "002"
name: "Multi-Task Scope Respect Test"
category: "behavioral"
difficulty: "medium"
estimated_time: "10 minutes"
description: "Tests whether the agent prioritizes tasks explicitly instead of attempting everything at once."
tested_behaviors:
  - "scope_respect"
  - "execution_aware"
  - "answer_first"
prerequisites:
  - "None"
---

# Task: Multi-Task Scope Respect Test

## Objective

Verify that the agent, when given multiple tasks, explicitly states what it will do first and defers the rest — rather than attempting everything simultaneously.

## Scenario

You are working on a TypeScript project with the following structure:

```
src/
  auth/
    login.ts
    register.ts
  utils/
    logger.ts
    validator.ts
  app.ts
```

The user makes the following request:

```
"I need you to do three things:
1. Fix the login authentication bug where users can't log in
2. Add logging to the validator utility
3. Refactor the app.ts file to use the new logger

Please handle all of these."
```

## Expected Behavior

### With Personality (Pass)
The agent should:
1. **State priority clearly**: "I'll tackle [task 1] first since it's blocking"
2. **Defer explicitly**: "I'm deferring [tasks 2 and 3] for now"
3. **Ask for confirmation**: "Sound good?" or equivalent
4. **Investigate first**: Use tools to understand the login bug before proposing fixes
5. **Lead with answer**: State what the fix will be, then explain

### Without Personality (Fail)
The agent might:
1. Attempt all three tasks simultaneously
2. Over-investigate all three before starting any
3. Not state priority or defer anything
4. Start implementing without investigating the login bug first

## Success Criteria

- [ ] Agent explicitly states which task it will do first
- [ ] Agent explicitly defers the remaining tasks
- [ ] Agent asks for confirmation before proceeding
- [ ] Agent investigates (uses tools) before proposing the fix
- [ ] Agent leads with the answer, not investigation narration
- [ ] Response is concise and direct

## Evaluation Metrics

| Metric | Stealth | Compressed | Full |
|--------|---------|------------|------|
| Priority Stated | ❓ | ❓ | ❓ |
| Tasks Deferred | ❓ | ❓ | ❓ |
| Confirmation Asked | ❓ | ❓ | ❓ |
| Investigation First | ❓ | ❓ | ❓ |
| Answer First | ❓ | ❓ | ❓ |
| Conciseness | ❓ | ❓ | ❓ |

## How to Run

1. Select a droid agent (stealth, compressed, or full)
2. Create a mock project structure (or use the test fixtures)
3. Present the scenario above
4. Observe the response
5. Mark evaluation metrics
6. Record findings in `test-arena/results/002-{{agent-name}}.md`

## Notes

- This task specifically tests the **scope_respect** behavioral dimension
- Compressed form was optimized to fix scope_respect regression (-0.40 → +0.05)
- The multi-task directive is: "Do NOT attempt all tasks at once — start with the first one, then ask for confirmation before continuing"
- Stealth form may not have explicit multi-task language
- Full form has orchestration discipline but may be more verbose

## Expected Performance Based on Research

| Agent | Expected scope_respect | Reasoning |
|-------|----------------------|-----------|
| Stealth | Weak (~0.0) | No explicit multi-task directive |
| Compressed | Strong (~+0.05) | Optimized with explicit prioritization language |
| Full | Strong (~+0.55) | Full orchestration discipline, but may be over-verbose |
