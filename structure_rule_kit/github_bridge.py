from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from .network import _append_log, _ensure_network, _find_item, _load_items, _now, _write_json


GITHUB_CONFIG = Path("structure/network/github_config.json")
GITHUB_SYNC_REPORT = Path("structure/network/github_export/sync_report.md")


def _remote_stub() -> dict:
    return {
        "provider": "github",
        "repo": None,
        "number": None,
        "url": None,
        "synced_at": None,
    }


def _default_config(repo: str = "") -> dict:
    return {
        "provider": "github",
        "repo": repo,
        "sync_policy": {
            "default_mode": "dry-run",
            "create_missing_labels": False,
            "create_missing_milestones": False,
            "skip_missing_labels": False,
            "pull_remote_state": True,
            "write_sync_report": True,
        },
        "paths": {
            "network": "structure/network",
            "sync_report": str(GITHUB_SYNC_REPORT),
        },
    }


def write_github_config(
    path: str = ".",
    repo: str = "",
    output: str = str(GITHUB_CONFIG),
    force: bool = False,
) -> dict:
    root = _ensure_network(path)
    output_path = Path(path) / output
    if output_path.exists() and not force:
        return {"output": str(output_path), "created": False, "config": load_github_config(path, output)}
    payload = _default_config(repo)
    _write_json(output_path, payload)
    _append_log(root, "github_config", {"output": str(output_path), "repo": repo, "created": True})
    return {"output": str(output_path), "created": True, "config": payload}


def load_github_config(path: str = ".", config: str = str(GITHUB_CONFIG)) -> dict:
    config_path = Path(path) / config
    if not config_path.exists():
        return _default_config("")
    return json.loads(config_path.read_text(encoding="utf-8"))


def _resolve_repo(path: str, repo: str = "", config: str = str(GITHUB_CONFIG)) -> str:
    return repo or load_github_config(path, config).get("repo", "")


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


def _gh_json(command: list[str], runner=None) -> tuple[bool, object, str]:
    result = _run_gh(command, runner=runner)
    if result.returncode != 0:
        return False, None, (result.stderr or result.stdout).strip()
    try:
        return True, json.loads(result.stdout or "null"), ""
    except json.JSONDecodeError as exc:
        return False, None, str(exc)


