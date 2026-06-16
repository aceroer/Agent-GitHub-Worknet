from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value.lower())
    return "-".join(words[:8]) or "task"


def create_agent_task(
    path: str = ".",
    title: str = "",
    goal: str = "",
    scope: str = "",
    forbidden: str = "",
    checks: str = "",
    output_dir: str = "structure/tasks",
) -> dict:
    root = Path(path)
    tasks_dir = root / output_dir
    tasks_dir.mkdir(parents=True, exist_ok=True)

    safe_title = title.strip() or "Untitled task"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = tasks_dir / f"{stamp}-{slugify(safe_title)}.md"

    content = f"""# Agent Task: {safe_title}

## Created

{datetime.now().isoformat(timespec="seconds")}

## Goal

{goal.strip() or "Not specified."}

## Scope

{scope.strip() or "Not specified."}

## Forbidden Actions

{forbidden.strip() or "Follow `structure/rules.md`."}

## Required Checks

{checks.strip() or "Follow `structure/metrics.md`."}

## Result

Not completed yet.

## Notes

Not specified.
"""
    output_path.write_text(content, encoding="utf-8")
    return {"output": str(output_path)}
