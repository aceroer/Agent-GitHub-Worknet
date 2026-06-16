from __future__ import annotations

from pathlib import Path

from .summary import summarize_structure


def scaffold_skill(path: str = ".", output: str = "skills/project-structure") -> dict:
    root = Path(path)
    output_dir = root / output
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_path = output_dir / "SKILL.md"

    summary = summarize_structure(path)
    content = f"""# Project Structure Skill

Use this skill when working inside this repository.

## Purpose

Load the repository's Structure Rule files before making changes.

## Project Snapshot

- Project: {summary.get("Project", "Not specified yet.")}
- Current stage: {summary.get("Current stage", "Not specified yet.")}
- Current priority: {summary.get("Current priority", "Not specified yet.")}

## Required Reading

1. `STRUCTURE_RULE.md`
2. `structure/project_plan.md`
3. `structure/rules.md`
4. `structure/roadmap.md`
5. `structure/status.md`

## Workflow

1. Read `STRUCTURE_RULE.md`.
2. Read the current status and relevant structure files.
3. Keep changes scoped to the requested task.
4. Run relevant checks.
5. Update status or agent notes when project state meaningfully changes.
"""
    skill_path.write_text(content, encoding="utf-8")
    return {"output": str(skill_path)}
