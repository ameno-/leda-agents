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

print("Done. Generated 9 agent files.")
