from __future__ import annotations

import json
import re
from pathlib import Path

from .parser import read_structure_files


WORD_RE = re.compile(r"[A-Za-z0-9_\-]+")


def split_sections(content: str) -> list[dict]:
    sections: list[dict] = []
    current_title = "Document"
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append({"title": current_title, "content": "\n".join(current_lines).strip()})
            current_title = line.lstrip("#").strip() or "Untitled"
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or not sections:
        sections.append({"title": current_title, "content": "\n".join(current_lines).strip()})

    return [section for section in sections if section["content"] or section["title"]]


def extract_keywords(text: str, limit: int = 16) -> list[str]:
    counts: dict[str, int] = {}
    for raw_word in WORD_RE.findall(text):
        word = raw_word.lower()
        if len(word) < 3:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def build_rag_index(path: str = ".", output: str = "structure/rag_index.json") -> dict:
    root = Path(path)
    documents = []

    for label, content in read_structure_files(path):
        documents.append(
            {
                "id": label.replace("/", "__"),
                "path": label,
                "title": label,
                "char_count": len(content),
                "keywords": extract_keywords(content),
                "sections": split_sections(content),
            }
        )

    index = {
        "version": "0.2",
        "kind": "structure-rule-rag-index",
        "root": str(root.resolve()),
        "documents": documents,
    }

    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return {"output": str(output_path), "documents": len(documents)}
