from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .parser import append_section_entry, replace_section


def update_status(
    path: str = ".",
    current: str = "",
    done: str = "",
    next_step: str = "",
    issue: str = "",
    decision: str = "",
) -> dict:
    root = Path(path)
    status_path = root / "structure" / "status.md"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    text = status_path.read_text(encoding="utf-8") if status_path.exists() else "# Status\n"

    if current:
        text = replace_section(text, "Current Task", current)
    if done:
        text = replace_section(text, "Last Completed Task", done)
    if next_step:
        text = replace_section(text, "Next Step", next_step)
    if issue:
        text = append_section_entry(text, "Known Issues", f"- {issue}")
    if decision:
        text = append_section_entry(text, "Recent Decisions", f"- {decision}")

    entries = []
    if current:
        entries.append(f"- Current: {current}")
    if done:
        entries.append(f"- Done: {done}")
    if next_step:
        entries.append(f"- Next: {next_step}")
    if issue:
        entries.append(f"- Issue: {issue}")
    if decision:
        entries.append(f"- Decision: {decision}")
    if entries:
        stamp = datetime.now().isoformat(timespec="seconds")
        text = append_section_entry(text, "Activity Log", f"### {stamp}\n\n" + "\n".join(entries))

    status_path.write_text(text, encoding="utf-8")
    return {"output": str(status_path), "updated": bool(entries)}
