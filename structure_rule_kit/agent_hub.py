from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

from .governance import SUBAGENTS_DIR, command_check, governance_init, sanitize_environment
from .network import _ensure_network, _find_item, _now, _slugify, _write_json
from .runtime import role_report, runtime_init, stream_event


AGENT_HUB_DIR = Path("structure/worknet/agent_hub")
SPAWNS_DIR = AGENT_HUB_DIR / "spawns"
PROMPTS_DIR = AGENT_HUB_DIR / "prompts"
RUNS_DIR = AGENT_HUB_DIR / "runs"
INGEST_DIR = AGENT_HUB_DIR / "ingest"
EVENT_LOG = AGENT_HUB_DIR / "agent_hub_log.jsonl"


RUNNER_ADAPTERS = {
    "local": {
        "kind": "subprocess",
        "summary": "Run an explicit local argv command under GNW command checks.",
        "requires_explicit_command": True,
        "event_source": "stdout-stderr",
    },
    "codex": {
        "kind": "external-cli",
        "summary": "Use Codex CLI as a worker agent. GNW supplies the prompt file and ingests the report.",
        "requires_explicit_command": True,
        "entrypoint_hint": "codex exec",
        "event_source": "adapter-output",
    },
    "pi": {
        "kind": "external-cli",
        "summary": "Use Pi as a worker runtime. GNW supplies task context and expects a role report artifact.",
        "requires_explicit_command": True,
        "entrypoint_hint": "pi",
        "event_source": "adapter-output",
    },
    "mini-swe": {
        "kind": "external-cli",
        "summary": "Use mini-swe-agent or a compatible SWE runner for issue-style coding work.",
        "requires_explicit_command": True,
        "entrypoint_hint": "mini-swe-agent",
        "event_source": "adapter-output",
    },
    "openhands": {
        "kind": "server-adapter",
        "summary": "Use an OpenHands agent server as the execution backend.",
        "requires_explicit_command": True,
        "entrypoint_hint": "openhands or agent server client",
        "event_source": "server-events",
    },
    "sandbox-agent": {
        "kind": "http-adapter",
        "summary": "Use Sandbox Agent as a universal HTTP/SSE adapter for Codex, Claude Code, OpenCode, Amp, Cursor, or Pi.",
        "requires_explicit_command": True,
        "entrypoint_hint": "sandbox-agent HTTP API client",
        "event_source": "http-sse-events",
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _hub_root(path: str = ".") -> Path:
    return _root(path) / AGENT_HUB_DIR


def _append_hub_log(path: str, event: str, payload: dict) -> None:
    root = _hub_root(path)
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (_root(path) / EVENT_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _next_hub_id(directory: Path, prefix: str) -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*.json"):
        stem = item.name.removeprefix(f"{prefix}-").removesuffix(".json")
        number = stem.split("-", 1)[0]
        if number.isdigit():
            existing.append(int(number))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def _load_json_by_id(root: Path, directory: Path, item_id: str) -> tuple[Path, dict]:
    for path in (root / directory).glob(f"{item_id}*.json"):
        return path, json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"{directory}/{item_id}")


def _load_subagent(path: str, subagent: str) -> dict:
    if not subagent:
        return {}
    root = _root(path) / SUBAGENTS_DIR
    for candidate in root.glob(f"{subagent}*.json"):
        return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"subagent/{subagent}")


def _read_issue(path: str, issue: str) -> dict:
    if not issue:
        return {}
    network_root = _ensure_network(path)
    _issue_path, payload = _find_item(network_root, "issues", issue)
    return {
        "id": payload.get("id", issue),
        "title": payload.get("title", ""),
        "body": payload.get("body", ""),
        "labels": payload.get("labels", []),
        "status": payload.get("status", ""),
    }


def _render_prompt(payload: dict) -> str:
    return "\n".join(
        [
            f"# GNW Subagent Spawn: {payload['id']}",
            "",
            "You are a worker agent launched by Agent GitHub Worknet Hub.",
            "Treat this as a bounded assignment, not a request for autonomous publication.",
            "",
            "## Assignment",
            f"- Role: {payload['role']}",
            f"- Runner: {payload['runner']}",
            f"- Subagent: {payload['subagent'] or 'external'}",
            f"- Issue: {payload['issue'] or 'not linked'}",
            f"- Stream: {payload['stream'] or 'not linked'}",
            "",
            "## Task",
            payload["task"],
            "",
            "## Issue Context",
            json.dumps(payload.get("issue_context", {}), indent=2),
            "",
            "## Governance Contract",
            "- Stay inside the task scope.",
            "- Do not push, open PRs, comment remotely, or publish unless a separate gate approves it.",
            "- Leave a concise report with files inspected or changed, checks run, and remaining risks.",
            "- If blocked, report the blocker instead of bypassing GNW gates.",
            "",
            "## Expected Output",
            "- summary",
            "- files_changed",
            "- checks_run",
            "- risks",
            "- next_action",
            "",
        ]
    )


def agent_hub_init(path: str = ".", force: bool = False) -> dict:
    runtime_init(path)
    root = _root(path)
    for directory in [root / AGENT_HUB_DIR, root / SPAWNS_DIR, root / PROMPTS_DIR, root / RUNS_DIR, root / INGEST_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    log_path = root / EVENT_LOG
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    adapters_path = root / AGENT_HUB_DIR / "runner_adapters.json"
    created = False
    if force or not adapters_path.exists():
        _write_json(adapters_path, {"version": "1.5.3", "adapters": RUNNER_ADAPTERS})
        created = True
    _append_hub_log(path, "agent_hub_init", {"adapters": str(adapters_path), "created": created})
    return {"output": str(root / AGENT_HUB_DIR), "adapters": str(adapters_path), "created": created}


def runner_adapters(path: str = ".") -> dict:
    agent_hub_init(path)
    adapters_path = _root(path) / AGENT_HUB_DIR / "runner_adapters.json"
    return json.loads(adapters_path.read_text(encoding="utf-8"))


def subagent_spawn(
    path: str = ".",
    subagent: str = "",
    runner: str = "local",
    role: str = "",
    issue: str = "",
    stream: str = "",
    task: str = "",
    command: str = "",
) -> dict:
    agent_hub_init(path)
    adapters = runner_adapters(path).get("adapters", {})
    if runner not in adapters:
        raise ValueError(f"Unknown runner adapter: {runner}")
    subagent_payload = _load_subagent(path, subagent)
    issue_context = _read_issue(path, issue or subagent_payload.get("linked_issue", ""))
    spawn_root = _root(path) / SPAWNS_DIR
    prompt_root = _root(path) / PROMPTS_DIR
    spawn_id = _next_hub_id(spawn_root, "spawn")
    role_name = role or subagent_payload.get("name", "") or "worker"
    prompt_path = prompt_root / f"{spawn_id}-{_slugify(role_name)}.md"
    payload = {
        "id": spawn_id,
        "version": "1.5.3",
        "status": "spawned",
        "runner": runner,
        "adapter": adapters[runner],
        "subagent": subagent,
        "role": role_name,
        "issue": issue or issue_context.get("id", ""),
        "stream": stream,
        "task": task.strip() or subagent_payload.get("goal") or "Produce a bounded GNW worker report.",
        "command": command,
        "prompt": str(prompt_path),
        "issue_context": issue_context,
        "created_at": _now(),
        "governance": {
            "remote_publication_default": "blocked",
            "requires_gate_for": ["commit", "remote-push", "gh-pr-create", "gh-issue-comment"],
            "ingest_required": True,
        },
    }
    prompt_path.write_text(_render_prompt(payload), encoding="utf-8")
    output = spawn_root / f"{spawn_id}-{runner}-{_slugify(role_name)}.json"
    _write_json(output, payload)
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="subagent_spawn",
            actor=subagent,
            message=f"Spawned {role_name} via {runner}.",
            payload={"spawn": spawn_id, "runner": runner, "prompt": str(prompt_path)},
        )
    _append_hub_log(path, "subagent_spawn", {"spawn": spawn_id, "runner": runner, "subagent": subagent, "stream": stream})
    return {"id": spawn_id, "output": str(output), "prompt": str(prompt_path), "payload": payload}


def subagent_run(
    path: str = ".",
    spawn: str = "",
    apply: bool = False,
    command: str = "",
    timeout: int = 120,
) -> dict:
    agent_hub_init(path)
    root = _root(path)
    _spawn_path, payload = _load_json_by_id(root, SPAWNS_DIR, spawn)
    run_root = root / RUNS_DIR
    run_id = _next_hub_id(run_root, "run")
    selected_command = command or payload.get("command", "")
    check = command_check(path, command=selected_command or "echo dry-run", subagent=payload.get("subagent", "")) if selected_command else {"ok": False, "status": "missing-command"}
    run_payload = {
        "id": run_id,
        "spawn": spawn,
        "runner": payload.get("runner", ""),
        "subagent": payload.get("subagent", ""),
        "command": selected_command,
        "apply": apply,
        "created_at": _now(),
        "command_check": check,
        "status": "dry-run",
        "returncode": None,
        "stdout": "",
        "stderr": "",
    }
    if apply:
        if not selected_command:
            run_payload["status"] = "missing-command"
        elif not check.get("ok"):
            run_payload["status"] = "command-denied"
        else:
            env_report = sanitize_environment(dict(os.environ))
            try:
                completed = subprocess.run(
                    shlex.split(selected_command),
                    cwd=str(root),
                    env=env_report["env"],
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
                run_payload.update(
                    {
                        "status": "completed" if completed.returncode == 0 else "failed",
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "removed_env": sorted(env_report["removed"]),
                    }
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                run_payload.update({"status": "failed", "stderr": str(exc), "returncode": 124})
    output = run_root / f"{run_id}-{spawn}.json"
    _write_json(output, run_payload)
    if payload.get("stream"):
        stream_event(
            path,
            stream=payload["stream"],
            event_type="subagent_run",
            actor=payload.get("subagent", ""),
            message=f"{run_payload['status']}: {payload.get('runner', '')} for {spawn}.",
            payload={"run": run_id, "spawn": spawn, "status": run_payload["status"]},
        )
    _append_hub_log(path, "subagent_run", {"run": run_id, "spawn": spawn, "status": run_payload["status"]})
    return {"id": run_id, "output": str(output), "payload": run_payload, "ok": run_payload["status"] in {"dry-run", "completed"}}


def subagent_ingest(
    path: str = ".",
    spawn: str = "",
    summary: str = "",
    artifact: str = "",
    status: str = "artifact",
    by: str = "",
) -> dict:
    agent_hub_init(path)
    root = _root(path)
    spawn_path, payload = _load_json_by_id(root, SPAWNS_DIR, spawn)
    ingest_root = root / INGEST_DIR
    ingest_id = _next_hub_id(ingest_root, "ingest")
    report = role_report(
        path,
        role=payload.get("role", "worker"),
        stream=payload.get("stream", ""),
        summary=summary or "Subagent output ingested.",
        by=by or payload.get("subagent", ""),
        status=status,
    )
    payload["status"] = "ingested"
    payload["updated_at"] = _now()
    _write_json(spawn_path, payload)
    ingest_payload = {
        "id": ingest_id,
        "spawn": spawn,
        "subagent": payload.get("subagent", ""),
        "role": payload.get("role", ""),
        "summary": summary or "Subagent output ingested.",
        "artifact": artifact,
        "status": status,
        "role_report": report["id"],
        "role_report_path": report["output"],
        "created_at": _now(),
    }
    output = ingest_root / f"{ingest_id}-{spawn}.json"
    _write_json(output, ingest_payload)
    _append_hub_log(path, "subagent_ingest", {"ingest": ingest_id, "spawn": spawn, "role_report": report["id"]})
    return {"id": ingest_id, "output": str(output), "role_report": report, "payload": ingest_payload}


def subagent_events(path: str = ".", spawn: str = "") -> dict:
    agent_hub_init(path)
    log_path = _root(path) / EVENT_LOG
    events = []
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if not spawn or event.get("spawn") == spawn:
                events.append(event)
    return {"events": events, "count": len(events), "spawn": spawn}
