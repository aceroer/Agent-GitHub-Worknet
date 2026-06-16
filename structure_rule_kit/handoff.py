from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .parser import extract_section
from .summary import summarize_structure


def _read(root: Path, relative: str) -> str:
    target = root / relative
    return target.read_text(encoding="utf-8") if target.exists() else ""


def build_handoff_pack(path: str = ".", task: str = "", output: str = "STRUCTURE_HANDOFF.md") -> dict:
    root = Path(path)
    summary = summarize_structure(path)
    status = _read(root, "structure/status.md")
    toolbox = _read(root, "structure/toolbox.md")
    rules = _read(root, "structure/rules.md")
    metrics = _read(root, "structure/metrics.md")
    files = _read(root, "structure/important_files.md")

    chunks = [
        "# Structure Handoff",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Task",
        "",
        task.strip() or "Not specified.",
        "",
        "## Project Snapshot",
        "",
    ]
    for key, value in summary.items():
        chunks.append(f"- {key}: {str(value).strip()}")
    chunks.extend(
        [
            "",
            "## Current Status",
            "",
            extract_section(status, "Current Task") or "Not specified.",
            "",
            "## Next Step",
            "",
            extract_section(status, "Next Step") or "Not specified.",
            "",
            "## Required Reading",
            "",
            "1. `STRUCTURE_RULE.md`",
            "2. `structure/project_plan.md`",
            "3. `structure/rules.md`",
            "4. `structure/roadmap.md`",
            "5. `structure/status.md`",
            "",
            "## Important Files",
            "",
            extract_section(files, "Core Source Files") or "Not specified.",
            "",
            "## Forbidden Actions",
            "",
            extract_section(rules, "Things Not To Do") or "Not specified.",
            "",
            "## Useful Commands",
            "",
            extract_section(toolbox, "Test Commands")
            or extract_section(toolbox, "Build Commands")
            or extract_section(toolbox, "Useful Scripts")
            or "Not specified.",
            "",
            "## Completion Criteria",
            "",
            extract_section(metrics, "Definition of Done") or "Not specified.",
            "",
            "## Known Issues",
            "",
            extract_section(status, "Known Issues") or "Not specified.",
            "",
            "## Handoff Notes",
            "",
            "Continue from this packet, then refresh `structure/status.md` after meaningful progress.",
        ]
    )

    output_path = root / output
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return {"output": str(output_path)}
