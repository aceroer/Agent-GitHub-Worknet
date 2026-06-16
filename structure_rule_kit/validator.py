from __future__ import annotations

from pathlib import Path

from .templates import REQUIRED_STRUCTURE_FILES


def has_title(text: str) -> bool:
    return any(line.startswith("# ") for line in text.splitlines())


def has_section(text: str) -> bool:
    return any(line.startswith("## ") for line in text.splitlines())


def validate_file(path: Path, allow_todo: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        errors.append(f"Missing file: {path}")
        return errors, warnings
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        errors.append(f"Empty file: {path}")
        return errors, warnings
    if not has_title(text):
        warnings.append(f"Missing title line: {path}")
    if not has_section(text):
        warnings.append(f"Missing section heading: {path}")
    if not allow_todo and "TODO" in text:
        warnings.append(f"Contains unresolved TODO: {path}")
    return errors, warnings


def validate_structure(path: str = ".", allow_todo: bool = False) -> dict:
    """
    Validate required structure files.
    Return validation report.
    """
    root = Path(path)
    missing_files: list[str] = []
    empty_files: list[str] = []
    warnings: list[str] = []

    root_file = root / "STRUCTURE_RULE.md"
    errors, file_warnings = validate_file(root_file, allow_todo=allow_todo)
    for error in errors:
        if "Missing file" in error:
            missing_files.append(str(root_file))
        if "Empty file" in error:
            empty_files.append(str(root_file))
    warnings.extend(file_warnings)

    structure_dir = root / "structure"
    if not structure_dir.exists():
        missing_files.append(str(structure_dir))
    else:
        for name in REQUIRED_STRUCTURE_FILES:
            target = structure_dir / name
            errors, file_warnings = validate_file(target, allow_todo=allow_todo)
            for error in errors:
                if "Missing file" in error:
                    missing_files.append(str(target))
                if "Empty file" in error:
                    empty_files.append(str(target))
            warnings.extend(file_warnings)

    return {
        "ok": not missing_files and not empty_files and not warnings,
        "missing_files": missing_files,
        "empty_files": empty_files,
        "warnings": warnings,
    }
