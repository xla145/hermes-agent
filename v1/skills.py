from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .types import ToolContext

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous",
    "you are now",
    "disregard your",
    "forget your instructions",
    "new instructions:",
    "system prompt:",
    "<system>",
    "]]>",
)


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    content: str
    frontmatter: dict[str, Any]


class SkillManager:
    def __init__(self, skills_dirs: list[Path], session_id: str = "default"):
        self.skills_dirs = [Path(path).expanduser().resolve() for path in skills_dirs]
        self.session_id = session_id

    def list_skills(self) -> list[Skill]:
        skills: list[Skill] = []
        for root in self.skills_dirs:
            if not root.exists():
                continue
            for manifest in root.rglob("SKILL.md"):
                skill = self._load_manifest(manifest)
                if skill:
                    skills.append(skill)
        return sorted(skills, key=lambda item: item.name)

    def build_index_prompt(self) -> str:
        skills = self.list_skills()
        if not skills:
            return ""
        lines = ["Available skills. Invoke by asking for the skill name or using /skill-name:"]
        lines.extend(f"- {skill.name}: {skill.description}" for skill in skills)
        return "\n".join(lines)

    def load(self, name: str, instruction: str = "") -> str:
        normalized = normalize_skill_name(name)
        for skill in self.list_skills():
            if normalize_skill_name(skill.name) == normalized:
                if looks_injected(skill.content):
                    raise ValueError(f"skill {skill.name!r} failed basic injection checks")
                content = preprocess_skill_content(skill.content, skill.path.parent, self.session_id)
                suffix = f"\n\nUser instruction:\n{instruction}" if instruction else ""
                return f"# Loaded skill: {skill.name}\n\n{content}{suffix}"
        raise KeyError(f"skill not found: {name}")

    def _load_manifest(self, manifest: Path) -> Skill | None:
        try:
            raw = manifest.read_text(encoding="utf-8")
        except OSError:
            return None
        frontmatter, body = parse_frontmatter(raw)
        name = str(frontmatter.get("name") or manifest.parent.name).strip()
        description = str(frontmatter.get("description") or first_nonempty_line(body) or "No description").strip()
        return Skill(name=name, description=description, path=manifest, content=body.strip(), frontmatter=frontmatter)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content
    raw = content[4:end]
    body = content[end + 4:].lstrip("\n")
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data, body


def preprocess_skill_content(content: str, skill_dir: Path, session_id: str) -> str:
    return content.replace("${HERMES_SKILL_DIR}", str(skill_dir)).replace("${HERMES_SESSION_ID}", session_id)


def looks_injected(content: str) -> bool:
    lower = content.lower()
    return any(pattern in lower for pattern in INJECTION_PATTERNS)


def normalize_skill_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", name.strip().lower()).strip("-")


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped
    return ""


def skills_handler(args: dict[str, Any], context: ToolContext) -> str:
    action = str(args.get("action") or "list")
    manager = context.agent.skills
    if action == "list":
        return json.dumps({"skills": [{"name": s.name, "description": s.description, "path": str(s.path)} for s in manager.list_skills()]}, ensure_ascii=False)
    if action == "load":
        return manager.load(str(args.get("name") or ""), str(args.get("instruction") or ""))
    raise ValueError(f"unknown skill action: {action}")


SKILLS_SCHEMA = {
    "name": "skills",
    "description": "List or load local skills from SKILL.md manifests.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list", "load"], "default": "list"},
            "name": {"type": "string"},
            "instruction": {"type": "string"},
        },
    },
}
