from __future__ import annotations

from pathlib import Path

from .agent_ready import is_unspecified
from .parser import extract_section
from .reporting import issue


def audit_toolbox(path: str = ".") -> dict:
    root = Path(path)
    toolbox_path = root / "structure" / "toolbox.md"
    if not toolbox_path.exists():
        message = "structure/toolbox.md"
        return {
            "ok": False,
            "status": "blocked",
            "missing": [message],
            "warnings": [],
            "issues": [issue("blocked", "Missing toolbox file.", message)],
        }

    text = toolbox_path.read_text(encoding="utf-8")
    missing: list[str] = []
    warnings: list[str] = []
    issues: list[dict] = []

    required = [
        "Package Manager",
        "Build Commands",
        "Test Commands",
        "Useful Scripts",
    ]
    optional = [
        "Lint Commands",
        "Format Commands",
        "External Tools",
    ]

    for section in required:
        if is_unspecified(extract_section(text, section)):
            message = f"toolbox.md: `{section}` is not specified."
            missing.append(message)
            issues.append(issue("blocked", message, "structure/toolbox.md", section))

    for section in optional:
        if is_unspecified(extract_section(text, section)):
            message = f"toolbox.md: `{section}` is not specified."
            warnings.append(message)
            issues.append(issue("warning", message, "structure/toolbox.md", section))

    status = "blocked" if missing else "warning" if warnings else "ready"
    return {"ok": not missing, "status": status, "missing": missing, "warnings": warnings, "issues": issues}
