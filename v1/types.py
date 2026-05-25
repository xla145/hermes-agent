from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping


Message = dict[str, Any]
ToolHandler = Callable[[dict[str, Any], "ToolContext"], str]


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0


@dataclass
class ToolCall:
    id: str | None
    name: str
    arguments: str


@dataclass
class ModelResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Usage | None = None
    raw: Any = None


@dataclass
class AgentResult:
    final_response: str
    messages: list[Message]
    iterations: int
    compressed: bool = False


@dataclass
class CommandResult:
    command: str
    exit_code: int | None
    output: str
    timed_out: bool = False


@dataclass
class ToolContext:
    workspace_root: Path
    agent: Any = None
    session_id: str = "default"
    max_result_chars: int = 20_000


@dataclass
class ToolSpec:
    name: str
    schema: dict[str, Any]
    handler: ToolHandler
    mutating: bool = False


def ensure_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
