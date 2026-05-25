from __future__ import annotations

from .planning import TodoStore
from .skills import SkillManager


def build_system_prompt(skills: SkillManager, todo_store: TodoStore, extra: str | None = None) -> str:
    parts = [
        "You are Hermes v1, a compact coding agent.",
        "Work in small safe steps. Use tools when you need current files, command output, skills, planning, or long-task delegation.",
        "Before multi-step implementation, keep the todo list current. Mark tasks completed immediately.",
        "Never write outside the workspace. Dangerous shell commands are blocked.",
    ]
    skill_index = skills.build_index_prompt()
    if skill_index:
        parts.append(skill_index)
    todo_text = todo_store.format_for_injection()
    if todo_text:
        parts.append(todo_text)
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)
