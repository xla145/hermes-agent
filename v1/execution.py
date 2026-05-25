from __future__ import annotations

import subprocess
from pathlib import Path

from .safety import detect_dangerous_command, truncate_result
from .types import CommandResult


class ExecutionEnvironment:
    def __init__(self, root: Path, max_result_chars: int = 20_000):
        self.root = root.resolve()
        self.cwd = self.root
        self.max_result_chars = max_result_chars

    def run(
        self,
        command: str,
        timeout: float = 120.0,
        *,
        require_approval_for_dangerous: bool = True,
    ) -> CommandResult:
        reason = detect_dangerous_command(command)
        if reason and require_approval_for_dangerous:
            raise PermissionError(f"dangerous command blocked: {reason}")

        try:
            completed = subprocess.run(
                command,
                cwd=self.cwd,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
            output = truncate_result(completed.stdout or "", self.max_result_chars)
            return CommandResult(command=command, exit_code=completed.returncode, output=output)
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            output = truncate_result(output, self.max_result_chars)
            return CommandResult(command=command, exit_code=None, output=output, timed_out=True)
