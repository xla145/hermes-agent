# Hermes Agent v1 Core

`v1/` is a compact, source-level extraction of Hermes Agent's core runtime ideas. It does not replace the main CLI, gateway, ACP adapter, TUI, web UI, cron, memory, or provider matrix.

## Included

- OpenAI-compatible Chat Completions model calls
- Multi-turn `Agent` loop with function/tool calls
- Minimal tool registry and tool-call guardrail
- Core development tools:
  - `read_file`
  - `write_file`
  - `search_text`
  - `bash`
- Workspace path safety, dangerous-command blocking, result truncation
- Lightweight write checkpoints under `.v1-checkpoints/`
- `SKILL.md` discovery/loading without inline shell expansion
- Session-scoped todo/plan store
- Long-task delegation through isolated child agents
- Context compression with head/tail preservation and middle summary

## Not included yet

- CLI entry points in `pyproject.toml`
- SQLite or JSONL session persistence
- Gateway/platform adapters
- MCP client
- Full checkpoint rollback UI/store
- Credential pool and OAuth refresh
- Multi-provider transports/fallback
- Browser/web/computer-use tools
- Cron and memory/session search

## Minimal usage

```python
from pathlib import Path
from v1 import Agent, AgentConfig, ModelConfig

config = AgentConfig(
    model=ModelConfig(
        model="gpt-4o-mini",
        api_key="...",
        base_url=None,
    ),
    workspace_root=Path.cwd(),
    skills_dirs=[Path("skills")],
)

agent = Agent(config)
print(agent.chat("Read README.md and summarize the project."))
```

Environment helper:

```python
from v1 import Agent, AgentConfig

agent = Agent(AgentConfig.from_env())
print(agent.chat("What files are in this project?"))
```

Set `HERMES_V1_MODEL`, `HERMES_V1_API_KEY`, `HERMES_V1_BASE_URL`, and optionally `HERMES_V1_TIMEOUT` for environment-based configuration. The OpenAI-compatible aliases `OPENAI_MODEL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_TIMEOUT` are also supported.

Prototype generation test:

```bash
OPENAI_API_KEY="..." \
OPENAI_MODEL="Minimax/Minimax-M2.5" \
OPENAI_BASE_URL="https://api.quchiai.com/v1" \
OPENAI_TIMEOUT="120" \
/Users/mac/xula/hermes-agent/.venv/bin/python v1/test_generate_prototype.py
```

The test reads `v1/source/需求结构化.md`, loads skills from `v1/skills`, and writes all generated design/prototype files inside `v1/`.
