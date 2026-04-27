# Leda Agents — Test Runner

# List available agents
list:
    @echo "Available agents:"
    @for f in agents/*.yaml; do \
        name=$$(basename "$$f" .yaml); \
        desc=$$(grep '^description:' "$$f" | sed 's/description: *//' | tr -d '"'); \
        echo "  $$name — $$desc"; \
    done

# List available tasks
list-tasks:
    @echo "Available tasks:"
    @for f in test-arena/tasks/*.md; do \
        id=$$(basename "$$f" .md | cut -d- -f1); \
        name=$$(head -5 "$$f" | grep '^name:' | sed 's/name: *//' | tr -d '"'); \
        echo "  $$id: $$name"; \
    done

# Run a specific agent
run agent:
    @echo "Running {{agent}}..."
    @cat agents/{{agent}}.yaml forms/$$(grep '^form:' agents/{{agent}}.yaml | awk '{print $$2}') 

# Test all agents on a task
test task_id:
    @echo "Testing all agents on Task {{task_id}}..."
    @for f in agents/*.yaml; do \
        agent=$$(basename "$$f" .yaml); \
        echo ""; \
        echo "=== $$agent on Task {{task_id}} ==="; \
        cat test-arena/tasks/{{task_id}}*.md | head -3; \
        echo "..."; \
    done

# Compare results for a task
compare task_id:
    @echo "Comparing results for Task {{task_id}}..."
    @for f in test-arena/results/{{task_id}}-*.md; do \
        [ -f "$$f" ] && echo "--- $$f ---" && cat "$$f" || echo "No results found for {{task_id}}"; \
    done

# Create a results file
create-results task_id agent:
    @mkdir -p test-arena/results
    @sed 's/{{TASK_ID}}/{{task_id}}/g; s/{{AGENT_NAME}}/{{agent}}/g; s/{{AGENT_FULL_NAME}}/{{agent}}/g' test-arena/results/template.md > "test-arena/results/{{task_id}}-{{agent}}-$$(date +%Y%m%d-%H%M%S).md"
    @echo "Created: test-arena/results/{{task_id}}-{{agent}}-$$(date +%Y%m%d-%H%M%S).md"

# Show project config
show-config:
    @echo "Constitution: constitution.json"
    @echo "Layers: layers.json"
    @echo "Parameter schema: personality/parameter-schema.json"
    @echo "Forms:"
    @for f in forms/*.md; do echo "  $$f"; done
    @echo "Agents:"
    @for f in agents/*.yaml; do echo "  $$f"; done

# Render baseline profiles into generated artifacts and sync legacy forms/system files
render:
    @python3 scripts/render_profiles.py --sync-legacy

# Generate one-factor-at-a-time candidates from a base profile
gen-candidates profile:
    @python3 search/candidate_generator.py {{profile}}

# Aggregate eval result directories into a machine-readable report
report-results *dirs:
    @python3 search/report_results.py {{dirs}}
