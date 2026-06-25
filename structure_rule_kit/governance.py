from __future__ import annotations

import json
import os
import re
import shlex
from datetime import datetime, timedelta
from pathlib import Path

from .network import _ensure_network, _find_item, _next_id, _now, _slugify, _write_json


GOVERNANCE_DIR = Path("structure/worknet/governance")
POLICY_FILE = GOVERNANCE_DIR / "policy.json"
AUDIT_LOG = GOVERNANCE_DIR / "audit_log.jsonl"
APPROVALS_DIR = GOVERNANCE_DIR / "approvals"
SANDBOXES_DIR = GOVERNANCE_DIR / "sandboxes"
TOKENS_DIR = GOVERNANCE_DIR / "capability_tokens"
SUBAGENTS_DIR = Path("structure/worknet/subagents")
PLANS_DIR = Path("structure/worknet/plans")

SHELL_CONTROL_TOKENS = {";", "&&", "||", "|", ">", ">>", "<", "<<", "`", "$(", "${"}
SECRET_NAME_RE = re.compile(r"(API[_-]?KEY|TOKEN|SECRET|PASSWORD|PRIVATE[_-]?KEY|ACCESS[_-]?KEY)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,})")


DEFAULT_POLICY = {
    "version": "1.2",
    "permissions": {
        "plan": {
            "description": "Read context and produce plans. No file writes, shell execution, or GitHub writes.",
            "write_paths": [],
            "command_levels": [],
            "github_apply": False,
            "requires_approval": False,
        },
        "draft": {
            "description": "Write local worknet, task, and draft artifacts. No source edits or GitHub writes.",
            "write_paths": ["structure/worknet/", "structure/tasks/", "structure/drafts/"],
            "command_levels": ["read"],
            "github_apply": False,
            "requires_approval": False,
        },
        "apply": {
            "description": "Apply project changes and verification commands only after explicit approval.",
            "write_paths": ["."],
            "command_levels": ["read", "verify", "write"],
            "github_apply": True,
            "requires_approval": True,
        },
    },
    "command_levels": {
        "read": ["ls", "pwd", "rg", "grep", "cat", "sed", "head", "tail", "find", "git status", "git diff"],
        "verify": ["pytest", "python -m pytest", "python3 -m pytest", "python -m py_compile", "python3 -m py_compile"],
        "write": ["black", "ruff", "npm run", "python -m build", "python3 -m build"],
        "danger": ["rm", "sudo", "mv", "git push", "gh issue create", "gh pr create", "gh issue comment", "curl", "chmod", "chown", "dd"],
    },
    "default_allowed_paths": [
        "structure/worknet/subagents/{subagent}/",
        "structure/tasks/",
        "structure/drafts/",
    ],
}

