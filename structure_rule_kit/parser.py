from __future__ import annotations

from pathlib import Path

from .templates import REQUIRED_STRUCTURE_FILES


def read_structure_files(path: str = ".") -> list[tuple[str, str]]:
    root = Path(path)
    files = [("STRUCTURE_RULE.md", root / "STRUCTURE_RULE.md")]
    files.extend((f"structure/{name}", root / "structure" / name) for name in REQUIRED_STRUCTURE_FILES)
    result: list[tuple[str, str]] = []
    for label, file_path in files:
        if file_path.exists():
            result.append((label, file_path.read_text(encoding="utf-8")))
    return result


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = index + 1
            break
    if start is None:
        return ""
    collected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()
