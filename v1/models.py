from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urljoin

from .config import ModelConfig
from .types import ModelResponse, ToolCall, Usage


class ModelError(Exception):
    pass


class ContextOverflowError(ModelError):
    pass


class RateLimitError(ModelError):
    pass


class ChatModel:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client: Any | None = None
        try:
            from openai import OpenAI
        except ModuleNotFoundError:
            return
        kwargs: dict[str, Any] = {}
        if config.api_key:
            kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        if config.timeout:
            kwargs["timeout"] = config.timeout
        self.client = OpenAI(**kwargs)

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> ModelResponse:
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                kwargs: dict[str, Any] = {
                    "model": self.config.model,
                    "messages": self._clean_messages(messages),
                }
                if tools:
                    kwargs["tools"] = [{"type": "function", "function": tool} for tool in tools]
                    kwargs["tool_choice"] = "auto"
                response = self._create_completion(kwargs)
                return self._normalize(response)
            except Exception as exc:
                last_error = exc
                classified = classify_model_error(exc)
                if classified == "context_overflow":
                    raise ContextOverflowError(str(exc)) from exc
                if attempt >= self.config.max_retries or classified not in {"rate_limit", "server_error", "timeout"}:
                    raise ModelError(str(exc)) from exc
                time.sleep(min(2 ** attempt, 8) + (attempt * 0.25))
        raise ModelError(str(last_error))

    def summarize(self, text: str, max_chars: int = 18_000) -> str:
        prompt = (
            "Summarize the following conversation segment for continuing an AI agent task. "
            "Preserve goals, decisions, tool results, file paths, errors, and unresolved work.\n\n"
            f"{text[:max_chars]}"
        )
        response = self.complete([
            {"role": "system", "content": "You summarize agent conversation context compactly and accurately."},
            {"role": "user", "content": prompt},
        ])
        return response.content or ""

    def _create_completion(self, kwargs: dict[str, Any]) -> Any:
        if self.client is not None:
            return self.client.chat.completions.create(**kwargs)
        if not self.config.base_url:
            raise ModelError("OPENAI_BASE_URL or HERMES_V1_BASE_URL is required when openai package is unavailable")
        if not self.config.api_key:
            raise ModelError("OPENAI_API_KEY or HERMES_V1_API_KEY is required")

        url = urljoin(self.config.base_url.rstrip("/") + "/", "chat/completions")
        payload = json.dumps(kwargs).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ModelError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise ModelError(str(exc.reason)) from exc

    @staticmethod
    def _clean_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        allowed = {"role", "content", "name", "tool_call_id", "tool_calls"}
        cleaned: list[dict[str, Any]] = []
        for message in messages:
            item = {k: v for k, v in message.items() if k in allowed and v is not None}
            if item.get("role") == "assistant" and item.get("tool_calls"):
                item["tool_calls"] = item["tool_calls"]
            cleaned.append(item)
        return cleaned

    @staticmethod
    def _normalize(response: Any) -> ModelResponse:
        if isinstance(response, dict):
            choice = response["choices"][0]
            message = choice.get("message") or {}
            tool_calls = []
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                tool_calls.append(ToolCall(id=call.get("id"), name=function.get("name", ""), arguments=function.get("arguments") or "{}"))
            raw_usage = response.get("usage") or {}
            usage = Usage(
                prompt_tokens=int(raw_usage.get("prompt_tokens") or 0),
                completion_tokens=int(raw_usage.get("completion_tokens") or 0),
                total_tokens=int(raw_usage.get("total_tokens") or 0),
            ) if raw_usage else None
            return ModelResponse(
                content=message.get("content"),
                tool_calls=tool_calls,
                finish_reason=choice.get("finish_reason") or "stop",
                usage=usage,
                raw=response,
            )

        choice = response.choices[0]
        message = choice.message
        tool_calls: list[ToolCall] = []
        for call in getattr(message, "tool_calls", None) or []:
            function = call.function
            tool_calls.append(ToolCall(id=call.id, name=function.name, arguments=function.arguments or "{}"))
        usage = None
        raw_usage = getattr(response, "usage", None)
        if raw_usage is not None:
            usage = Usage(
                prompt_tokens=getattr(raw_usage, "prompt_tokens", 0) or 0,
                completion_tokens=getattr(raw_usage, "completion_tokens", 0) or 0,
                total_tokens=getattr(raw_usage, "total_tokens", 0) or 0,
            )
        return ModelResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=getattr(choice, "finish_reason", "stop") or "stop",
            usage=usage,
            raw=response,
        )


def parse_tool_arguments(arguments: str) -> dict[str, Any]:
    try:
        value = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def classify_model_error(exc: Exception) -> str:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    if status == 429 or "rate limit" in text or "too many requests" in text:
        return "rate_limit"
    if status in {500, 502, 503, 504, 529} or "overloaded" in text:
        return "server_error"
    if status == 413 or "context length" in text or "maximum context" in text or "too many tokens" in text:
        return "context_overflow"
    if "timeout" in text or "timed out" in text:
        return "timeout"
    return "unknown"
