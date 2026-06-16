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


def replace_section(text: str, heading: str, new_content: str) -> str:
    lines = text.splitlines()
    marker = f"## {heading}"
    start = None
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start = index
            break

    replacement = [marker, "", new_content.strip()]
    if start is None:
        if text.strip():
            return text.rstrip() + "\n\n" + "\n".join(replacement) + "\n"
        return "\n".join(replacement) + "\n"

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    updated = lines[:start] + replacement + lines[end:]
    return "\n".join(updated).rstrip() + "\n"


def append_section_entry(text: str, heading: str, entry: str) -> str:
    current = extract_section(text, heading)
    if current:
        new_content = current.rstrip() + "\n\n" + entry.strip()
    else:
        new_content = entry.strip()
    return replace_section(text, heading, new_content)
