from __future__ import annotations

from pathlib import Path

from .templates import ROOT_TEMPLATE, STRUCTURE_TEMPLATES


def write_if_allowed(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return True


def init_structure(path: str = ".", force: bool = False, minimal: bool = False) -> dict:
    """
    Create structure rule files in a project.
    """
    root = Path(path)
    created: list[str] = []
    skipped: list[str] = []

    root_file = root / "STRUCTURE_RULE.md"
    if write_if_allowed(root_file, ROOT_TEMPLATE, force):
        created.append(str(root_file))
    else:
        skipped.append(str(root_file))

    structure_dir = root / "structure"
    structure_dir.mkdir(parents=True, exist_ok=True)

    templates = STRUCTURE_TEMPLATES
    if minimal:
        keep = {"project_plan.md", "rules.md", "roadmap.md", "status.md"}
        templates = {name: content for name, content in STRUCTURE_TEMPLATES.items() if name in keep}

    for name, content in templates.items():
        target = structure_dir / name
        if write_if_allowed(target, content, force):
            created.append(str(target))
        else:
            skipped.append(str(target))

    return {"created": created, "skipped": skipped}
