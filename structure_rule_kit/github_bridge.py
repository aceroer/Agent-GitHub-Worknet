from __future__ import annotations

import json
from pathlib import Path

from .network import _append_log, _ensure_network, _load_items, _now, _write_json


def _remote_stub() -> dict:
    return {
        "provider": "github",
        "repo": None,
        "number": None,
        "url": None,
        "synced_at": None,
    }


def _clean_item(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key != "_path"}


def _ensure_remote(payload: dict) -> bool:
    remote = payload.get("remote")
    if not isinstance(remote, dict):
        payload["remote"] = _remote_stub()
        return True
    changed = False
    for key, value in _remote_stub().items():
        if key not in remote:
            remote[key] = value
            changed = True
    return changed


def ensure_remote_metadata(path: str = ".") -> dict:
    root = _ensure_network(path)
    updated = []
    for folder in ["issues", "prs", "milestones"]:
        for item_path in sorted((root / folder).glob("*.json")):
            payload = json.loads(item_path.read_text(encoding="utf-8"))
            if _ensure_remote(payload):
                payload["updated_at"] = _now()
                _write_json(item_path, payload)
                updated.append(str(item_path))
    _append_log(root, "github_remote_metadata", {"updated": len(updated)})
    return {"updated": updated, "count": len(updated)}


def _labels_from_issues(issues: list[dict]) -> list[dict]:
    names = sorted({label for issue in issues for label in issue.get("labels", [])})
    return [
        {
            "name": name,
            "color": "ededed",
            "description": "Exported from Structure Rule Kit.",
        }
        for name in names
    ]


def export_github_labels(path: str = ".", output: str = "structure/network/github_export/labels.json") -> dict:
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issues = _load_items(root / "issues")
    labels = _labels_from_issues(issues)
    output_path = Path(path) / output
    _write_json(output_path, {"labels": labels, "generated_at": _now()})
    _append_log(root, "github_labels_export", {"output": str(output_path), "labels": len(labels)})
    return {"output": str(output_path), "labels": len(labels)}


def _issue_markdown(issue: dict) -> str:
    labels = ", ".join(issue.get("labels", [])) or "None"
    return f"""# {issue.get('title', 'Untitled issue')}

Local ID: {issue.get('id')}

Status: {issue.get('status', 'open')}

Labels: {labels}

Assignee: {issue.get('assignee') or 'None'}

Linked snapshot: {issue.get('linked_snapshot') or 'None'}

Remote URL: {issue.get('remote', {}).get('url') or 'Not synced'}

## Body

{issue.get('body') or 'Not specified.'}
"""


def export_github_issues(path: str = ".", output_dir: str = "structure/network/github_export/issues") -> dict:
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issues = _load_items(root / "issues")
    output_root = Path(path) / output_dir
    output_root.mkdir(parents=True, exist_ok=True)
    outputs = []
    for issue in issues:
        output = output_root / f"{issue['id']}.md"
        output.write_text(_issue_markdown(issue), encoding="utf-8")
        outputs.append(str(output))
    _append_log(root, "github_issues_export", {"output_dir": str(output_root), "issues": len(outputs)})
    return {"output_dir": str(output_root), "issues": len(outputs), "outputs": outputs}


def export_github_milestones(
    path: str = ".",
    output: str = "structure/network/github_export/milestones.json",
) -> dict:
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    milestones = [_clean_item(item) for item in _load_items(root / "milestones")]
    output_path = Path(path) / output
    _write_json(output_path, {"milestones": milestones, "generated_at": _now()})
    _append_log(root, "github_milestones_export", {"output": str(output_path), "milestones": len(milestones)})
    return {"output": str(output_path), "milestones": len(milestones)}


def _linked(items: list[dict]) -> list[dict]:
    return [item for item in items if item.get("remote", {}).get("url") or item.get("remote", {}).get("number")]


def build_github_sync_plan(
    path: str = ".",
    output: str = "structure/network/github_export/sync_plan.md",
) -> dict:
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issues = _load_items(root / "issues")
    prs = _load_items(root / "prs")
    milestones = _load_items(root / "milestones")
    labels = _labels_from_issues(issues)
    linked_issues = _linked(issues)
    linked_prs = _linked(prs)
    linked_milestones = _linked(milestones)

    chunks = [
        "# GitHub Bridge Sync Plan",
        "",
        "Mode: dry-run only",
        "",
        "No remote API calls will be performed by this plan.",
        "",
        "## Summary",
        "",
        f"- Labels to ensure: {len(labels)}",
        f"- Local milestones: {len(milestones)}",
        f"- Milestones already linked: {len(linked_milestones)}",
        f"- Local issues: {len(issues)}",
        f"- Issues already linked: {len(linked_issues)}",
        f"- Local PR records: {len(prs)}",
        f"- PR records already linked: {len(linked_prs)}",
        "",
        "## Labels",
        "",
    ]
    chunks.extend(f"- {label['name']}" for label in labels)
    if not labels:
        chunks.append("- None.")
    chunks.extend(["", "## Milestones", ""])
    chunks.extend(f"- [{item.get('status', 'open')}] {item['id']}: {item.get('title', '')}" for item in milestones)
    if not milestones:
        chunks.append("- None.")
    chunks.extend(["", "## Issues", ""])
    chunks.extend(
        f"- [{item.get('status', 'open')}] {item['id']}: {item.get('title', '')}"
        f" -> {item.get('remote', {}).get('url') or 'create'}"
        for item in issues
    )
    if not issues:
        chunks.append("- None.")
    chunks.extend(["", "## PR Records", ""])
    chunks.extend(
        f"- [{item.get('status', 'open')}] {item['id']}: {item.get('title', '')}"
        f" -> {item.get('remote', {}).get('url') or 'export-only'}"
        for item in prs
    )
    if not prs:
        chunks.append("- None.")
    chunks.extend(
        [
            "",
            "## Next API Phase",
            "",
            "- Create missing labels.",
            "- Create or link missing milestones.",
            "- Create missing issues from exported markdown.",
            "- Keep PR records export-only until a real branch exists on the remote.",
        ]
    )

    output_path = Path(path) / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    _append_log(root, "github_sync_plan", {"output": str(output_path), "issues": len(issues), "prs": len(prs)})
    return {
        "output": str(output_path),
        "labels": len(labels),
        "issues": len(issues),
        "prs": len(prs),
        "milestones": len(milestones),
        "mode": "dry-run",
    }


def github_sync(path: str = ".", dry_run: bool = True) -> dict:
    if not dry_run:
        return {"ok": False, "status": "unsupported", "message": "Real GitHub sync is not implemented in 0.8."}
    labels = export_github_labels(path)
    issues = export_github_issues(path)
    milestones = export_github_milestones(path)
    plan = build_github_sync_plan(path)
    return {
        "ok": True,
        "status": "dry-run",
        "labels": labels,
        "issues": issues,
        "milestones": milestones,
        "plan": plan,
    }
