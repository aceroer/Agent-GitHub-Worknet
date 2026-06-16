from __future__ import annotations

from pathlib import Path

from .parser import extract_section


def summarize_structure(path: str = ".") -> dict:
    root = Path(path)
    plan = (root / "structure" / "project_plan.md").read_text(encoding="utf-8") if (root / "structure" / "project_plan.md").exists() else ""
    files = (root / "structure" / "important_files.md").read_text(encoding="utf-8") if (root / "structure" / "important_files.md").exists() else ""
    rules = (root / "structure" / "rules.md").read_text(encoding="utf-8") if (root / "structure" / "rules.md").exists() else ""
    metrics = (root / "structure" / "metrics.md").read_text(encoding="utf-8") if (root / "structure" / "metrics.md").exists() else ""

    return {
        "Project": extract_section(plan, "Project Name") or "Not specified yet.",
        "Current stage": extract_section(plan, "Current Stage") or "Not specified yet.",
        "Current priority": extract_section(plan, "Current Priority") or "Not specified yet.",
        "Important files": extract_section(files, "Core Source Files") or "Not specified yet.",
        "Allowed actions": extract_section(rules, "General Rules") or "Not specified yet.",
        "Forbidden actions": extract_section(rules, "Things Not To Do") or "Not specified yet.",
        "Completion criteria": extract_section(metrics, "Definition of Done") or "Not specified yet.",
    }