GATED_ACTIONS = {
    "commit": {
        "aliases": ["git-commit", "git commit"],
        "required_action": "commit",
        "description": "Create a local git commit.",
        "examples": ["git commit"],
    },
    "remote-push": {
        "aliases": ["push", "git-push", "git push"],
        "required_action": "remote-push",
        "description": "Push local commits to a remote repository or fork.",
        "examples": ["git push"],
    },
    "gh-pr-create": {
        "aliases": ["pr-create", "github-pr-create", "gh pr create"],
        "required_action": "gh-pr-create",
        "description": "Create a GitHub pull request.",
        "examples": ["gh pr create"],
    },
    "gh-issue-comment": {
        "aliases": ["issue-comment", "github-issue-comment", "gh issue comment"],
        "required_action": "gh-issue-comment",
        "description": "Write a GitHub issue comment.",
        "examples": ["gh issue comment"],
    },
    "gh-pr-ready": {
        "aliases": ["pr-ready", "github-pr-ready", "gh pr ready"],
        "required_action": "gh-pr-ready",
        "description": "Mark a draft GitHub pull request ready for review.",
        "examples": ["gh pr ready"],
    },
    "gh-pr-merge": {
        "aliases": ["pr-merge", "github-pr-merge", "gh pr merge"],
        "required_action": "gh-pr-merge",
        "description": "Merge a GitHub pull request.",
        "examples": ["gh pr merge"],
    },
    "gh-pr-close": {
        "aliases": ["pr-close", "github-pr-close", "gh pr close"],
        "required_action": "gh-pr-close",
        "description": "Close a GitHub pull request.",
        "examples": ["gh pr close"],
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _governance_root(path: str = ".") -> Path:
    return _root(path) / GOVERNANCE_DIR


def _append_audit(path: str, event: str, payload: dict) -> None:
    governance_root = _governance_root(path)
    governance_root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (governance_root / "audit_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def governance_init(path: str = ".", force: bool = False) -> dict:
    root = _root(path)
    governance_root = _governance_root(path)
    for directory in [governance_root, root / APPROVALS_DIR, root / SANDBOXES_DIR, root / TOKENS_DIR, root / SUBAGENTS_DIR, root / PLANS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    policy_path = root / POLICY_FILE
    created_policy = False
    if force or not policy_path.exists():
        _write_json(policy_path, DEFAULT_POLICY)
        created_policy = True

    audit_path = root / AUDIT_LOG
    if not audit_path.exists():
        audit_path.write_text("", encoding="utf-8")
    _append_audit(path, "governance_init", {"policy": str(policy_path), "created_policy": created_policy})
    return {"output": str(governance_root), "policy": str(policy_path), "created_policy": created_policy}


def load_policy(path: str = ".", policy: str = str(POLICY_FILE)) -> dict:
    policy_path = _root(path) / policy
    if not policy_path.exists():
        governance_init(path)
    return json.loads(policy_path.read_text(encoding="utf-8"))


def policy_show(path: str = ".") -> dict:
    return load_policy(path)


def _load_subagent(path: str, subagent: str) -> tuple[Path, dict]:
    root = _root(path) / SUBAGENTS_DIR
    for candidate in root.glob(f"{subagent}*.json"):
        return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"subagent/{subagent}")


def _normalize_relative(root: Path, value: str) -> str:
    target = Path(value)
    if target.is_absolute():
        try:
            target = target.resolve().relative_to(root.resolve())
        except ValueError:
            return str(target)
    return target.as_posix().lstrip("./")


def _safe_resolve_for_check(root: Path, value: str) -> Path:
    base = root.resolve()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve(strict=False)


def _path_allowed(root: Path, target: str, allowed_paths: list[str]) -> bool:
    base = root.resolve()
    target_resolved = _safe_resolve_for_check(root, target)
    for allowed in allowed_paths:
        allowed_clean = allowed.replace("\\", "/").lstrip("./")
        if allowed_clean == ".":
            return target_resolved == base or base in target_resolved.parents
        allowed_clean = allowed_clean.rstrip("/")
        allowed_resolved = _safe_resolve_for_check(root, allowed_clean)
        if target_resolved == allowed_resolved or allowed_resolved in target_resolved.parents:
            return True
    return False


def subagent_create(
    path: str = ".",
    name: str = "",
    permission: str = "plan",
    goal: str = "",
    issue: str = "",
    allowed_paths: list[str] | None = None,
) -> dict:
    governance_init(path)
    policy = load_policy(path)
    if permission not in policy["permissions"]:
        raise ValueError(f"Unknown permission: {permission}")

    root = _root(path)
    subagent_root = root / SUBAGENTS_DIR
    subagent_id = _next_id(subagent_root, "subagent")
    title = name.strip() or subagent_id
    output = subagent_root / f"{subagent_id}-{_slugify(title)}.json"
    if allowed_paths is None:
        allowed_paths = list(policy["permissions"][permission]["write_paths"])
        if permission == "draft":
            allowed_paths.extend(item.replace("{subagent}", subagent_id) for item in policy["default_allowed_paths"])

    payload = {
        "id": subagent_id,
        "name": title,
        "permission": permission,
        "goal": goal.strip(),
        "linked_issue": issue,
        "allowed_paths": sorted(dict.fromkeys(allowed_paths)),
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }
    _write_json(output, payload)

    sandbox = {
        "subagent": subagent_id,
        "permission": permission,
        "allowed_paths": payload["allowed_paths"],
        "command_levels": policy["permissions"][permission]["command_levels"],
        "github_apply": policy["permissions"][permission]["github_apply"],
        "created_at": _now(),
    }
    sandbox_path = root / SANDBOXES_DIR / f"{subagent_id}.json"
    _write_json(sandbox_path, sandbox)
    _append_audit(path, "subagent_create", {"subagent": subagent_id, "permission": permission, "sandbox": str(sandbox_path)})
    return {"id": subagent_id, "output": str(output), "sandbox": str(sandbox_path), "payload": payload}


def subagent_plan(path: str = ".", issue: str = "", output_dir: str = str(PLANS_DIR)) -> dict:
    governance_init(path)
    network_root = _ensure_network(path)
    _issue_path, issue_payload = _find_item(network_root, "issues", issue)
    root = _root(path)
    plan_root = root / output_dir
    plan_id = _next_id(plan_root, "plan")
    output = plan_root / f"{plan_id}-{issue}.json"
    title = issue_payload.get("title", issue)
    payload = {
        "id": plan_id,
        "issue": issue,
        "title": title,
        "created_at": _now(),
        "mode": "deterministic-governance-plan",
        "subagents": [
            {
                "role": "context-reader",
                "permission": "plan",
                "task": "Read the local issue, structure files, and recent worknet state.",
            },
            {
                "role": "draft-builder",
                "permission": "draft",
                "task": "Prepare task notes, draft changes, and verification checklist under allowed worknet paths.",
            },
            {
                "role": "human-approved-applier",
                "permission": "apply",
                "task": "Apply code or GitHub changes only after an approval record grants the specific action.",
            },
        ],
        "checks": [
            "Run sandbox-check before writing any file.",
            "Run command-check before executing any command.",
            "Request approval before apply-level file changes or GitHub writes.",
        ],
    }
    _write_json(output, payload)
    _append_audit(path, "subagent_plan", {"issue": issue, "plan": str(output)})
    return {"id": plan_id, "output": str(output), "payload": payload}


def approval_request(path: str = ".", subagent: str = "", action: str = "", target: str = "", reason: str = "") -> dict:
    governance_init(path)
    root = _root(path)
    _load_subagent(path, subagent)
    approvals_root = root / APPROVALS_DIR
    approval_id = _next_id(approvals_root, "approval")
    payload = {
        "id": approval_id,
        "subagent": subagent,
        "action": action.strip() or "unspecified",
        "target": target,
        "reason": reason,
        "status": "requested",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = approvals_root / f"{approval_id}.json"
    _write_json(output, payload)
    _append_audit(path, "approval_request", {"approval": approval_id, "subagent": subagent, "action": payload["action"]})
    return {"id": approval_id, "output": str(output), "payload": payload}


def _load_approval(path: str, approval: str) -> tuple[Path, dict]:
    approvals_root = _root(path) / APPROVALS_DIR
    for candidate in approvals_root.glob(f"{approval}*.json"):
        return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"approval/{approval}")


def approval_grant(path: str = ".", approval: str = "", granted_by: str = "human", ttl_hours: int = 24) -> dict:
    governance_init(path)
    root = _root(path)
    approval_path, payload = _load_approval(path, approval)
    payload["status"] = "granted"
    payload["granted_by"] = granted_by
    payload["granted_at"] = _now()
    payload["updated_at"] = _now()
    _write_json(approval_path, payload)

    token_root = root / TOKENS_DIR
    token_id = _next_id(token_root, "token")
    token = {
        "id": token_id,
        "approval": payload["id"],
        "subagent": payload["subagent"],
        "action": payload["action"],
        "target": payload["target"],
        "status": "active",
        "created_at": _now(),
        "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(timespec="seconds"),
    }
    token_path = token_root / f"{token_id}.json"
    _write_json(token_path, token)
    _append_audit(path, "approval_grant", {"approval": payload["id"], "token": token_id})
    return {"id": payload["id"], "output": str(approval_path), "token": str(token_path), "payload": payload}


def token_revoke(path: str = ".", token: str = "", revoked_by: str = "human", reason: str = "") -> dict:
    governance_init(path)
    root = _root(path)
    token_root = root / TOKENS_DIR
    matches = sorted(token_root.glob(f"{token}*.json"))
    if not matches:
        raise FileNotFoundError(f"token/{token}")
    token_path = matches[0]
    payload = json.loads(token_path.read_text(encoding="utf-8"))
    payload["status"] = "revoked"
    payload["revoked_by"] = revoked_by
    payload["revoked_at"] = _now()
    payload["revocation_reason"] = reason
    _write_json(token_path, payload)
    _append_audit(path, "token_revoke", {"token": payload.get("id", token), "revoked_by": revoked_by})
    return {"id": payload.get("id", token), "output": str(token_path), "payload": payload}


def token_is_active(token: dict) -> bool:
    if token.get("status") != "active":
        return False
    expires_at = token.get("expires_at", "")
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at) < datetime.now():
                return False
        except ValueError:
            return False
    return True


def _canonical_gate_action(action: str) -> str:
    normalized = action.strip().lower()
    for canonical, definition in GATED_ACTIONS.items():
        names = [canonical, *definition.get("aliases", [])]
        if normalized in {name.lower() for name in names}:
            return canonical
    return normalized


def _load_tokens(path: str) -> list[dict]:
    token_root = _root(path) / TOKENS_DIR
    if not token_root.exists():
        return []
    tokens = []
    for token_path in sorted(token_root.glob("*.json")):
        try:
            tokens.append(json.loads(token_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            tokens.append({"id": token_path.stem, "status": "invalid", "path": str(token_path)})
    return tokens


def gate_check(path: str = ".", action: str = "", subagent: str = "", target: str = "") -> dict:
    governance_init(path)
    canonical = _canonical_gate_action(action)
    definition = GATED_ACTIONS.get(canonical, {})
    required_action = definition.get("required_action", canonical)
    tokens = _load_tokens(path)
    matches = []
    inactive_matches = []
    for token in tokens:
        action_matches = token.get("action") in {required_action, canonical, action}
        subagent_matches = not subagent or token.get("subagent") == subagent
        target_matches = not target or token.get("target") in {"", target}
        if not (action_matches and subagent_matches and target_matches):
            continue
        if token_is_active(token):
            matches.append(token)
        else:
            inactive_matches.append(token)
    ok = bool(matches)
    report = {
        "ok": ok,
        "action": canonical,
        "requested_action": action,
        "required_action": required_action,
        "target": target,
        "subagent": subagent,
        "status": "approved" if ok else "blocked",
        "description": definition.get("description", "Gated action requires explicit approval."),
        "matching_tokens": [token.get("id", "") for token in matches],
        "inactive_tokens": [token.get("id", "") for token in inactive_matches],
        "message": "Approval token found." if ok else "Missing active approval token for gated action.",
    }
    _append_audit(
        path,
        "gate_check",
        {
            "action": canonical,
            "target": target,
            "subagent": subagent,
            "status": report["status"],
            "matching_tokens": report["matching_tokens"],
        },
    )
    return report


def sandbox_check(path: str = ".", subagent: str = "", target_path: str = "") -> dict:
    governance_init(path)
    root = _root(path)
    _subagent_path, payload = _load_subagent(path, subagent)
    allowed = _path_allowed(root, target_path, payload.get("allowed_paths", []))
    resolved = str(_safe_resolve_for_check(root, target_path))
    report = {
        "ok": allowed,
        "subagent": subagent,
        "permission": payload.get("permission", ""),
        "path": target_path,
        "resolved_path": resolved,
        "allowed_paths": payload.get("allowed_paths", []),
        "status": "allowed" if allowed else "denied",
    }
    _append_audit(path, "sandbox_check", {"subagent": subagent, "target": target_path, "status": report["status"]})
    return report


def _command_starts(command: str, prefix: str) -> bool:
    return command == prefix or command.startswith(f"{prefix} ")


def classify_command(command: str) -> str:
    command = command.strip()
    if not command:
        return "unknown"
    if any(token in command for token in SHELL_CONTROL_TOKENS):
        return "danger"
    try:
        parts = shlex.split(command)
    except ValueError:
        return "unknown"
    first = parts[0] if parts else ""
    if "=" in first and not first.startswith("./"):
        return "unknown"
    danger_prefixes = DEFAULT_POLICY["command_levels"]["danger"]
    if first in {"rm", "sudo", "chmod", "chown", "dd", "curl"}:
        return "danger"
    if any(_command_starts(command, prefix) for prefix in danger_prefixes):
        return "danger"
    if "pytest" in parts or any(_command_starts(command, prefix) for prefix in DEFAULT_POLICY["command_levels"]["verify"]):
        return "verify"
    if first in {"ls", "pwd", "rg", "grep", "cat", "sed", "head", "tail", "find"}:
        return "read"
    if any(_command_starts(command, prefix) for prefix in ["git status", "git diff"]):
        return "read"
    if first in {"black", "ruff", "npm"} or any(_command_starts(command, prefix) for prefix in DEFAULT_POLICY["command_levels"]["write"]):
        return "write"
    return "unknown"


def sanitize_environment(env: dict[str, str] | None = None) -> dict:
    env = dict(env or os.environ)
    removed = sorted(key for key in env if SECRET_NAME_RE.search(key))
    sanitized = {key: value for key, value in env.items() if key not in removed}
    return {"env": sanitized, "removed": removed}


def secret_scan(path: str = ".", target_path: str = "") -> dict:
    root = _root(path)
    target = _safe_resolve_for_check(root, target_path)
    base = root.resolve()
    if target != base and base not in target.parents:
        raise ValueError("Secret scan target escapes repository root")
    findings = []
    if target.exists() and target.is_file():
        text = target.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if SECRET_NAME_RE.search(line) or SECRET_VALUE_RE.search(line):
                findings.append({"line": lineno, "kind": "possible-secret"})
    report = {"ok": not findings, "path": target_path, "resolved_path": str(target), "findings": findings}
    _append_audit(path, "secret_scan", {"target": target_path, "findings": len(findings)})
    return report


def command_check(path: str = ".", command: str = "", subagent: str = "", permission: str = "") -> dict:
    governance_init(path)
    policy = load_policy(path)
    if subagent:
        _subagent_path, payload = _load_subagent(path, subagent)
        permission = payload.get("permission", permission)
    permission = permission or "plan"
    if permission not in policy["permissions"]:
        raise ValueError(f"Unknown permission: {permission}")
    level = classify_command(command)
    allowed_levels = policy["permissions"][permission]["command_levels"]
    ok = level in allowed_levels and level != "danger"
    report = {
        "ok": ok,
        "command": command,
        "level": level,
        "permission": permission,
        "allowed_levels": allowed_levels,
        "status": "allowed" if ok else "denied",
    }
    _append_audit(path, "command_check", {"subagent": subagent, "permission": permission, "command": command, "level": level, "status": report["status"]})
    return report


def governance_status(path: str = ".") -> dict:
    governance_init(path)
    root = _root(path)
    subagents = list((root / SUBAGENTS_DIR).glob("*.json"))
    approvals = list((root / APPROVALS_DIR).glob("*.json"))
    tokens = list((root / TOKENS_DIR).glob("*.json"))
    audit_path = root / AUDIT_LOG
    audit_events = len(audit_path.read_text(encoding="utf-8").splitlines()) if audit_path.exists() else 0
    return {
        "ready": (root / POLICY_FILE).exists(),
        "policy": str(root / POLICY_FILE),
        "subagents": len(subagents),
        "approvals": len(approvals),
        "tokens": len(tokens),
        "audit_events": audit_events,
    }
