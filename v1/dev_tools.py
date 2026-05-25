from __future__ import annotations

import json
from pathlib import Path

from .safety import create_checkpoint, ensure_workspace_path, truncate_result
from .types import ToolContext


def read_file_handler(args: dict, context: ToolContext) -> str:
    path = ensure_workspace_path(args.get("path", ""), context.workspace_root)
    offset = max(0, int(args.get("offset", 0) or 0))
    limit = int(args.get("limit", 2000) or 2000)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    selected = lines[offset: offset + limit]
    numbered = "\n".join(f"{offset + index + 1}\t{line}" for index, line in enumerate(selected))
    return truncate_result(numbered, context.max_result_chars)


def write_file_handler(args: dict, context: ToolContext) -> str:
    path = ensure_workspace_path(args.get("path", ""), context.workspace_root)
    content = str(args.get("content", ""))
    checkpoint = None
    if context.agent.config.safety.checkpoints_enabled:
        checkpoint = create_checkpoint(path, context.workspace_root, context.agent.config.safety.checkpoint_dir_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return json.dumps({"ok": True, "path": str(path.relative_to(context.workspace_root)), "checkpoint": checkpoint}, ensure_ascii=False)


def search_text_handler(args: dict, context: ToolContext) -> str:
    query = str(args.get("query", ""))
    if not query:
        return json.dumps({"matches": []})
    base = ensure_workspace_path(args.get("path") or ".", context.workspace_root)
    max_matches = int(args.get("max_matches", 100) or 100)
    files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file() and _is_text_candidate(p)]
    matches: list[dict[str, object]] = []
    for file_path in files:
        try:
            for line_no, line in enumerate(file_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if query in line:
                    matches.append({"path": str(file_path.relative_to(context.workspace_root)), "line": line_no, "text": line[:500]})
                    if len(matches) >= max_matches:
                        return json.dumps({"matches": matches}, ensure_ascii=False)
        except OSError:
            continue
    return json.dumps({"matches": matches}, ensure_ascii=False)


def bash_handler(args: dict, context: ToolContext) -> str:
    command = str(args.get("command", ""))
    timeout = float(args.get("timeout") or context.agent.config.safety.command_timeout)
    result = context.agent.execution.run(
        command,
        timeout=timeout,
        require_approval_for_dangerous=context.agent.config.safety.require_approval_for_dangerous_commands,
    )
    return json.dumps({
        "command": result.command,
        "exit_code": result.exit_code,
        "output": result.output,
        "timed_out": result.timed_out,
    }, ensure_ascii=False)


def _is_text_candidate(path: Path) -> bool:
    if any(part in {".git", "node_modules", "__pycache__", ".v1-checkpoints"} for part in path.parts):
        return False
    return path.stat().st_size <= 2_000_000


READ_FILE_SCHEMA = {
    "name": "read_file",
    "description": "Read a UTF-8 text file inside the workspace with line numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "offset": {"type": "integer", "default": 0},
            "limit": {"type": "integer", "default": 2000},
        },
        "required": ["path"],
    },
}

WRITE_FILE_SCHEMA = {
    "name": "write_file",
    "description": "Write a UTF-8 text file inside the workspace. Existing files are checkpointed first when enabled.",
    "parameters": {
        "type": "object",
        "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        "required": ["path", "content"],
    },
}

SEARCH_TEXT_SCHEMA = {
    "name": "search_text",
    "description": "Search for an exact text query in workspace files.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "path": {"type": "string", "default": "."},
            "max_matches": {"type": "integer", "default": 100},
        },
        "required": ["query"],
    },
}

BASH_SCHEMA = {
    "name": "bash",
    "description": "Run a shell command in the workspace with timeout and dangerous-command blocking.",
    "parameters": {
        "type": "object",
        "properties": {"command": {"type": "string"}, "timeout": {"type": "number", "default": 120}},
        "required": ["command"],
    },
}
