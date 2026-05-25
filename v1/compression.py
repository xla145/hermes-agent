from __future__ import annotations

import json
from typing import Any

from .config import CompressionConfig
from .models import ChatModel, ModelError
from .safety import truncate_result

SUMMARY_PREFIX = "[Compressed conversation summary]"


class ContextCompressor:
    def __init__(self, config: CompressionConfig):
        self.config = config

    def approx_tokens(self, messages: list[dict[str, Any]]) -> int:
        return sum(max(1, len(json.dumps(message, ensure_ascii=False, default=str)) // 4) for message in messages)

    def maybe_compress(self, messages: list[dict[str, Any]], model: ChatModel, focus: str | None = None) -> tuple[list[dict[str, Any]], bool]:
        if self.approx_tokens(messages) <= self.config.max_approx_tokens:
            return messages, False
        if len(messages) <= self.config.head_messages + self.config.tail_messages + 2:
            return self._prune_tool_results(messages), True
        return self.compress(messages, model, focus), True

    def compress(self, messages: list[dict[str, Any]], model: ChatModel, focus: str | None = None) -> list[dict[str, Any]]:
        head = messages[: self.config.head_messages]
        middle = messages[self.config.head_messages: -self.config.tail_messages]
        tail = messages[-self.config.tail_messages:]
        middle_text = "\n".join(format_message(message) for message in self._prune_tool_results(middle))
        if focus:
            middle_text = f"Focus topic: {focus}\n\n{middle_text}"
        try:
            summary = model.summarize(middle_text, self.config.summary_model_max_chars)
        except ModelError:
            summary = truncate_result(middle_text, self.config.summary_model_max_chars)
        summary_message = {"role": "system", "content": f"{SUMMARY_PREFIX}\n{summary}"}
        return head + [summary_message] + self._prune_tool_results(tail)

    def _prune_tool_results(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pruned: list[dict[str, Any]] = []
        for message in messages:
            item = dict(message)
            if item.get("role") == "tool" and isinstance(item.get("content"), str):
                item["content"] = truncate_result(item["content"], self.config.max_tool_result_chars)
            pruned.append(item)
        return pruned


def format_message(message: dict[str, Any]) -> str:
    role = message.get("role", "unknown")
    content = message.get("content", "")
    if message.get("tool_calls"):
        content = f"{content}\nTool calls: {message['tool_calls']}"
    return f"{role}: {content}"
