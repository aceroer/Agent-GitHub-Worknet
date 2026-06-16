#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def load_items(directory: Path) -> list[dict]:
    items = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_path"] = str(path)
        items.append(payload)
    return items


def classify_issue(issue: dict) -> str:
    remote = issue.get("remote") or {}
    if remote.get("url") or remote.get("number"):
        return "linked"
    return "local-only"


def build_report(path: Path, repo: str, output: Path) -> dict:
    network = path / "structure" / "network"
    issues = load_items(network / "issues")
    milestones = load_items(network / "milestones")
    prs = load_items(network / "prs")

    issue_groups = {"linked": [], "local-only": []}
    for issue in issues:
        issue_groups[classify_issue(issue)].append(issue)

    chunks = [
        "# GitHub Closure Sync Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Repo: {repo or 'Not specified'}",
        "",
        "## Summary",
        "",
        f"- Issues: {len(issues)}",
        f"- Linked issues: {len(issue_groups['linked'])}",
        f"- Local-only issues: {len(issue_groups['local-only'])}",
        f"- Milestones: {len(milestones)}",
        f"- PR records: {len(prs)}",
        "",
        "## Linked Issues",
        "",
    ]
    chunks.extend(
        f"- {item['id']}: {item.get('title', '')} -> {item.get('remote', {}).get('url')}"
        for item in issue_groups["linked"]
    )
    if not issue_groups["linked"]:
        chunks.append("- None.")

    chunks.extend(["", "## Local-Only Issues", ""])
    chunks.extend(f"- {item['id']}: {item.get('title', '')}" for item in issue_groups["local-only"])
    if not issue_groups["local-only"]:
        chunks.append("- None.")

    chunks.extend(
        [
            "",
            "## Experimental Notes",
            "",
            "- This report does not pull remote state yet.",
            "- Future closure work should add missing-remote and divergent states.",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return {
        "output": str(output),
        "issues": len(issues),
        "linked": len(issue_groups["linked"]),
        "local_only": len(issue_groups["local-only"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an experimental GitHub closure sync report.")
    parser.add_argument("--path", default=".", help="Project path containing structure/network.")
    parser.add_argument("--repo", default="", help="GitHub repo in owner/name form.")
    parser.add_argument("--output", default="structure/network/github_export/sync_report.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(Path(args.path), args.repo, Path(args.path) / args.output)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Wrote {report['output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
