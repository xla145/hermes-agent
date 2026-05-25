from __future__ import annotations

import json
from typing import Any

from .compression import ContextCompressor
from .config import AgentConfig
from .execution import ExecutionEnvironment
from .long_tasks import LongTaskRunner
from .models import ChatModel, ContextOverflowError, parse_tool_arguments
from .planning import TodoStore
from .prompts import build_system_prompt
from .skills import SkillManager
from .tools import ToolGuardrail, ToolRegistry, create_default_registry
from .types import AgentResult, Message, ToolContext


class Agent:
    def __init__(self, config: AgentConfig, *, include_delegate: bool = True, registry: ToolRegistry | None = None):
        self.config = config
        self.config.workspace_root = self.config.workspace_root.resolve()
        self.model = ChatModel(config.model)
        self.messages: list[Message] = []
        self.todo_store = TodoStore()
        self.skills = SkillManager(config.skills_dirs, config.session_id)
        self.compressor = ContextCompressor(config.compression)
        self.execution = ExecutionEnvironment(config.workspace_root, config.safety.max_result_chars)
        self.long_tasks = LongTaskRunner(self)
        self.registry = registry or create_default_registry(include_delegate=include_delegate)
        self.guardrail = ToolGuardrail()

    def chat(self, message: str) -> str:
        return self.run(message).final_response

    def reset(self) -> None:
        self.messages.clear()
        self.todo_store = TodoStore()
        self.guardrail = ToolGuardrail()

    def run(self, message: str, *, system_message: str | None = None) -> AgentResult:
        self.messages.append({"role": "user", "content": message})
        compressed = False
        final_response = ""

        for iteration in range(1, self.config.max_iterations + 1):
            system = {"role": "system", "content": build_system_prompt(self.skills, self.todo_store, system_message)}
            request_messages = [system] + self.messages
            request_messages, did_compress = self.compressor.maybe_compress(request_messages, self.model, focus=message)
            compressed = compressed or did_compress
            if did_compress:
                self.messages = [m for m in request_messages if m.get("role") != "system"]

            try:
                response = self.model.complete(request_messages, self.registry.definitions())
            except ContextOverflowError:
                self.messages, _ = self.compressor.compress(self.messages, self.model, focus=message), True
                compressed = True
                continue

            assistant_message = self._assistant_message(response.content, response.tool_calls)
            self.messages.append(assistant_message)

            if not response.tool_calls:
                final_response = response.content or ""
                return AgentResult(final_response=final_response, messages=self.messages.copy(), iterations=iteration, compressed=compressed)

            for tool_call in response.tool_calls:
                args = parse_tool_arguments(tool_call.arguments)
                context = ToolContext(
                    workspace_root=self.config.workspace_root,
                    agent=self,
                    session_id=self.config.session_id,
                    max_result_chars=self.config.safety.max_result_chars,
                )
                result = self.registry.dispatch(tool_call.name, args, context)
                guardrail_message = self.guardrail.observe(tool_call.name, args, result)
                if guardrail_message:
                    result = f"{result}\n\n{guardrail_message}"
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id or tool_call.name,
                    "name": tool_call.name,
                    "content": result,
                })

        final_response = final_response or "Max iterations reached before a final response."
        return AgentResult(final_response=final_response, messages=self.messages.copy(), iterations=self.config.max_iterations, compressed=compressed)

    @staticmethod
    def _assistant_message(content: str | None, tool_calls: list[Any]) -> Message:
        message: Message = {"role": "assistant", "content": content or ""}
        if tool_calls:
            message["tool_calls"] = [
                {
                    "id": call.id or call.name,
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.arguments or json.dumps({})},
                }
                for call in tool_calls
            ]
        return message
