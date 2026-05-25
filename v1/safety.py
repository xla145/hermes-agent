from __future__ import annotations

import re
import shutil
import time
from pathlib import Path


HARDLINE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\brm\s+(-[^\s]*\s+)*(/|/\*|/ \*)(\s|$)", "recursive delete of root filesystem"),
    (r"\brm\s+(-[^\s]*\s+)*(~|\$HOME)(/?|/\*)?(\s|$)", "recursive delete of home directory"),
    (r"\bmkfs(\.[a-z0-9]+)?\b", "format filesystem"),
    (r"\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*", "raw block device overwrite"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "fork bomb"),
    (r"\bkill\s+(-[^\s]+\s+)*-1\b", "kill all processes"),
    (r"(?:^|[;&|\n`]\s*)(?:sudo\s+)?(?:shutdown|reboot|halt|poweroff)\b", "shutdown or reboot"),
)

DANGEROUS_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\brm\s+(-[^\s]*r[^\s]*|-r|-R|--recursive)\b", "recursive delete"),
    (r"\bgit\s+reset\s+--hard\b", "hard git reset"),
    (r"\bgit\s+clean\s+(-[^\s]*f|--force)\b", "forced git clean"),
    (r"\bchmod\s+(-[^\s]*R[^\s]*|-R)\s+", "recursive chmod"),
    (r"\bchown\s+(-[^\s]*R[^\s]*|-R)\s+", "recursive chown"),
    (r"\bcurl\b[^\n|]*\|\s*(?:sudo\s+)?(?:sh|bash)\b", "curl piped to shell"),
    (r"\bwget\b[^\n|]*\|\s*(?:sudo\s+)?(?:sh|bash)\b", "wget piped to shell"),
    (r"\b(?:sudo\s+)?(?:rm|mv|cp|tee)\b[^\n]*(?:/etc/|/private/etc/|/dev/|~/.ssh|\$HOME/.ssh)", "sensitive system path write"),
)


def ensure_workspace_path(path: str | Path, root: Path) -> Path:
    root = root.resolve()
    target = Path(path)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes workspace: {path}") from exc
    return target


def detect_hardline_command(command: str) -> str | None:
    normalized = command.strip()
    for pattern, reason in HARDLINE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return reason
    return None


def detect_dangerous_command(command: str) -> str | None:
    hardline = detect_hardline_command(command)
    if hardline:
        return hardline
    normalized = command.strip()
    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return reason
    return None


def truncate_result(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"{text[:limit]}\n\n[truncated {omitted} chars]"


def create_checkpoint(path: Path, root: Path, checkpoint_dir_name: str = ".v1-checkpoints") -> str | None:
    if not path.exists() or not path.is_file():
        return None
    root = root.resolve()
    relative = path.resolve().relative_to(root)
    checkpoint_root = root / checkpoint_dir_name / str(int(time.time() * 1000))
    destination = checkpoint_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return str(destination.relative_to(root))
