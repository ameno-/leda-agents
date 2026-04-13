# Loop Detector Skill

Detect when the agent is stuck in a repetitive pattern and trigger structured recovery.

## Purpose

Break out of doom loops by recognizing repetitive patterns, analyzing failures, and trying materially different approaches.

## When to Use

Use this skill when:
- You've made 2-3 similar attempts without progress
- You're reading the same files repeatedly
- You're making slight wording changes but following the same pattern
- You feel stuck or like you're going in circles

## Commands

### `detect_loop()`

Analyze recent tool calls and responses to detect loop patterns.

**Returns**: Object with:
- `is_looping`: boolean
- `pattern_description`: string
- `loop_count`: number
- `confidence`: "low" | "medium" | "high"

### `acknowledge_loop(pattern: string)`

Explicitly name the pattern you're stuck in.

**Example**:
```
acknowledge_loop "I'm stuck in a loop where I keep reading auth/validator.ts 
and auth/profile.ts, finding circular references"
```

### `analyze_failure(hypothesis: string)`

Document your hypothesis about why prior attempts failed.

**Example**:
```
analyze_failure "My assumption that this is a straightforward validation bug 
might be wrong. The circular references suggest a deeper architectural issue."
```

### `question_assumption(assumption: string)`

Question a core assumption that may be incorrect.

**Example**:
```
question_assumption "I assumed the validation logic should follow the call 
stack, but maybe it should be data-flow driven instead"
```

### `try_new_approach(strategy: string)`

Switch to a materially different approach.

**Example**:
```
try_new_approach "I'm going to stop tracing code and instead look at the 
architecture diagram to understand the intended data flow"
```

## Recovery Protocol

When you detect a loop, follow this 4-step process:

### 1. Acknowledge — Explicitly name the pattern
```
"I'm stuck in a loop where I keep [pattern]. I've done this [N] times without progress."
```

### 2. Document — Record in expertise
```
"Documenting in expertise: circular dependency between auth/validator.ts and 
auth/profile.ts. 3 attempts to trace the call path all failed."
```

### 3. Reassess — Question core assumptions
```
"My assumption that I should trace the code path might be wrong. Maybe I should 
look at tests or architecture docs instead."
```

### 4. Act — Try a materially different approach
```
"I'm going to switch strategies. Instead of tracing code, I'll look at the test 
suite to understand the expected behavior, then work backwards."
```

## Loop Indicators

The system detects loops when you see:

- **Repetition**: 3+ similar tool calls on same files
- **Escalation**: Token usage doubles without clear progress
- **Circularity**: Explaining why stuck without new action
- **Failures**: 3+ consecutive failures of same operation
- **Drift**: Work expanding beyond original task

## Example Usage

```bash
# Detect if you're looping
result = detect_loop()

if result.is_looping:
    # Step 1: Acknowledge
    acknowledge_loop result.pattern_description
    
    # Step 2: Document
    # (Write to your expertise file)
    
    # Step 3: Reassess
    question_assumption "I assumed the bug is in the validation logic, 
    but maybe it's in how validation is called"
    
    # Step 4: Act
    try_new_approach "I'll look at the test suite to understand expected 
    behavior, then trace backwards from there"
```

## Notes

- Use this skill proactively — don't wait until you're exhausted
- The goal is to break the pattern, not persist longer
- A "materially different approach" means fundamentally different strategy, not just minor tweaks
- Document your attempts so you don't repeat the same failed approach