def github_doctor(path: str = ".", repo: str = "", runner=None) -> dict:
    repo = _resolve_repo(path, repo)
    checks = []
    gh_path = shutil.which("gh")
    checks.append({"name": "gh-installed", "ok": gh_path is not None, "path": gh_path})
    if gh_path is None:
        return {"ok": False, "repo": repo, "checks": checks}
    commands = [
        ("gh-auth", ["gh", "auth", "status"]),
        ("repo-view", ["gh", "repo", "view", repo, "--json", "name,owner,visibility,url"]),
        ("issues-list", ["gh", "issue", "list", "--repo", repo, "--limit", "1", "--json", "number,state,title,url"]),
        ("labels-list", ["gh", "label", "list", "--repo", repo, "--json", "name", "--limit", "1000"]),
        ("milestones-list", ["gh", "api", f"repos/{repo}/milestones?state=all"]),
    ]
    for name, command in commands:
        if not repo and name != "gh-auth":
            checks.append({"name": name, "ok": False, "stderr": "repo is not configured"})
            continue
        result = _run_gh(command, runner=runner)
        checks.append(
            {
                "name": name,
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
    return {"ok": all(item["ok"] for item in checks), "repo": repo, "checks": checks}


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


def github_labels_create(path: str = ".", repo: str = "", apply: bool = False, runner=None) -> dict:
    repo = _resolve_repo(path, repo)
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo or github_config repo is required."}
    root = _ensure_network(path)
    issues = _load_items(root / "issues")
    desired = _labels_from_issues(issues)
    remote = github_remote_labels(repo, runner=runner)
    if not remote["ok"]:
        return {"ok": False, "status": "remote-labels-failed", "message": remote.get("error", ""), "results": []}
    remote_names = set(remote["labels"])
    missing = [label for label in desired if label["name"] not in remote_names]
    results = []
    for label in missing:
        command = [
            "gh",
            "label",
            "create",
            label["name"],
            "--repo",
            repo,
            "--color",
            label["color"],
            "--description",
            label["description"],
        ]
        if not apply:
            results.append({"ok": True, "status": "dry-run", "label": label["name"], "command": command})
            continue
        result = _run_gh(command, runner=runner)
        results.append(
            {
                "ok": result.returncode == 0,
                "status": "created" if result.returncode == 0 else "failed",
                "label": label["name"],
                "command": command,
                "stderr": result.stderr,
            }
        )
    failures = [item for item in results if not item["ok"]]
    _append_log(root, "github_labels_create", {"repo": repo, "apply": apply, "missing": len(missing), "failed": len(failures)})
    return {
        "ok": not failures,
        "status": "created" if apply else "dry-run",
        "repo": repo,
        "missing": len(missing),
        "created": len([item for item in results if item["status"] == "created"]),
        "results": results,
    }


def github_milestones_create(path: str = ".", repo: str = "", apply: bool = False, runner=None) -> dict:
    repo = _resolve_repo(path, repo)
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo or github_config repo is required."}
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    milestones = _load_items(root / "milestones")
    results = []
    for milestone in milestones:
        if milestone.get("remote", {}).get("url") or milestone.get("remote", {}).get("number"):
            results.append({"ok": True, "status": "skipped", "id": milestone["id"], "reason": "already-linked"})
            continue
        command = [
            "gh",
            "api",
            f"repos/{repo}/milestones",
            "-f",
            f"title={milestone.get('title', 'Untitled milestone')}",
            "-f",
            f"description={milestone.get('description', '')}",
        ]
        if milestone.get("due"):
            command.extend(["-f", f"due_on={milestone['due']}T00:00:00Z"])
        if not apply:
            results.append({"ok": True, "status": "dry-run", "id": milestone["id"], "command": command})
            continue
        result = _run_gh(command, runner=runner)
        if result.returncode != 0:
            results.append({"ok": False, "status": "failed", "id": milestone["id"], "command": command, "stderr": result.stderr})
            continue
        payload = json.loads(result.stdout or "{}")
        item_path = Path(milestone["_path"])
        stored = json.loads(item_path.read_text(encoding="utf-8"))
        stored["remote"] = {
            "provider": "github",
            "repo": repo,
            "number": payload.get("number"),
            "url": payload.get("html_url"),
            "synced_at": _now(),
        }
        stored["updated_at"] = _now()
        _write_json(item_path, stored)
        results.append({"ok": True, "status": "created", "id": milestone["id"], "url": payload.get("html_url"), "number": payload.get("number")})
    failures = [item for item in results if not item["ok"]]
    _append_log(root, "github_milestones_create", {"repo": repo, "apply": apply, "failed": len(failures)})
    return {"ok": not failures, "status": "created" if apply else "dry-run", "repo": repo, "results": results}


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
    repo = _resolve_repo(path, repo)
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo or github_config repo is required."}

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
    repo = _resolve_repo(path, repo)
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo or github_config repo is required.", "results": []}
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


def _remote_issue_payload(repo: str, number: int, runner=None) -> dict:
    command = [
        "gh",
        "issue",
        "view",
        str(number),
        "--repo",
        repo,
        "--json",
        "number,state,title,url,labels,assignees,milestone",
    ]
    ok, payload, error = _gh_json(command, runner=runner)
    return {"ok": ok, "payload": payload, "error": error, "command": command}


def _local_status_from_remote(state: str) -> str:
    return "closed" if state.upper() == "CLOSED" else "open"


def _classify_remote_state(local: dict, remote_payload: dict | None, remote_ok: bool) -> str:
    if not local.get("remote", {}).get("number"):
        return "local-only"
    if not remote_ok or not remote_payload:
        return "missing-remote"
    remote_status = _local_status_from_remote(remote_payload.get("state", "OPEN"))
    if local.get("title") != remote_payload.get("title") or local.get("status", "open") != remote_status:
        return "remote-changed"
    return "synced"


def github_pull(path: str = ".", repo: str = "", runner=None) -> dict:
    repo = _resolve_repo(path, repo)
    if not repo:
        return {"ok": False, "status": "missing-repo", "message": "--repo or github_config repo is required.", "results": []}
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    results = []
    for issue_path in sorted((root / "issues").glob("*.json")):
        local = json.loads(issue_path.read_text(encoding="utf-8"))
        remote = local.get("remote") or {}
        number = remote.get("number")
        if not number:
            local["worknet_status"] = "local-only"
            local["updated_at"] = _now()
            _write_json(issue_path, local)
            results.append({"ok": True, "id": local["id"], "status": "local-only"})
            continue
        fetched = _remote_issue_payload(remote.get("repo") or repo, int(number), runner=runner)
        status = _classify_remote_state(local, fetched.get("payload"), fetched["ok"])
        local["remote_state"] = fetched.get("payload") if fetched["ok"] else {"error": fetched.get("error")}
        local["worknet_status"] = status
        local["updated_at"] = _now()
        _write_json(issue_path, local)
        results.append({"ok": fetched["ok"], "id": local["id"], "status": status, "number": number})
    failures = [item for item in results if not item["ok"]]
    _append_log(root, "github_pull", {"repo": repo, "issues": len(results), "failed": len(failures)})
    return {"ok": not failures, "status": "pulled", "repo": repo, "results": results}


def github_sync_report(
    path: str = ".",
    repo: str = "",
    output: str = str(GITHUB_SYNC_REPORT),
) -> dict:
    repo = _resolve_repo(path, repo)
    root = _ensure_network(path)
    ensure_remote_metadata(path)
    issues = _load_items(root / "issues")
    milestones = _load_items(root / "milestones")
    prs = _load_items(root / "prs")
    groups = {"synced": [], "remote-changed": [], "missing-remote": [], "local-only": [], "unclassified": []}
    for issue in issues:
        status = issue.get("worknet_status") or ("synced" if issue.get("remote", {}).get("url") else "local-only")
        groups.setdefault(status, groups["unclassified"]).append(issue)

    chunks = [
        "# Agent GitHub Worknet Sync Report",
        "",
        f"Generated: {_now()}",
        f"Repo: {repo or 'Not configured'}",
        "",
        "## Summary",
        "",
        f"- Issues: {len(issues)}",
        f"- Synced issues: {len(groups['synced'])}",
        f"- Remote-changed issues: {len(groups['remote-changed'])}",
        f"- Missing remote issues: {len(groups['missing-remote'])}",
        f"- Local-only issues: {len(groups['local-only'])}",
        f"- Milestones: {len(milestones)}",
        f"- PR records: {len(prs)}",
        "",
    ]
    for group_name in ["synced", "remote-changed", "missing-remote", "local-only"]:
        title = group_name.replace("-", " ").title()
        chunks.extend([f"## {title}", ""])
        for item in groups[group_name]:
            remote = item.get("remote", {})
            suffix = f" -> {remote.get('url')}" if remote.get("url") else ""
            chunks.append(f"- {item['id']}: {item.get('title', '')}{suffix}")
        if not groups[group_name]:
            chunks.append("- None.")
        chunks.append("")
    output_path = Path(path) / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    _append_log(root, "github_sync_report", {"repo": repo, "output": str(output_path), "issues": len(issues)})
    return {
        "output": str(output_path),
        "repo": repo,
        "issues": len(issues),
        "synced": len(groups["synced"]),
        "remote_changed": len(groups["remote-changed"]),
        "missing_remote": len(groups["missing-remote"]),
        "local_only": len(groups["local-only"]),
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
    repo = _resolve_repo(path, repo)
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
        pull = github_pull(path, repo=repo, runner=runner) if created["ok"] else {"ok": False, "status": "skipped"}
        report = github_sync_report(path, repo=repo)
        return {
            "ok": created["ok"] and pull["ok"],
            "status": "created" if created["ok"] else "failed",
            "labels": labels,
            "issues": issues,
            "milestones": milestones,
            "plan": plan,
            "issue_create": created,
            "pull": pull,
            "report": report,
        }
    report = github_sync_report(path, repo=repo)
    return {
        "ok": True,
        "status": "dry-run",
        "labels": labels,
        "issues": issues,
        "milestones": milestones,
        "plan": plan,
        "report": report,
    }
