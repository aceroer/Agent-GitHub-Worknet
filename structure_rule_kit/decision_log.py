from __future__ import annotations

from datetime import datetime
from pathlib import Path


def append_decision_log(
    path: str = ".",
    decision: str = "",
    rationale: str = "",
    impact: str = "",
    output: str = "structure/decision_log.md",
) -> dict:
    root = Path(path)
    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        text = output_path.read_text(encoding="utf-8").rstrip()
    else:
        text = "# Decision Log"

    stamp = datetime.now().isoformat(timespec="seconds")
    entry = f"""## {stamp}

### Decision

{decision.strip() or "Not specified."}

### Rationale

{rationale.strip() or "Not specified."}

### Impact

{impact.strip() or "Not specified."}
"""
    output_path.write_text(text + "\n\n" + entry, encoding="utf-8")
    return {"output": str(output_path)}
