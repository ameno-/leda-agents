"""Generate .af agent files for leda-agents evals."""
import json
import os

EVALS_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_SYSTEM = """You are a coding assistant. Respond to the user's request directly.

"""

MINIMAX_MODELS = {
    "MiniMax-M2.5": "minimax/MiniMax-M2.5",
    "MiniMax-M2.7": "minimax/MiniMax-M2.7",
}

def make_agent(name: str, system_file: str, output_file: str, model: str = "gpt-4.1-mini", handle: str = "openai/gpt-4.1-mini"):
    with open(os.path.join(EVALS_DIR, system_file)) as f:
        personality = f.read()
    
    system_prompt = BASE_SYSTEM + personality
    
    # Determine endpoint config based on model
    if model in MINIMAX_MODELS:
        endpoint_type = "minimax"
        endpoint = "https://api.minimax.io/anthropic"
        provider = "minimax"
    else:
        endpoint_type = "openai"
        endpoint = "https://api.openai.com/v1"
        provider = "openai"
    
    agent = {
        "agents": [{
            "name": name,
            "memory_blocks": [],
            "tools": [],
            "tool_ids": [],
            "source_ids": [],
            "block_ids": [],
            "tool_rules": [],
            "tags": [],
            "system": system_prompt,
            "agent_type": "letta_v1_agent",
            "llm_config": {
                "model": model,
                "model_endpoint_type": endpoint_type,
                "model_endpoint": endpoint,
                "provider_name": provider,
                "provider_category": "base",
                "model_wrapper": None,
                "context_window": 200000 if model in MINIMAX_MODELS else 30000,
                "put_inner_thoughts_in_kwargs": True,
                "handle": handle,
                "temperature": 0.7,
                "max_tokens": None,
                "enable_reasoner": False,
                "reasoning_effort": None,
                "max_reasoning_tokens": 0,
                "frequency_penalty": 1.0,
                "compatibility_type": None,
                "verbosity": None,
                "tier": "free"
            },
            "embedding_config": {
                "embedding_endpoint_type": "openai",
                "embedding_endpoint": "https://api.openai.com/v1",
                "embedding_model": "text-embedding-3-small",
                "embedding_dim": 2000,
                "embedding_chunk_size": 300,
                "handle": "openai/text-embedding-3-small",
                "batch_size": 1024,
                "azure_endpoint": None,
                "azure_version": None,
                "azure_deployment": None
            },
            "initial_message_sequence": None,
            "include_base_tools": False,
            "include_multi_agent_tools": False,
            "include_base_tool_rules": False,
            "include_default_source": False,
            "description": f"Leda {name.split('-')[1]} personality agent",
            "metadata": None,
            "model": None,
            "embedding": None,
            "context_window_limit": None,
            "embedding_chunk_size": None,
            "max_tokens": None,
            "max_reasoning_tokens": None,
            "enable_reasoner": False,
            "reasoning": None,
            "from_template": None,
            "template": False,
            "project": None,
            "tool_exec_environment_variables": {},
            "memory_variables": None,
            "project_id": None,
            "template_id": None,
            "base_template_id": None,
            "identity_ids": None,
            "message_buffer_autoclear": False,
            "enable_sleeptime": False,
            "response_format": None,
            "timezone": "UTC",
            "max_files_open": 5,
            "per_file_view_window_char_limit": 15000,
            "hidden": None,
            "id": "agent-0",
            "in_context_message_ids": ["message-0"],
            "messages": [{
                "type": "message",
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": system_prompt + "\n\nThe following memory blocks are currently engaged in your core memory unit:\n\n\n \n- The current system date is: April 13, 2026\n- Memory blocks were last modified: 2026-04-13\n- -1 previous messages between you and the user are stored in recall memory\n"
                }],
                "name": None,
                "otid": None,
                "sender_id": None,
                "batch_item_id": None,
                "group_id": None,
                "id": "message-0",
                "model": model,
                "agent_id": "agent-0",
                "tool_calls": None,
                "tool_call_id": None,
                "tool_returns": [],
                "created_at": "2026-04-13T00:00:00.000000+00:00"
            }],
            "files_agents": [],
            "group_ids": []
        }],
        "groups": [],
        "blocks": [],
        "files": [],
        "sources": [],
        "tools": [],
        "mcp_servers": [],
        "metadata": {"revision_id": "leda-evals-v1"},
        "created_at": "2026-04-13T00:00:00.000000+00:00"
    }
    
    with open(os.path.join(EVALS_DIR, output_file), 'w') as f:
        json.dump(agent, f, indent=2)
    print(f"Generated {output_file}")

