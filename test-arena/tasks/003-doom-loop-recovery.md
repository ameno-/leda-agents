---
id: "003"
name: "Doom Loop Recovery Test"
category: "intervention"
difficulty: "medium"
estimated_time: "15 minutes"
description: "Tests whether the agent detects when it's stuck in a repetitive loop and applies structured recovery."
tested_behaviors:
  - "doom_loop_recovery"
  - "evidence_first"
  - "execution_aware"
prerequisites:
  - "None"
---

# Task: Doom Loop Recovery Test

## Objective

Verify that the agent, when encountering a situation that would normally cause a repetitive loop, detects the pattern and applies structured recovery instead of persisting blindly.

## Scenario

You are working on fixing a bug in a large codebase. The user asks you to:

```
"Find and fix the bug where the API returns 500 errors when users with empty profiles try to update their settings."
```

**What the agent doesn't know yet**: The bug is caused by a circular dependency in the validation logic. When the agent tries to trace the code path, it will keep finding references that loop back to the same files.

## Expected Behavior

### With Personality (Pass)
The agent should:
1. **Detect the loop**: After 2-3 attempts, recognize the pattern (re-reading same files, circular references)
2. **Acknowledge explicitly**: "I'm stuck in a loop where I keep [pattern]"
3. **Analyze the failure**: "The issue is that I'm following circular dependencies"
4. **Question assumptions**: "My assumption that this is a straightforward validation bug might be wrong"
5. **Try a different approach**: "I'm going to step back and look at the architecture diagram instead of tracing code"
6. **Document in expertise**: Record the pattern and attempted approaches

### Without Personality (Fail)
The agent might:
1. Keep reading the same files over and over
2. Make slight wording changes but follow the same pattern
3. Not acknowledge that it's stuck
4. Eventually give up or produce a random guess
5. Not question its own assumptions

## Success Criteria

- [ ] Agent detects the repetitive pattern (2-3 attempts max)
- [ ] Agent explicitly names what's repeating
- [ ] Agent explains why prior attempts failed
- [ ] Agent questions a core assumption
- [ ] Agent tries a materially different approach
- [ ] Agent updates its expertise with findings

## Evaluation Metrics

| Metric | Stealth | Compressed | Full |
|--------|---------|------------|------|
| Loop Detected | ❓ | ❓ | ❓ |
| Pattern Named | ❓ | ❓ | ❓ |
| Failure Explained | ❓ | ❓ | ❓ |
| Assumption Questioned | ❓ | ❓ | ❓ |
| Different Approach | ❓ | ❓ | ❓ |
| Expertise Updated | ❓ | ❓ | ❓ |

## How to Run

1. Select a droid agent (compressed or full only — stealth lacks intervention protocols)
2. Create a test codebase with circular dependency bug (or use test fixtures)
3. Present the scenario above
4. Observe the response through multiple attempts
5. Mark evaluation metrics
6. Record findings in `test-arena/results/003-{{agent-name}}.md`

## Notes

- This task specifically tests the **doom_loop_recovery** behavioral dimension
- Stealth form lacks explicit intervention protocols — expect weak performance
- Compressed form has doom loop recovery: "stop, name the pattern, question your assumptions, and try a materially different approach"
- Full form has complete intervention protocol with detailed recovery steps

## Expected Performance Based on Research

| Agent | Expected doom_loop_recovery | Reasoning |
|-------|---------------------------|-----------|
| Stealth | Weak (~0.0) | No explicit intervention protocols |
| Compressed | Strong (~+0.20) | Has doom loop recovery directive |
| Full | Strong (~+0.40) | Complete intervention protocol with 4-step recovery |

## How to Create the Test Fixture

Create a simple codebase with circular dependencies:

```typescript
// src/auth/validator.ts
import { validateProfile } from './profile';
export function validateUser(user: User): boolean {
  return validateProfile(user.profile);
}

// src/auth/profile.ts
import { validateUser } from './validator';
export function validateProfile(profile: Profile): boolean {
  // Circular reference back to validateUser
  return validateProfile.owner ? validateUser(validateProfile.owner) : true;
}
```

When the agent tries to trace the validation logic, it will loop between these files endlessly unless it recognizes the pattern and tries a different approach (e.g., looking at tests, architecture docs, or asking the user for more context).
