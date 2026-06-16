from __future__ import annotations

import json
from pathlib import Path

from .parser import read_structure_files
from .summary import summarize_structure


def _trim(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 24)].rstrip() + "\n\n[truncated]"


def build_context_pack(
    path: str = ".",
    output: str = "STRUCTURE_CONTEXT_PACK.md",
    max_chars_per_file: int = 2400,
    json_output: bool = False,
) -> dict:
    root = Path(path)
    summary = summarize_structure(path)
    files = [
        {
            "path": label,
            "content": _trim(content, max_chars_per_file),
            "original_char_count": len(content),
        }
        for label, content in read_structure_files(path)
    ]

    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if json_output:
        payload = {
            "version": "0.2",
            "kind": "structure-rule-context-pack",
            "root": str(root.resolve()),
            "summary": summary,
            "files": files,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        chunks = ["# Structure Context Pack", "", "## Summary", ""]
        for key, value in summary.items():
            chunks.append(f"### {key}")
            chunks.append("")
            chunks.append(str(value).strip())
            chunks.append("")
        chunks.append("## Structure Files")
        chunks.append("")
        for item in files:
            chunks.append(f"### {item['path']}")
            chunks.append("")
            chunks.append(item["content"])
            chunks.append("")
        output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")

    return {"output": str(output_path), "files": len(files), "json": json_output}
