from __future__ import annotations

from dataclasses import replace
from typing import Any

from .types import ToolContext


class LongTaskRunner:
    def __init__(self, parent_agent: Any):
        self.parent_agent = parent_agent

    def run(self, prompt: str) -> str:
        from .agent import Agent
        child_config = replace(self.parent_agent.config, session_id=f"{self.parent_agent.config.session_id}:child")
        child = Agent(child_config, include_delegate=False)
        result = child.run(
            "You are a child agent working on an isolated long task. "
            "Return a concise summary with findings, changed files, and unresolved issues.\n\n"
            f"Task:\n{prompt}"
        )
        return result.final_response


def delegate_handler(args: dict[str, Any], context: ToolContext) -> str:
    prompt = str(args.get("prompt") or args.get("task") or "")
    if not prompt:
        raise ValueError("delegate requires prompt")
    return context.agent.long_tasks.run(prompt)


DELEGATE_SCHEMA = {
    "name": "delegate",
    "description": "Run an isolated child Agent for a long subtask and return its summary.",
    "parameters": {
        "type": "object",
        "properties": {"prompt": {"type": "string", "description": "The subtask prompt for the child agent."}},
        "required": ["prompt"],
    },
}
