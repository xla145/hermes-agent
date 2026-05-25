from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout: float = 120.0
    max_retries: int = 2

    @classmethod
    def from_env(cls, model: str | None = None) -> "ModelConfig":
        timeout = os.getenv("HERMES_V1_TIMEOUT") or os.getenv("OPENAI_TIMEOUT")
        return cls(
            model=model or os.getenv("HERMES_V1_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
            base_url=os.getenv("HERMES_V1_BASE_URL") or os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("HERMES_V1_API_KEY") or os.getenv("OPENAI_API_KEY"),
            timeout=float(timeout) if timeout else 120.0,
        )


@dataclass
class CompressionConfig:
    max_approx_tokens: int = 80_000
    head_messages: int = 4
    tail_messages: int = 20
    max_tool_result_chars: int = 12_000
    summary_model_max_chars: int = 18_000


@dataclass
class SafetyConfig:
    command_timeout: float = 120.0
    max_result_chars: int = 20_000
    checkpoints_enabled: bool = True
    checkpoint_dir_name: str = ".v1-checkpoints"
    require_approval_for_dangerous_commands: bool = True


@dataclass
class AgentConfig:
    model: ModelConfig
    workspace_root: Path = field(default_factory=lambda: Path.cwd())
    session_id: str = "default"
    max_iterations: int = 20
    skills_dirs: list[Path] = field(default_factory=list)
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)

    @classmethod
    def from_env(cls, model: str | None = None, workspace_root: str | Path | None = None) -> "AgentConfig":
        return cls(
            model=ModelConfig.from_env(model),
            workspace_root=Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve(),
        )