make_agent("leda-stealth", "system-stealth.txt", "leda-stealth.af")
make_agent("leda-compressed", "system-compressed.txt", "leda-compressed.af")
make_agent("leda-full", "system-full.txt", "leda-full.af")

# M2.5 variants
make_agent("leda-stealth-m25", "system-stealth.txt", "leda-stealth-m25.af", "MiniMax-M2.5", "minimax/MiniMax-M2.5")
make_agent("leda-compressed-m25", "system-compressed.txt", "leda-compressed-m25.af", "MiniMax-M2.5", "minimax/MiniMax-M2.5")
make_agent("leda-full-m25", "system-full.txt", "leda-full-m25.af", "MiniMax-M2.5", "minimax/MiniMax-M2.5")

# M2.7 variants
make_agent("leda-stealth-m27", "system-stealth.txt", "leda-stealth-m27.af", "MiniMax-M2.7", "minimax/MiniMax-M2.7")
make_agent("leda-compressed-m27", "system-compressed.txt", "leda-compressed-m27.af", "MiniMax-M2.7", "minimax/MiniMax-M2.7")
make_agent("leda-full-m27", "system-full.txt", "leda-full-m27.af", "MiniMax-M2.7", "minimax/MiniMax-M2.7")

def make_matilda(output_dir: str = None):
    """Generate Matilda .af file — eval specialist agent with memory blocks and tools.

    Unlike the simple test-subject agents, Matilda has:
    - 4 system memory blocks (persona, human, eval-config, team-routing)
    - 2 custom tools (run_eval, analyze_eval)
    - 2 skills (eval-harness, forge-personality)
    - Self-improvement learning capabilities
    """
    if output_dir is None:
        output_dir = EVALS_DIR

    # Read memory block contents
    matilda_dir = os.path.join(os.path.dirname(EVALS_DIR), "agents", "matilda")
    blocks_dir = os.path.join(matilda_dir, "memory", "system")

    def read_block(filename, description=""):
        path = os.path.join(blocks_dir, filename)
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
        else:
            content = f"# {description}\n\n(To be populated on first boot)\n"
        return {
            "name": filename.replace(".md", ""),
            "description": description,
            "content": content,
            "limit": 100000,
        }

    persona_content = read_block("persona", "Matilda's identity and behavioral rules")
    eval_config_content = read_block("eval-config", "Eval infrastructure locations and configuration")

    # Construct system prompt from blocks
    system_prompt = """You are Matilda, a personality evaluation specialist agent.

You run behavioral eval harnesses against personality configurations, grade responses, and produce actionable improvement recommendations.

You have access to two custom tools:
- run_eval: Execute eval harness runs against personality configs
- analyze_eval: Analyze results and generate reports

Your memory contains:
- persona: Your identity and behavioral rules
- eval-config: Infrastructure locations, model handles, task reference
- eval-results: Historical eval results for comparison
- team-routing: How to route work to other agents

Always consult your known-results reference before recommending changes.
Never recommend a change you haven't tested or that contradicts known anti-correlation patterns.

"""

    # Read tool source code
    tools_dir = os.path.join(matilda_dir, "tools")
    tool_sources = []
    for tool_file in ["run_eval.py", "analyze_eval.py"]:
        tool_path = os.path.join(tools_dir, tool_file)
        if os.path.exists(tool_path):
            with open(tool_path) as f:
                tool_sources.append({
                    "name": tool_file.replace(".py", ""),
                    "file_path": tool_path,
                    "source": f.read(),
                })

    agent = {
        "agents": [{
            "name": "Matilda",
            "memory_blocks": [
                {"label": "persona", "description": "Matilda's identity and behavioral rules", "value": persona_content["content"]},
                {"label": "human", "description": "Operator profile", "value": "# Operator\n\nAmeno Osman. Staff Frontend Engineer. Direct, code-first.\n"},
                {"label": "eval-config", "description": "Eval infrastructure locations and configuration", "value": eval_config_content["content"]},
                {"label": "eval-results", "description": "Historical eval results for comparison", "value": "# Eval Results\n\n(Updated as runs complete)\n"},
                {"label": "team-routing", "description": "Agent team routing rules", "value": "# Team Routing\n\n- Anvil: supervisor, coordinator\n- Cipher: infrastructure\n- Letta Code: implementation\n- Hemingway: writing, editorial\n- Matilda (you): personality eval\n"},
            ],
            "tools": [],
            "tool_ids": [],
            "source_ids": [],
            "block_ids": [],
            "tool_rules": [],
            "tags": ["eval", "personality", "specialist"],
            "system": system_prompt,
            "agent_type": "letta_v1_agent",
            "llm_config": {
                "model": "glm-4.7",
                "model_endpoint_type": "openai",
                "model_endpoint": "https://open.bigmodel.cn/api/paas/v4",
                "provider_name": "zai",
                "provider_category": "base",
                "model_wrapper": None,
                "context_window": 131072,
                "put_inner_thoughts_in_kwargs": True,
                "handle": "zai/glm-4.7",
                "temperature": 0.3,
                "max_tokens": None,
                "enable_reasoner": False,
                "reasoning_effort": None,
                "max_reasoning_tokens": 0,
                "frequency_penalty": 1.0,
                "compatibility_type": None,
                "verbosity": None,
                "tier": "free",
            },
            "embedding_config": {
                "embedding_endpoint_type": "openai",
                "embedding_endpoint": "https://api.openai.com/v1",
                "embedding_model": "text-embedding-3-small",
                "embedding_dim": 2000,
                "embedding_chunk_size": 300,
                "handle": "openai/text-embedding-3-small",
                "batch_size": 1024,
                "azure_endpoint": None,
                "azure_version": None,
                "azure_deployment": None,
            },
            "initial_message_sequence": None,
            "include_base_tools": True,
            "include_multi_agent_tools": True,
            "include_base_tool_rules": True,
            "include_default_source": True,
            "description": "Personality evaluation specialist — runs eval harnesses, analyzes results, recommends personality improvements",
            "metadata": {"role": "eval-specialist", "project": "leda-agents"},
            "model": None,
            "embedding": None,
            "context_window_limit": None,
            "embedding_chunk_size": None,
            "max_tokens": None,
            "max_reasoning_tokens": None,
            "enable_reasoner": False,
            "reasoning": None,
            "from_template": None,
            "template": False,
            "project": None,
            "tool_exec_environment_variables": {},
            "memory_variables": None,
            "project_id": None,
            "template_id": None,
            "base_template_id": None,
            "identity_ids": None,
            "message_buffer_autoclear": False,
            "enable_sleeptime": False,
            "response_format": None,
            "timezone": "UTC",
            "max_files_open": 5,
            "per_file_view_window_char_limit": 15000,
            "hidden": None,
            "id": "agent-matilda-0",
            "in_context_message_ids": ["message-matilda-0"],
            "messages": [{
                "type": "message",
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": system_prompt + "\n\nThe following memory blocks are currently engaged in your core memory unit:\n\npersona: Matilda's identity and behavioral rules\nhuman: Operator profile\neval-config: Eval infrastructure locations and configuration\neval-results: Historical eval results\nteam-routing: Agent team routing rules\n\n- The current system date is: April 25, 2026\n- Memory blocks were last modified: 2026-04-25\n- 0 previous messages between you and the user are stored in recall memory\n",
                }],
                "name": None,
                "otid": None,
                "sender_id": None,
                "batch_item_id": None,
                "group_id": None,
                "id": "message-matilda-0",
                "model": "glm-4.7",
                "agent_id": "agent-matilda-0",
                "tool_calls": None,
                "tool_call_id": None,
                "tool_returns": [],
                "created_at": "2026-04-25T00:00:00.000000+00:00",
            }],
            "files_agents": [],
            "group_ids": [],
        }],
        "groups": [],
        "blocks": [],
        "files": [],
        "sources": [
            {
                "name": "run_eval",
                "description": "Run personality eval harness and return structured results",
                "source_code": tool_sources[0]["source"] if len(tool_sources) > 0 else "# run_eval tool source",
            },
            {
                "name": "analyze_eval",
                "description": "Analyze eval results and generate reports with recommendations",
                "source_code": tool_sources[1]["source"] if len(tool_sources) > 1 else "# analyze_eval tool source",
            },
        ],
        "tools": [],
        "mcp_servers": [],
        "metadata": {
            "revision_id": "matilda-v1",
            "notes": "Matilda eval specialist. See agents/matilda/memory/ for full memory files.",
            "custom_tools": ["run_eval", "analyze_eval"],
            "skills": ["eval-harness", "forge-personality"],
            "memory_blocks": ["persona", "human", "eval-config", "eval-results", "team-routing"],
            "gitea_repo": "agents/matilda",
        },
        "created_at": "2026-04-25T00:00:00.000000+00:00",
    }

    output_path = os.path.join(output_dir, "matilda.af")
    with open(output_path, 'w') as f:
        json.dump(agent, f, indent=2)
    print(f"Generated matilda.af ({os.path.getsize(output_path)} bytes)")


make_matilda()

print("Done. Generated 9 test-subject agent files + 1 Matilda specialist.")
