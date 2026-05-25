from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .dev_tools import BASH_SCHEMA, READ_FILE_SCHEMA, SEARCH_TEXT_SCHEMA, WRITE_FILE_SCHEMA, bash_handler, read_file_handler, search_text_handler, write_file_handler
from .planning import TODO_SCHEMA, todo_handler
from .skills import SKILLS_SCHEMA, skills_handler
from .types import ToolContext, ToolHandler, ToolSpec


@dataclass
class ToolGuardrail:
    exact_failure_warn_after: int = 2
    exact_failure_block_after: int = 5
    seen_failures: dict[str, int] = field(default_factory=dict)

    def observe(self, name: str, args: dict[str, Any], result: str) -> str | None:
        failed = is_failed_result(result)
        if not failed:
            return None
        signature = self._signature(name, args)
        count = self.seen_failures.get(signature, 0) + 1
        self.seen_failures[signature] = count
        if count >= self.exact_failure_block_after:
            return f"blocked repeated failing tool call: {name} failed {count} times with same arguments"
        if count >= self.exact_failure_warn_after:
            return f"warning: repeated failing tool call: {name} failed {count} times with same arguments"
        return None

    @staticmethod
    def _signature(name: str, args: dict[str, Any]) -> str:
        raw = json.dumps(args, sort_keys=True, ensure_ascii=False, default=str)
        return f"{name}:{hashlib.sha256(raw.encode()).hexdigest()}"


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, name: str, schema: dict[str, Any], handler: ToolHandler, *, mutating: bool = False) -> None:
        self._tools[name] = ToolSpec(name=name, schema=schema, handler=handler, mutating=mutating)

    def definitions(self) -> list[dict[str, Any]]:
        return [spec.schema for spec in self._tools.values()]

    def dispatch(self, name: str, args: dict[str, Any], context: ToolContext) -> str:
        spec = self._tools.get(name)
        if spec is None:
            return json.dumps({"error": f"unknown tool: {name}"})
        try:
            result = spec.handler(args, context)
        except Exception as exc:
            return json.dumps({"error": str(exc), "tool": name}, ensure_ascii=False)
        return result


def create_default_registry(include_delegate: bool = True) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("read_file", READ_FILE_SCHEMA, read_file_handler)
    registry.register("write_file", WRITE_FILE_SCHEMA, write_file_handler, mutating=True)
    registry.register("search_text", SEARCH_TEXT_SCHEMA, search_text_handler)
    registry.register("bash", BASH_SCHEMA, bash_handler, mutating=True)
    registry.register("todo", TODO_SCHEMA, todo_handler, mutating=True)
    registry.register("skills", SKILLS_SCHEMA, skills_handler)
    if include_delegate:
        from .long_tasks import DELEGATE_SCHEMA, delegate_handler
        registry.register("delegate", DELEGATE_SCHEMA, delegate_handler, mutating=True)
    return registry


def is_failed_result(result: str) -> bool:
    lower = result[:500].lower()
    return '"error"' in lower or '"exit_code": 1' in lower or lower.startswith("error")
