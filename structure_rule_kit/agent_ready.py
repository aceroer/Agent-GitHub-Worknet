from __future__ import annotations

from pathlib import Path

from .parser import extract_section
from .reporting import issue
from .validator import validate_structure


UNSPECIFIED_MARKERS = ("not specified", "tbd", "todo")


def is_unspecified(value: str) -> bool:
    stripped = value.strip().lower()
    if not stripped:
        return True
    return any(marker in stripped for marker in UNSPECIFIED_MARKERS)


def _read(root: Path, relative: str) -> str:
    target = root / relative
    return target.read_text(encoding="utf-8") if target.exists() else ""


def check_agent_ready(path: str = ".") -> dict:
    root = Path(path)
    validation = validate_structure(path)
    missing: list[str] = []
    warnings: list[str] = []
    issues: list[dict] = []

    if validation["missing_files"]:
        for item in validation["missing_files"]:
            message = f"Missing required file: {item}"
            missing.append(message)
            issues.append(issue("blocked", message, item))
    if validation["empty_files"]:
        for item in validation["empty_files"]:
            message = f"Empty required file: {item}"
            missing.append(message)
            issues.append(issue("blocked", message, item))
    if validation["warnings"]:
        for item in validation["warnings"]:
            warnings.append(item)
            issues.append(issue("warning", item))

    plan = _read(root, "structure/project_plan.md")
    rules = _read(root, "structure/rules.md")
    metrics = _read(root, "structure/metrics.md")
    files = _read(root, "structure/important_files.md")
    status = _read(root, "structure/status.md")
    toolbox = _read(root, "structure/toolbox.md")

    required_sections = [
        ("project_plan.md", "Project Name", plan),
        ("project_plan.md", "Core Goal", plan),
        ("project_plan.md", "Current Stage", plan),
        ("project_plan.md", "Current Priority", plan),
        ("rules.md", "Things Not To Do", rules),
        ("metrics.md", "Definition of Done", metrics),
        ("metrics.md", "Required Checks", metrics),
        ("important_files.md", "Core Source Files", files),
        ("status.md", "Current Task", status),
        ("status.md", "Next Step", status),
    ]

    for filename, heading, content in required_sections:
        value = extract_section(content, heading)
        if is_unspecified(value):
            message = f"{filename}: `{heading}` is not specified."
            missing.append(message)
            issues.append(issue("blocked", message, f"structure/{filename}", heading))

    toolbox_sections = ["Build Commands", "Test Commands", "Useful Scripts"]
    if all(is_unspecified(extract_section(toolbox, section)) for section in toolbox_sections):
        message = "toolbox.md: no build, test, or useful script commands are specified."
        warnings.append(message)
        issues.append(issue("warning", message, "structure/toolbox.md"))

    status = "blocked" if missing else "warning" if warnings else "ready"

    return {
        "ready": not missing,
        "status": status,
        "missing": missing,
        "warnings": warnings,
        "issues": issues,
    }
