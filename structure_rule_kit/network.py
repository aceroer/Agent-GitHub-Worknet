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
    for name in ["issues", "branches", "prs", "reviews", "projects"]:
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


def init_network(path: str = ".") -> dict:
    root = _ensure_network(path)
    _append_log(root, "network_init", {})
    return {"output": str(root)}


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
