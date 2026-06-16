from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


NETWORK_DIR = Path("structure/network")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _slugify(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value.lower())
    return "-".join(words[:10]) or "item"


def _network_root(path: str) -> Path:
    return Path(path) / NETWORK_DIR


def _ensure_network(path: str = ".") -> Path:
    root = _network_root(path)
    for name in ["issues", "branches", "prs", "reviews", "projects", "comments", "milestones", "github_export"]:
        (root / name).mkdir(parents=True, exist_ok=True)
    log_path = root / "network_log.jsonl"
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    return root


def _next_id(directory: Path, prefix: str) -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*.json"):
        match = re.match(rf"{prefix}-(\d+)-", item.name)
        if match:
            existing.append(int(match.group(1)))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _append_log(network_root: Path, event: str, payload: dict) -> None:
    record = {"timestamp": _now(), "event": event, **payload}
    with (network_root / "network_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _load_items(directory: Path) -> list[dict]:
    items = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_path"] = str(path)
        items.append(payload)
    return items


def _find_item(root: Path, folder: str, item_id: str) -> tuple[Path, dict]:
    for path in (root / folder).glob(f"{item_id}*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        return path, payload
    raise FileNotFoundError(f"{folder}/{item_id}")


def _update_item(root: Path, folder: str, item_id: str, updates: dict, event: str) -> dict:
    path, payload = _find_item(root, folder, item_id)
    payload.update(updates)
    payload["updated_at"] = _now()
    _write_json(path, payload)
    _append_log(root, event, {"id": item_id, "updates": updates})
    return {"output": str(path), "id": item_id, "payload": payload}


def init_network(path: str = ".") -> dict:
    root = _ensure_network(path)
    _append_log(root, "network_init", {})
    return {"output": str(root)}


def update_issue_status(path: str = ".", issue: str = "", status: str = "closed") -> dict:
    root = _ensure_network(path)
    return _update_item(root, "issues", issue, {"status": status}, f"issue_{status}")


def assign_issue(path: str = ".", issue: str = "", assignee: str = "") -> dict:
    root = _ensure_network(path)
    return _update_item(root, "issues", issue, {"assignee": assignee}, "issue_assign")


def label_issue(path: str = ".", issue: str = "", labels: list[str] | None = None) -> dict:
    root = _ensure_network(path)
    item_path, payload = _find_item(root, "issues", issue)
    existing = list(payload.get("labels", []))
    for label in labels or []:
        if label not in existing:
            existing.append(label)
    payload["labels"] = existing
    payload["updated_at"] = _now()
    _write_json(item_path, payload)
    _append_log(root, "issue_label", {"id": issue, "labels": labels or []})
    return {"output": str(item_path), "id": issue, "payload": payload}


def create_issue(
    path: str = ".",
    title: str = "",
    body: str = "",
    labels: list[str] | None = None,
    assignee: str = "",
    linked_snapshot: str = "",
) -> dict:
    root = _ensure_network(path)
    issue_id = _next_id(root / "issues", "issue")
    payload = {
        "id": issue_id,
        "title": title.strip() or "Untitled issue",
        "status": "open",
        "body": body.strip() or "Not specified.",
        "labels": labels or [],
        "assignee": assignee,
        "linked_snapshot": linked_snapshot,
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = root / "issues" / f"{issue_id}-{_slugify(payload['title'])}.json"
    _write_json(output, payload)
    _append_log(root, "issue_create", {"id": issue_id, "title": payload["title"]})
    return {"output": str(output), "id": issue_id}


def list_issues(path: str = ".", status: str = "") -> list[dict]:
    root = _ensure_network(path)
    issues = _load_items(root / "issues")
    if status:
        issues = [issue for issue in issues if issue.get("status") == status]
    return issues


def create_network_branch(
    path: str = ".",
    name: str = "",
    purpose: str = "",
    issue: str = "",
    context_branch: str = "",
) -> dict:
    root = _ensure_network(path)
    branch_id = _slugify(name or purpose or "branch")
    payload = {
        "id": branch_id,
        "name": name.strip() or branch_id,
        "purpose": purpose.strip() or "Not specified.",
        "status": "active",
        "linked_issue": issue,
        "linked_context_branch": context_branch,
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = root / "branches" / f"{branch_id}.json"
    _write_json(output, payload)
    _append_log(root, "branch_create", {"id": branch_id, "name": payload["name"]})
    return {"output": str(output), "id": branch_id}


def create_pr(
    path: str = ".",
    title: str = "",
    body: str = "",
    issue: str = "",
    branch: str = "",
    checks: list[str] | None = None,
    linked_snapshot: str = "",
) -> dict:
    root = _ensure_network(path)
    pr_id = _next_id(root / "prs", "pr")
    payload = {
        "id": pr_id,
        "title": title.strip() or "Untitled PR",
        "status": "open",
        "body": body.strip() or "Not specified.",
        "linked_issue": issue,
        "branch": branch,
        "checks": checks or [],
        "linked_snapshot": linked_snapshot,
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = root / "prs" / f"{pr_id}-{_slugify(payload['title'])}.json"
    _write_json(output, payload)
    _append_log(root, "pr_create", {"id": pr_id, "title": payload["title"]})
    return {"output": str(output), "id": pr_id}


def update_pr_status(path: str = ".", pr: str = "", status: str = "closed") -> dict:
    root = _ensure_network(path)
    return _update_item(root, "prs", pr, {"status": status}, f"pr_{status}")


def merge_pr(path: str = ".", pr: str = "", method: str = "semantic") -> dict:
    root = _ensure_network(path)
    pr_path, payload = _find_item(root, "prs", pr)
    payload["status"] = "merged"
    payload["merge_method"] = method
    payload["merged_at"] = _now()
    payload["updated_at"] = _now()
    _write_json(pr_path, payload)
    linked_issue = payload.get("linked_issue")
    issue_output = ""
    if linked_issue:
        issue_output = update_issue_status(path, linked_issue, "closed")["output"]
    _append_log(root, "pr_merge", {"id": pr, "method": method, "linked_issue": linked_issue})
    build_project_board(path)
    return {"output": str(pr_path), "id": pr, "linked_issue_output": issue_output}


def create_review(
    path: str = ".",
    pr: str = "",
    reviewer: str = "",
    decision: str = "comment",
    body: str = "",
) -> dict:
    root = _ensure_network(path)
    review_id = _next_id(root / "reviews", "review")
    payload = {
        "id": review_id,
        "pr": pr,
        "reviewer": reviewer,
        "decision": decision,
        "body": body.strip() or "Not specified.",
        "created_at": _now(),
    }
    output = root / "reviews" / f"{review_id}-{_slugify(pr or decision)}.json"
    _write_json(output, payload)
    _append_log(root, "review_create", {"id": review_id, "pr": pr, "decision": decision})
    return {"output": str(output), "id": review_id}


def add_comment(path: str = ".", target: str = "", author: str = "", body: str = "") -> dict:
    root = _ensure_network(path)
    target_dir = root / "comments" / target
    target_dir.mkdir(parents=True, exist_ok=True)
    comment_id = _next_id(target_dir, "comment")
    payload = {
        "id": comment_id,
        "target": target,
        "author": author or "agent",
        "body": body.strip() or "Not specified.",
        "created_at": _now(),
    }
    output = target_dir / f"{comment_id}.json"
    _write_json(output, payload)
    _append_log(root, "comment_add", {"id": comment_id, "target": target})
    return {"output": str(output), "id": comment_id}


def list_comments(path: str = ".", target: str = "") -> list[dict]:
    root = _ensure_network(path)
    if target:
        return _load_items(root / "comments" / target)
    comments = []
    for directory in sorted((root / "comments").glob("*")):
        if directory.is_dir():
            comments.extend(_load_items(directory))
    return comments


def timeline(path: str = ".", target: str = "") -> list[dict]:
    root = _ensure_network(path)
    events = []
    log_path = root / "network_log.jsonl"
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if not target or record.get("id") == target or record.get("target") == target or record.get("pr") == target:
                events.append(record)
    for comment in list_comments(path, target):
        events.append({"timestamp": comment["created_at"], "event": "comment", "id": comment["id"], "target": comment["target"]})
    return sorted(events, key=lambda item: item.get("timestamp", ""))


def create_milestone(path: str = ".", title: str = "", due: str = "", description: str = "") -> dict:
    root = _ensure_network(path)
    milestone_id = _next_id(root / "milestones", "milestone")
    payload = {
        "id": milestone_id,
        "title": title.strip() or "Untitled milestone",
        "status": "open",
        "due": due,
        "description": description.strip() or "Not specified.",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = root / "milestones" / f"{milestone_id}-{_slugify(payload['title'])}.json"
    _write_json(output, payload)
    _append_log(root, "milestone_create", {"id": milestone_id, "title": payload["title"]})
    return {"output": str(output), "id": milestone_id}


def list_milestones(path: str = ".") -> list[dict]:
    root = _ensure_network(path)
    return _load_items(root / "milestones")


def github_export(path: str = ".", item_type: str = "issue", item_id: str = "") -> dict:
    root = _ensure_network(path)
    folder = "issues" if item_type == "issue" else "prs"
    _, payload = _find_item(root, folder, item_id)
    output = root / "github_export" / f"{item_id}.md"
    if item_type == "issue":
        content = f"""# {payload['title']}

Status: {payload.get('status')}

Labels: {', '.join(payload.get('labels', [])) or 'None'}

Assignee: {payload.get('assignee') or 'None'}

## Body

{payload.get('body') or 'Not specified.'}
"""
    else:
        content = f"""# {payload['title']}

Status: {payload.get('status')}

Branch: {payload.get('branch') or 'None'}

Linked issue: {payload.get('linked_issue') or 'None'}

Checks: {', '.join(payload.get('checks', [])) or 'None'}

## Body

{payload.get('body') or 'Not specified.'}
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    _append_log(root, "github_export", {"type": item_type, "id": item_id, "output": str(output)})
    return {"output": str(output)}


def build_project_board(path: str = ".", output: str = "structure/network/projects/board.md") -> dict:
    root = _ensure_network(path)
    issues = list_issues(path)
    prs = _load_items(root / "prs")
    reviews = _load_items(root / "reviews")
    branches = _load_items(root / "branches")

    chunks = [
        "# Agent Network Board",
        "",
        "## Summary",
        "",
        f"- Issues: {len(issues)}",
        f"- Branches: {len(branches)}",
        f"- PRs: {len(prs)}",
        f"- Reviews: {len(reviews)}",
        "",
        "## Issues",
        "",
    ]
    chunks.extend(f"- [{item.get('status')}] {item['id']}: {item['title']}" for item in issues)
    if not issues:
        chunks.append("- None.")
    chunks.extend(["", "## Branches", ""])
    chunks.extend(f"- [{item.get('status')}] {item['id']}: {item.get('purpose', '')}" for item in branches)
    if not branches:
        chunks.append("- None.")
    chunks.extend(["", "## Pull Requests", ""])
    chunks.extend(f"- [{item.get('status')}] {item['id']}: {item['title']}" for item in prs)
    if not prs:
        chunks.append("- None.")
    chunks.extend(["", "## Reviews", ""])
    chunks.extend(f"- [{item.get('decision')}] {item['id']} on {item.get('pr') or 'unlinked'}" for item in reviews)
    if not reviews:
        chunks.append("- None.")

    output_path = Path(path) / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    _append_log(root, "project_board", {"output": str(output_path)})
    return {"output": str(output_path), "issues": len(issues), "prs": len(prs), "reviews": len(reviews)}


def sync_network(path: str = ".", target: str = "codex") -> dict:
    from .agent_sync import sync_agent

    root = _ensure_network(path)
    board = build_project_board(path)
    agent = sync_agent(path, target=target)
    _append_log(root, "network_sync", {"target": target, "board": board["output"], "status": agent["status"]})
    return {"board": board["output"], "agent_sync": agent, "status": agent["status"], "ready": agent["ready"]}


def snapshot_network(path: str = ".", message: str = "Agent network snapshot", target: str = "codex") -> dict:
    from .agent_brief import build_agent_brief
    from .context_git import create_context_snapshot, init_context

    root = _ensure_network(path)
    init_context(path)
    board = build_project_board(path)
    brief = build_agent_brief(path, task=message, refresh=True)
    snapshot = create_context_snapshot(path, message=message)

    updated = []
    for folder in ["issues", "prs", "reviews"]:
        for item_path in (root / folder).glob("*.json"):
            payload = json.loads(item_path.read_text(encoding="utf-8"))
            if not payload.get("linked_snapshot"):
                payload["linked_snapshot"] = snapshot["id"]
                payload["updated_at"] = _now()
                _write_json(item_path, payload)
                updated.append(str(item_path))

    _append_log(
        root,
        "network_snapshot",
        {"snapshot": snapshot["id"], "message": message, "updated": len(updated), "target": target},
    )
    return {
        "snapshot": snapshot["id"],
        "snapshot_file": snapshot["output"],
        "board": board["output"],
        "brief": brief["output"],
        "updated": updated,
    }
