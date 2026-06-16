from __future__ import annotations

import json
from pathlib import Path

from .parser import read_structure_files


def build_mcp_manifest(path: str = ".", output: str = "structure/mcp_manifest.json") -> dict:
    root = Path(path)
    resources = []

    for label, content in read_structure_files(path):
        resources.append(
            {
                "uri": f"structure-rule://{label}",
                "name": label,
                "mimeType": "text/markdown",
                "description": f"Structure Rule file: {label}",
                "char_count": len(content),
            }
        )

    manifest = {
        "version": "0.2",
        "kind": "structure-rule-mcp-manifest",
        "root": str(root.resolve()),
        "resources": resources,
        "tools": [
            {
                "name": "structure_rule_summary",
                "description": "Return a compact project structure summary.",
            },
            {
                "name": "structure_rule_context_pack",
                "description": "Return a bounded context pack built from structure files.",
            },
        ],
    }

    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"output": str(output_path), "resources": len(resources), "tools": len(manifest["tools"])}
