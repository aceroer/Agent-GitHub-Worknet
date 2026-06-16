from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


def append_verify_log(
    path: str = ".",
    command: str = "",
    result: str = "",
    notes: str = "",
    output: str = "structure/verification_log.md",
    run: bool = False,
    timeout: int = 120,
) -> dict:
    root = Path(path)
    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    exit_code = None
    stdout = ""
    stderr = ""
    actual_result = result.strip()

    if run and command.strip():
        completed = subprocess.run(
            command,
            cwd=root,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if not actual_result:
            actual_result = "pass" if exit_code == 0 else "fail"

    if output_path.exists():
        text = output_path.read_text(encoding="utf-8").rstrip()
    else:
        text = "# Verification Log"

    stamp = datetime.now().isoformat(timespec="seconds")
    entry = f"""## {stamp}

- Command: `{command.strip() or "Not specified."}`
- Result: {actual_result or "Not specified."}
- Exit code: {exit_code if exit_code is not None else "Not run."}
- Notes: {notes.strip() or "Not specified."}
"""
    if stdout:
        entry += f"\n### Stdout\n\n```text\n{stdout[-4000:]}\n```\n"
    if stderr:
        entry += f"\n### Stderr\n\n```text\n{stderr[-4000:]}\n```\n"
    output_path.write_text(text + "\n\n" + entry, encoding="utf-8")
    return {"output": str(output_path), "result": actual_result or "", "exit_code": exit_code, "ran": run}
