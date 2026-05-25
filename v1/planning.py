from __future__ import annotations

import json
from typing import Any

from .types import ToolContext

VALID_STATUSES = {"pending", "in_progress", "completed", "cancelled"}


class TodoStore:
    def __init__(self):
        self._items: list[dict[str, str]] = []

    def write(self, todos: list[dict[str, Any]], merge: bool = False) -> list[dict[str, str]]:
        if not merge:
            self._items = [self._validate(item) for item in self._dedupe_by_id(todos)]
            return self.read()

        existing = {item["id"]: item for item in self._items}
        for raw in self._dedupe_by_id(todos):
            item_id = str(raw.get("id", "")).strip()
            if not item_id:
                continue
            if item_id in existing:
                if raw.get("content"):
                    existing[item_id]["content"] = str(raw["content"]).strip()
                if raw.get("status"):
                    status = str(raw["status"]).strip().lower()
                    if status in VALID_STATUSES:
                        existing[item_id]["status"] = status
            else:
                item = self._validate(raw)
                existing[item["id"]] = item
                self._items.append(item)

        seen: set[str] = set()
        rebuilt: list[dict[str, str]] = []
        for item in self._items:
            current = existing[item["id"]]
            if current["id"] not in seen:
                rebuilt.append(current)
                seen.add(current["id"])
        self._items = rebuilt
        return self.read()

    def read(self) -> list[dict[str, str]]:
        return [item.copy() for item in self._items]

    def format_for_injection(self) -> str | None:
        active = [item for item in self._items if item["status"] in {"pending", "in_progress"}]
        if not active:
            return None
        markers = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]", "cancelled": "[~]"}
        lines = ["Active plan/todo list:"]
        lines.extend(f"- {markers.get(item['status'], '[?]')} {item['id']}. {item['content']} ({item['status']})" for item in active)
        return "\n".join(lines)

    @staticmethod
    def _validate(item: dict[str, Any]) -> dict[str, str]:
        item_id = str(item.get("id") or "?").strip()
        content = str(item.get("content") or "(no description)").strip()
        status = str(item.get("status") or "pending").strip().lower()
        if status not in VALID_STATUSES:
            status = "pending"
        return {"id": item_id, "content": content, "status": status}

    @staticmethod
    def _dedupe_by_id(todos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        last_index: dict[str, int] = {}
        for index, item in enumerate(todos):
            item_id = str(item.get("id", "")).strip() or "?"
            last_index[item_id] = index
        return [todos[index] for index in sorted(last_index.values())]


def todo_handler(args: dict[str, Any], context: ToolContext) -> str:
    store = context.agent.todo_store
    if "todos" in args:
        items = store.write(args.get("todos") or [], bool(args.get("merge", False)))
    else:
        items = store.read()
    summary = {status: sum(1 for item in items if item["status"] == status) for status in VALID_STATUSES}
    summary["total"] = len(items)
    return json.dumps({"todos": items, "summary": summary}, ensure_ascii=False)


TODO_SCHEMA = {
    "name": "todo",
    "description": "Read or update the current session plan/todo list. Use for multi-step work and mark items completed immediately.",
    "parameters": {
        "type": "object",
        "properties": {
            "todos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "content": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled"]},
                    },
                    "required": ["id", "content", "status"],
                },
            },
            "merge": {"type": "boolean", "default": False},
        },
    },
}
