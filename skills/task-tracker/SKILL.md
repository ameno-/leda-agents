# Task Tracker Skill

Track task progress, completion gates, and verification steps for droid agents.

## Purpose

Maintain structured task state including current phase, completion gates, and verification status. This helps ensure follow-through discipline and prevents incomplete work.

## When to Use

Use this skill when:
- Starting a new task
- Reaching a completion gate
- Verifying work before declaring complete
- Recording task completion or deferral

## Commands

### `task_start(task_description: string, phases: string[])`

Initialize a new task with its required phases.

**Example**:
```
task_start("Fix login authentication bug", [
  "investigate",
  "implement",
  "verify",
  "document"
])
```

**Returns**: Task ID

### `task_phase_complete(task_id: string, phase: string, notes?: string)`

Mark a phase as complete and record notes.

**Example**:
```
task_phase_complete("task-123", "investigate", 
  "Found the bug in auth/validator.ts line 42")
```

### `task_check_completion_gates(task_id: string)`

Check all completion gates for a task.

**Returns**: Object with:
- `can_complete`: boolean
- `gates_passed`: string[]
- `gates_failed`: string[]

### `task_complete(task_id: string, summary: string)`

Mark a task as complete with a summary of what was done.

**Example**:
```
task_complete("task-123", "Fixed the null reference bug in auth/validator.ts. 
Added null checks and ran all tests. All tests passing.")
```

### `task_defer(task_id: string, reason: string)`

Defer a task for later with a reason.

**Example**:
```
task_defer("task-456", "Waiting for clarification on edge case handling")
```

## Completion Gates

The following gates must pass before a task can be marked complete:

1. **requirements_met**: All parts of the original request addressed
2. **code_complete**: Code compiles/builds without errors, no TODOs
3. **tests_pass**: Tests run and pass, no regressions
4. **documented**: Complex logic has comments, docs updated if needed
5. **verified**: Work has been verified (tests run, manual checks)
6. **pending_resolved**: All blocking pending items resolved

## Usage Pattern

```bash
# 1. Start the task
task_start "Add logging to validator" ["investigate", "implement", "verify", "document"]

# 2. Complete phases as you work
task_phase_complete "task-789" "investigate" "Found logging requirements in README"
task_phase_complete "task-789" "implement" "Added winston logger with INFO level"

# 3. Check completion gates before declaring done
task_check_completion_gates "task-789"

# 4. If gates pass, mark complete
task_complete "task-789" "Added structured logging to validator.ts. 
Logger outputs to both console and file. All tests passing."
```

## Notes

- This skill maintains state in the agent's expertise file
- Use this before declaring any task complete
- If `task_check_completion_gates` returns `can_complete: false`, address the failed gates first
- Use `task_defer` when you need more information or the task is blocked
