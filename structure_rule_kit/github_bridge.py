from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .network import _append_log, _ensure_network, _find_item, _load_items, _now, _write_json


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


def _issue_body(issue: dict) -> str:
    body = issue.get("body") or "Not specified."
    linked_snapshot = issue.get("linked_snapshot") or "None"
    return f"""{body}

---
Local Structure Rule Kit issue: {issue.get('id')}
Linked snapshot: {linked_snapshot}
"""


def _parse_issue_number(url: str) -> int | None:
    match = re.search(r"/issues/(\d+)(?:\D*)?$", url.strip())
    if not match:
        return None
    return int(match.group(1))


def _run_gh(command: list[str], runner=None) -> subprocess.CompletedProcess:
    run = runner or subprocess.run
    return run(command, capture_output=True, text=True)


def github_remote_labels(repo: str, runner=None) -> dict:
    command = ["gh", "label", "list", "--repo", repo, "--json", "name", "--limit", "1000"]
    result = _run_gh(command, runner=runner)
    if result.returncode != 0:
        return {
            "ok": False,
            "repo": repo,
            "labels": [],
            "error": (result.stderr or result.stdout).strip(),
            "command": command,
        }
    payload = json.loads(result.stdout or "[]")
    return {"ok": True, "repo": repo, "labels": sorted(item["name"] for item in payload), "command": command}


def _issue_create_command(repo: str, issue: dict, labels: list[str] | None = None) -> list[str]:
    command = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        issue.get("title") or "Untitled issue",
        "--body",
        _issue_body(issue),
    ]
    for label in labels or []:
        command.extend(["--label", label])
    return command


def github_issue_create(
    path: str = ".",
    issue: str = "",
    repo: str = "",
    apply: bool = False,
    skip_missing_labels: bool = False,
    runner=None,
) -> dict:
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo is required."}

    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issue_path, payload = _find_item(root, "issues", issue)
    _ensure_remote(payload)
    remote = payload["remote"]
    if remote.get("url") or remote.get("number"):
        return {
            "ok": True,
            "status": "skipped",
            "reason": "already-linked",
            "id": issue,
            "remote": remote,
        }

    labels = list(payload.get("labels", []))
    remote_label_report = github_remote_labels(repo, runner=runner) if labels else {"ok": True, "labels": []}
    missing_labels = []
    if labels and remote_label_report["ok"]:
        remote_labels = set(remote_label_report["labels"])
        missing_labels = [label for label in labels if label not in remote_labels]
    if labels and not remote_label_report["ok"]:
        missing_labels = labels

    selected_labels = [label for label in labels if label not in missing_labels] if skip_missing_labels else labels
    command = _issue_create_command(repo, payload, selected_labels)

    if missing_labels and not skip_missing_labels:
        return {
            "ok": False,
            "status": "missing-labels",
            "id": issue,
            "repo": repo,
            "missing_labels": missing_labels,
            "command": command,
            "message": "Remote labels are missing. Create them first or use --skip-missing-labels.",
        }

    if not apply:
        return {
            "ok": True,
            "status": "dry-run",
            "id": issue,
            "repo": repo,
            "missing_labels": missing_labels,
            "command": command,
        }

    result = _run_gh(command, runner=runner)
    if result.returncode != 0:
        return {
            "ok": False,
            "status": "failed",
            "id": issue,
            "repo": repo,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    url = result.stdout.strip().splitlines()[-1].strip()
    number = _parse_issue_number(url)
    payload["remote"] = {
        "provider": "github",
        "repo": repo,
        "number": number,
        "url": url,
        "synced_at": _now(),
    }
    payload["updated_at"] = _now()
    _write_json(issue_path, payload)
    _append_log(root, "github_issue_create", {"id": issue, "repo": repo, "url": url, "number": number})
    return {"ok": True, "status": "created", "id": issue, "repo": repo, "url": url, "number": number}


def github_issues_create(
    path: str = ".",
    repo: str = "",
    apply: bool = False,
    skip_missing_labels: bool = False,
    runner=None,
) -> dict:
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo is required.", "results": []}
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issues = _load_items(root / "issues")
    results = []
    for item in issues:
        results.append(
            github_issue_create(
                path,
                issue=item["id"],
                repo=repo,
                apply=apply,
                skip_missing_labels=skip_missing_labels,
                runner=runner,
            )
        )
    failures = [item for item in results if not item.get("ok")]
    created = [item for item in results if item.get("status") == "created"]
    skipped = [item for item in results if item.get("status") == "skipped"]
    dry_runs = [item for item in results if item.get("status") == "dry-run"]
    _append_log(
        root,
        "github_issues_create",
        {"repo": repo, "apply": apply, "created": len(created), "skipped": len(skipped), "failed": len(failures)},
    )
    return {
        "ok": not failures,
        "status": "created" if apply and created else "dry-run",
        "repo": repo,
        "created": len(created),
        "skipped": len(skipped),
        "dry_run": len(dry_runs),
        "failed": len(failures),
        "results": results,
    }


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


def github_sync(path: str = ".", dry_run: bool = True, repo: str = "", skip_missing_labels: bool = False, runner=None) -> dict:
    labels = export_github_labels(path)
    issues = export_github_issues(path)
    milestones = export_github_milestones(path)
    plan = build_github_sync_plan(path)
    if not dry_run:
        created = github_issues_create(
            path,
            repo=repo,
            apply=True,
            skip_missing_labels=skip_missing_labels,
            runner=runner,
        )
        return {
            "ok": created["ok"],
            "status": "created" if created["ok"] else "failed",
            "labels": labels,
            "issues": issues,
            "milestones": milestones,
            "plan": plan,
            "issue_create": created,
        }
    return {
        "ok": True,
        "status": "dry-run",
        "labels": labels,
        "issues": issues,
        "milestones": milestones,
        "plan": plan,
    }
