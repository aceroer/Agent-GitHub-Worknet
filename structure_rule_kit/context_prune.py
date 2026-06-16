from __future__ import annotations

import json
from pathlib import Path

from .parser import read_structure_files
from .summary import summarize_structure


PRIORITY = {
    "STRUCTURE_RULE.md": 100,
    "structure/status.md": 95,
    "structure/project_plan.md": 90,
    "structure/rules.md": 85,
    "structure/metrics.md": 80,
    "structure/important_files.md": 75,
    "structure/toolbox.md": 70,
    "structure/roadmap.md": 65,
    "structure/action_protocol.md": 60,
    "structure/agent_notes.md": 50,
}


def _fit(text: str, budget: int) -> str:
    if len(text) <= budget:
        return text
    if budget <= 24:
        return text[:budget]
    return text[: budget - 24].rstrip() + "\n\n[truncated]"


def build_context_prune(
    path: str = ".",
    output: str = "STRUCTURE_CONTEXT_PRUNED.md",
    budget: int = 8000,
    json_output: bool = False,
) -> dict:
    root = Path(path)
    summary = summarize_structure(path)
    files = sorted(read_structure_files(path), key=lambda item: (-PRIORITY.get(item[0], 0), item[0]))

    prefix = ["# Structure Context Pruned", "", f"Budget: {budget}", "", "## Summary", ""]
    for key, value in summary.items():
        prefix.append(f"- {key}: {str(value).strip()}")
    prefix.append("")

    selected = []
    prefix_text = "\n".join(prefix)
    remaining = max(0, budget - len(prefix_text) - 1)
    for label, content in files:
        if remaining <= 0:
            break
        header = f"## {label}\n\n"
        available = remaining - len(header) - 2
        if available <= 0:
            break
        fitted = _fit(content.strip(), available)
        selected.append({"path": label, "content": fitted, "original_char_count": len(content)})
        remaining -= len(header) + len(fitted) + 2

    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if json_output:
        payload = {
            "version": "0.2",
            "kind": "structure-rule-context-pruned",
            "budget": budget,
            "used_chars": budget - remaining,
            "summary": summary,
            "files": selected,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        chunks = prefix[:]
        for item in selected:
            chunks.append(f"## {item['path']}")
            chunks.append("")
            chunks.append(item["content"])
            chunks.append("")
        output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")

    return {"output": str(output_path), "files": len(selected), "used_chars": budget - remaining}
