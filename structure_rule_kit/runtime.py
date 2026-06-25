from __future__ import annotations

import json
from pathlib import Path

from .governance import SANDBOXES_DIR, SUBAGENTS_DIR, governance_init, load_policy
from .network import _ensure_network, _find_item, _now, _slugify, _write_json


RUNTIME_DIR = Path("structure/worknet/runtime")
STREAMS_DIR = RUNTIME_DIR / "streams"
ROLES_DIR = RUNTIME_DIR / "roles"
ASSIGNMENTS_DIR = RUNTIME_DIR / "assignments"
CEO_PLANS_DIR = RUNTIME_DIR / "ceo_plans"
EXECUTIVES_DIR = RUNTIME_DIR / "executives"
APPOINTMENTS_DIR = EXECUTIVES_DIR / "appointments"
EXECUTIVE_REPORTS_DIR = EXECUTIVES_DIR / "reports"
ROLE_REPORTS_DIR = RUNTIME_DIR / "role_reports"
EXECUTIVE_BOARD_FILE = EXECUTIVES_DIR / "executive_board.json"
CURRENT_STREAM = RUNTIME_DIR / "current_stream.json"
ROLE_FILE = ROLES_DIR / "corporate_levels.json"
RUNTIME_LOG = RUNTIME_DIR / "runtime_log.jsonl"


CORPORATE_LEVELS = {
    "version": "1.4",
    "philosophy": "Stream-structured runtime: work advances through auditable streams, not session trees.",
    "supervision": {
        "human_supervisor": "P13",
        "ceo_agent": "P12",
        "rule": "P12 may coordinate globally but cannot override P13 gates.",
    },
    "levels": {
        "P1": {
            "title": "Observer Intern",
            "scope": "Read-only local context.",
            "capabilities": ["read_context"],
            "governance_permission": "plan",
        },
        "P2": {
            "title": "Summarizer",
            "scope": "Summarize structure, issues, and streams.",
            "capabilities": ["read_context", "summarize"],
            "governance_permission": "plan",
        },
        "P3": {
            "title": "Draft Assistant",
            "scope": "Create local plans, task drafts, and notes.",
            "capabilities": ["read_context", "summarize", "draft"],
            "governance_permission": "draft",
        },
        "P4": {
            "title": "Sandbox Worker",
            "scope": "Edit approved sandbox and worknet files.",
            "capabilities": ["read_context", "draft", "sandbox_write"],
            "governance_permission": "draft",
        },
        "P5": {
            "title": "Read Command Worker",
            "scope": "Run read-only inspection commands.",
            "capabilities": ["read_context", "sandbox_write", "read_commands"],
            "governance_permission": "draft",
        },
        "P6": {
            "title": "Verification Worker",
            "scope": "Run verification commands under approval policy.",
            "capabilities": ["read_context", "sandbox_write", "read_commands", "verify_commands"],
            "governance_permission": "apply",
        },
        "P7": {
            "title": "Scoped Implementer",
            "scope": "Prepare scoped source edits after approval.",
            "capabilities": ["verify_commands", "scoped_source_edits"],
            "governance_permission": "apply",
        },
        "P8": {
            "title": "Worknet Operator",
            "scope": "Create and update local issue, PR, milestone, and project objects.",
            "capabilities": ["scoped_source_edits", "local_worknet_write"],
            "governance_permission": "apply",
        },
        "P9": {
            "title": "Lead Agent",
            "scope": "Coordinate multiple subagents and merge local evidence.",
            "capabilities": ["local_worknet_write", "coordinate_subagents"],
            "governance_permission": "apply",
        },
        "P10": {
            "title": "Manager Agent",
            "scope": "Approve low-risk local tool execution within policy.",
            "capabilities": ["coordinate_subagents", "low_risk_approval"],
            "governance_permission": "apply",
        },
        "P11": {
            "title": "Remote Action Preparer",
            "scope": "Prepare GitHub or external actions for human approval.",
            "capabilities": ["low_risk_approval", "prepare_remote_actions"],
            "governance_permission": "apply",
        },
        "P12": {
            "title": "CEO Agent",
            "scope": "Global planning, delegation, stream routing, and escalation.",
            "capabilities": ["prepare_remote_actions", "global_orchestration", "escalate_to_human"],
            "governance_permission": "apply",
        },
        "P13": {
            "title": "Human Supervisor",
            "scope": "Final owner. May grant, revoke, take over, or redirect any stream.",
            "capabilities": ["global_orchestration", "human_takeover", "grant_capability", "revoke_capability"],
            "governance_permission": "owner",
        },
    },
}


EXECUTIVE_BOARD = {
    "version": "1.4.1",
    "rule": "CEO agents may appoint executive offices. P13 human supervisors may override any appointment.",
    "ceo_level": "P12",
    "human_supervisor_level": "P13",
    "offices": {
        "COO": {
            "title": "Chief Operating Officer Agent",
            "default_level": "P11",
            "domain": "Operations, stream progress, issue/project flow, and delivery cadence.",
            "capabilities": ["stream_operations", "issue_project_routing", "delivery_tracking"],
        },
        "CTO": {
            "title": "Chief Technology Officer Agent",
            "default_level": "P11",
            "domain": "Architecture, implementation routes, verification strategy, and technical risk.",
            "capabilities": ["architecture_review", "implementation_route", "verification_strategy"],
        },
        "CFO": {
            "title": "Chief Financial Officer Agent",
            "default_level": "P10",
            "domain": "Token budget, model/API cost, resource use, and usage reporting.",
            "capabilities": ["cost_tracking", "token_budgeting", "resource_reporting"],
        },
        "CSO": {
            "title": "Chief Security Officer Agent",
            "default_level": "P11",
            "domain": "Governance, sandbox, secret exposure, and permission risk.",
            "capabilities": ["security_review", "sandbox_policy", "secret_risk_review"],
        },
        "CRO": {
            "title": "Chief Research Officer Agent",
            "default_level": "P10",
            "domain": "Research routes, evidence quality, knowledge capture, and open questions.",
            "capabilities": ["research_route", "evidence_review", "knowledge_capture"],
        },
    },
    "appointments": {},
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _runtime_root(path: str = ".") -> Path:
    return _root(path) / RUNTIME_DIR


def _append_runtime_log(path: str, event: str, payload: dict) -> None:
    root = _runtime_root(path)
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (_root(path) / RUNTIME_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _next_record_id(directory: Path, prefix: str, suffix: str) -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*{suffix}"):
        stem = item.name.removeprefix(f"{prefix}-").removesuffix(suffix)
        number = stem.split("-", 1)[0]
        if number.isdigit():
            existing.append(int(number))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def runtime_init(path: str = ".", force: bool = False) -> dict:
    governance_init(path)
    root = _root(path)
    for directory in [
        root / RUNTIME_DIR,
        root / STREAMS_DIR,
        root / ROLES_DIR,
        root / ASSIGNMENTS_DIR,
        root / CEO_PLANS_DIR,
        root / EXECUTIVES_DIR,
        root / APPOINTMENTS_DIR,
        root / EXECUTIVE_REPORTS_DIR,
        root / ROLE_REPORTS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
    role_path = root / ROLE_FILE
    created_roles = False
    if force or not role_path.exists():
        _write_json(role_path, CORPORATE_LEVELS)
        created_roles = True
    board_path = root / EXECUTIVE_BOARD_FILE
    created_board = False
    if force or not board_path.exists():
        _write_json(board_path, EXECUTIVE_BOARD)
        created_board = True
    log_path = root / RUNTIME_LOG
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    _append_runtime_log(path, "runtime_init", {"roles": str(role_path), "created_roles": created_roles, "executive_board": str(board_path), "created_board": created_board})
    return {"output": str(root / RUNTIME_DIR), "roles": str(role_path), "executive_board": str(board_path), "created_roles": created_roles, "created_board": created_board}


def load_roles(path: str = ".") -> dict:
    role_path = _root(path) / ROLE_FILE
    if not role_path.exists():
        runtime_init(path)
    return json.loads(role_path.read_text(encoding="utf-8"))


def role_show(path: str = ".", level: str = "") -> dict:
    roles = load_roles(path)
    if level:
        return {"version": roles["version"], "level": level, "role": roles["levels"][level]}
    return roles


def load_executive_board(path: str = ".") -> dict:
    board_path = _root(path) / EXECUTIVE_BOARD_FILE
    if not board_path.exists():
        runtime_init(path)
    return json.loads(board_path.read_text(encoding="utf-8"))


def executive_board(path: str = ".", office: str = "") -> dict:
    board = load_executive_board(path)
    if office:
        office = office.upper()
        return {
            "version": board["version"],
            "office": office,
            "definition": board["offices"][office],
            "appointment": board.get("appointments", {}).get(office, {}),
        }
    return board


def _load_subagent(path: str, subagent: str) -> tuple[Path, dict]:
    root = _root(path) / SUBAGENTS_DIR
    for candidate in root.glob(f"{subagent}*.json"):
        return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"subagent/{subagent}")


def _level_number(level: str) -> int:
    return int(level.upper().removeprefix("P"))


def level_allows(path: str = ".", level: str = "P1", capability: str = "") -> dict:
    roles = load_roles(path)
    levels = roles["levels"]
    level = level.upper()
    if level not in levels:
        raise ValueError(f"Unknown level: {level}")
    allowed = []
    for name, payload in levels.items():
        if _level_number(name) <= _level_number(level):
            allowed.extend(payload.get("capabilities", []))
    allowed = sorted(dict.fromkeys(allowed))
    ok = capability in allowed if capability else True
    return {"ok": ok, "level": level, "capability": capability, "allowed_capabilities": allowed}


def agent_promote(path: str = ".", subagent: str = "", level: str = "P3", title: str = "") -> dict:
    runtime_init(path)
    roles = load_roles(path)
    policy = load_policy(path)
    level = level.upper()
    if level not in roles["levels"]:
        raise ValueError(f"Unknown level: {level}")
    subagent_path, payload = _load_subagent(path, subagent)
    role = roles["levels"][level]
    payload["corporate_level"] = level
    payload["corporate_title"] = title or role["title"]
    payload["permission"] = role["governance_permission"] if role["governance_permission"] != "owner" else payload.get("permission", "apply")
    payload["updated_at"] = _now()
    _write_json(subagent_path, payload)
    sandbox_path = _root(path) / SANDBOXES_DIR / f"{subagent}.json"
    if sandbox_path.exists() and payload["permission"] in policy["permissions"]:
        sandbox = json.loads(sandbox_path.read_text(encoding="utf-8"))
        sandbox["permission"] = payload["permission"]
        sandbox["command_levels"] = policy["permissions"][payload["permission"]]["command_levels"]
        sandbox["github_apply"] = policy["permissions"][payload["permission"]]["github_apply"]
        sandbox["updated_at"] = _now()
        _write_json(sandbox_path, sandbox)
    _append_runtime_log(path, "agent_promote", {"subagent": subagent, "level": level, "title": payload["corporate_title"]})
    return {"id": subagent, "level": level, "output": str(subagent_path), "payload": payload}


def _actor_level(path: str, actor: str) -> str:
    if not actor or actor.lower() in {"human", "owner", "p13"}:
        return "P13"
    _actor_path, actor_payload = _load_subagent(path, actor)
    return actor_payload.get("corporate_level", "P3")


def _can_appoint(path: str, by: str) -> bool:
    return _level_number(_actor_level(path, by)) >= 12


def executive_appoint(
    path: str = ".",
    office: str = "",
    subagent: str = "",
    by: str = "",
    level: str = "",
    mandate: str = "",
) -> dict:
    runtime_init(path)
    office = office.upper()
    board = load_executive_board(path)
    if office not in board["offices"]:
        raise ValueError(f"Unknown executive office: {office}")
    if not _can_appoint(path, by):
        raise PermissionError("Executive appointments require a P12 CEO agent or P13 human supervisor.")
    office_def = board["offices"][office]
    appointed_level = (level or office_def["default_level"]).upper()
    promoted = agent_promote(path, subagent=subagent, level=appointed_level, title=office_def["title"])
    root = _root(path)
    appointment_root = root / APPOINTMENTS_DIR
    appointment_id = _next_record_id(appointment_root, "appointment", ".json")
    payload = {
        "id": appointment_id,
        "office": office,
        "title": office_def["title"],
        "subagent": subagent,
        "appointed_by": by or "P13",
        "level": appointed_level,
        "mandate": mandate or office_def["domain"],
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = appointment_root / f"{appointment_id}-{office.lower()}.json"
    _write_json(output, payload)
    board.setdefault("appointments", {})[office] = {
        "appointment": appointment_id,
        "subagent": subagent,
        "level": appointed_level,
        "appointed_by": by or "P13",
        "mandate": payload["mandate"],
        "updated_at": _now(),
    }
    _write_json(root / EXECUTIVE_BOARD_FILE, board)
    _append_runtime_log(path, "executive_appoint", {"office": office, "subagent": subagent, "by": by, "appointment": appointment_id})
    return {"id": appointment_id, "office": office, "output": str(output), "promoted": promoted, "payload": payload}


def executive_delegate(
    path: str = ".",
    office: str = "",
    stream: str = "",
    issue: str = "",
    duty: str = "",
    by: str = "",
) -> dict:
    runtime_init(path)
    office = office.upper()
    board = load_executive_board(path)
    appointment = board.get("appointments", {}).get(office, {})
    if not appointment:
        raise ValueError(f"No active appointment for {office}")
    if by and not _can_appoint(path, by):
        raise PermissionError("Executive delegation requires a P12 CEO agent or P13 human supervisor.")
    assignment = assignment_create(
        path,
        subagent=appointment["subagent"],
        stream=stream,
        issue=issue,
        duty=duty or f"{office} owns {board['offices'][office]['domain']}",
        level=appointment["level"],
    )
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="executive_delegate",
            actor=by or "P13",
            message=f"{office} delegated to {appointment['subagent']}",
            payload={"assignment": assignment["id"], "office": office},
        )
    _append_runtime_log(path, "executive_delegate", {"office": office, "assignment": assignment["id"], "stream": stream, "issue": issue})
    return {"office": office, "assignment": assignment}


def executive_report(
    path: str = ".",
    office: str = "",
    stream: str = "",
    summary: str = "",
    by: str = "",
) -> dict:
    runtime_init(path)
    office = office.upper()
    board = load_executive_board(path)
    if office not in board["offices"]:
        raise ValueError(f"Unknown executive office: {office}")
    appointment = board.get("appointments", {}).get(office, {})
    report_root = _root(path) / EXECUTIVE_REPORTS_DIR
    report_id = _next_record_id(report_root, f"{office.lower()}-report", ".json")
    payload = {
        "id": report_id,
        "office": office,
        "title": board["offices"][office]["title"],
        "stream": stream,
        "reported_by": by or appointment.get("subagent", ""),
        "appointed_subagent": appointment.get("subagent", ""),
        "summary": summary or "Not specified.",
        "created_at": _now(),
    }
    output = report_root / f"{report_id}.json"
    _write_json(output, payload)
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="executive_report",
            actor=payload["reported_by"],
            message=f"{office} report: {payload['summary']}",
            payload={"report": str(output), "office": office},
        )
    _append_runtime_log(path, "executive_report", {"office": office, "stream": stream, "report": str(output)})
    return {"id": report_id, "office": office, "output": str(output), "payload": payload}


def role_report(
    path: str = ".",
    role: str = "",
    stream: str = "",
    summary: str = "",
    by: str = "",
    status: str = "artifact",
) -> dict:
    runtime_init(path)
    normalized_role = _slugify(role or "role")
    report_root = _root(path) / ROLE_REPORTS_DIR
    report_id = _next_record_id(report_root, f"{normalized_role}-report", ".json")
    payload = {
        "id": report_id,
        "role": role.strip() or "role",
        "stream": stream,
        "reported_by": by,
        "summary": summary or "Not specified.",
        "status": status or "artifact",
        "created_at": _now(),
    }
    output = report_root / f"{report_id}.json"
    _write_json(output, payload)
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="role_report",
            actor=by,
            message=f"{payload['role']} report: {payload['summary']}",
            payload={"report": str(output), "role": payload["role"], "status": payload["status"]},
        )
    _append_runtime_log(
        path,
        "role_report",
        {"role": payload["role"], "stream": stream, "report": str(output), "status": payload["status"]},
    )
    return {"id": report_id, "role": payload["role"], "output": str(output), "payload": payload}


def assignment_create(
    path: str = ".",
    subagent: str = "",
    stream: str = "",
    issue: str = "",
    duty: str = "",
    level: str = "",
) -> dict:
    runtime_init(path)
    root = _root(path)
    if subagent:
        _subagent_path, subagent_payload = _load_subagent(path, subagent)
        level = level or subagent_payload.get("corporate_level", "P3")
    assignment_root = root / ASSIGNMENTS_DIR
    assignment_id = _next_record_id(assignment_root, "assignment", ".json")
    payload = {
        "id": assignment_id,
        "subagent": subagent,
        "stream": stream,
        "issue": issue,
        "duty": duty or "Not specified.",
        "level": level or "P3",
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = assignment_root / f"{assignment_id}.json"
    _write_json(output, payload)
    _append_runtime_log(path, "assignment_create", {"assignment": assignment_id, "subagent": subagent, "stream": stream, "issue": issue})
    return {"id": assignment_id, "output": str(output), "payload": payload}


def _stream_path(path: str, stream: str) -> Path:
    stream_root = _root(path) / STREAMS_DIR
    for candidate in stream_root.glob(f"{stream}*.jsonl"):
        return candidate
    direct = stream_root / f"{stream}.jsonl"
    if direct.exists():
        return direct
    raise FileNotFoundError(f"stream/{stream}")


def _append_stream_event(stream_path: Path, event_type: str, payload: dict) -> dict:
    lines = stream_path.read_text(encoding="utf-8").splitlines() if stream_path.exists() else []
    event = {
        "event_id": f"event-{len(lines) + 1:04d}",
        "timestamp": _now(),
        "type": event_type,
        **payload,
    }
    with stream_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    return event


def stream_start(
    path: str = ".",
    issue: str = "",
    title: str = "",
    ceo_agent: str = "",
    supervisor: str = "human",
) -> dict:
    runtime_init(path)
    network_root = _ensure_network(path)
    issue_payload = {}
    if issue:
        _issue_path, issue_payload = _find_item(network_root, "issues", issue)
    stream_root = _root(path) / STREAMS_DIR
    stream_id = _next_record_id(stream_root, "stream", ".jsonl")
    stream_title = title or issue_payload.get("title", issue or stream_id)
    output = stream_root / f"{stream_id}.jsonl"
    output.write_text("", encoding="utf-8")
    event = _append_stream_event(
        output,
        "stream_started",
        {
            "stream": stream_id,
            "issue": issue,
            "title": stream_title,
            "ceo_agent": ceo_agent,
            "human_supervisor": supervisor,
            "state": "active",
            "philosophy": "stream",
        },
    )
    current = {
        "stream": stream_id,
        "issue": issue,
        "title": stream_title,
        "ceo_agent": ceo_agent,
        "human_supervisor": supervisor,
        "state": "active",
        "updated_at": _now(),
    }
    _write_json(_root(path) / CURRENT_STREAM, current)
    _append_runtime_log(path, "stream_start", {"stream": stream_id, "issue": issue, "output": str(output)})
    return {"id": stream_id, "output": str(output), "event": event, "current": str(_root(path) / CURRENT_STREAM)}


def stream_event(
    path: str = ".",
    stream: str = "",
    event_type: str = "observation",
    message: str = "",
    actor: str = "",
    payload: dict | None = None,
) -> dict:
    runtime_init(path)
    stream_path = _stream_path(path, stream)
    event = _append_stream_event(
        stream_path,
        event_type,
        {
            "actor": actor,
            "message": message,
            "payload": payload or {},
        },
    )
    _append_runtime_log(path, "stream_event", {"stream": stream, "event_type": event_type, "event_id": event["event_id"]})
    return {"stream": stream, "output": str(stream_path), "event": event}


def _load_stream_events(path: str, stream: str) -> list[dict]:
    stream_path = _stream_path(path, stream)
    events = []
    for line in stream_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def ceo_plan(
    path: str = ".",
    issue: str = "",
    stream: str = "",
    ceo_agent: str = "",
    objective: str = "",
) -> dict:
    runtime_init(path)
    if not stream:
        stream = stream_start(path, issue=issue, ceo_agent=ceo_agent)["id"]
    network_root = _ensure_network(path)
    issue_payload = {}
    if issue:
        _issue_path, issue_payload = _find_item(network_root, "issues", issue)
    plan_root = _root(path) / CEO_PLANS_DIR
    plan_id = _next_record_id(plan_root, "ceo-plan", ".json")
    plan = {
        "id": plan_id,
        "stream": stream,
        "issue": issue,
        "ceo_agent": ceo_agent,
        "created_at": _now(),
        "objective": objective or issue_payload.get("title", issue or "Not specified."),
        "supervision": {
            "human": "P13 final supervisor",
            "ceo": "P12 global coordinator",
        },
        "delegation": [
            {"level": "P2", "role": "summarize current state"},
            {"level": "P3", "role": "draft implementation route"},
            {"level": "P6", "role": "verify commands after approval"},
            {"level": "P9", "role": "merge subagent evidence"},
            {"level": "P13", "role": "approve high-risk or external actions"},
        ],
        "gates": [
            "No remote action without explicit approval.",
            "No live model call without a capability token.",
            "No source edit outside assigned scope.",
            "Human takeover can pause or redirect the stream at any point.",
        ],
    }
    output = plan_root / f"{plan_id}-{stream}.json"
    _write_json(output, plan)
    event = stream_event(path, stream=stream, event_type="ceo_plan", message=plan["objective"], actor=ceo_agent or "ceo-agent", payload={"plan": str(output)})
    _append_runtime_log(path, "ceo_plan", {"stream": stream, "issue": issue, "plan": str(output)})
    return {"id": plan_id, "stream": stream, "output": str(output), "event": event["event"], "payload": plan}


def human_takeover(path: str = ".", stream: str = "", reason: str = "", actor: str = "human") -> dict:
    runtime_init(path)
    event = stream_event(
        path,
        stream=stream,
        event_type="human_takeover",
        message=reason or "Human supervisor took over the stream.",
        actor=actor,
        payload={"level": "P13", "state": "human_control"},
    )
    current_path = _root(path) / CURRENT_STREAM
    if current_path.exists():
        current = json.loads(current_path.read_text(encoding="utf-8"))
        if current.get("stream") == stream:
            current["state"] = "human_control"
            current["updated_at"] = _now()
            current["takeover_reason"] = reason
            _write_json(current_path, current)
    _append_runtime_log(path, "human_takeover", {"stream": stream, "actor": actor})
    return event


def runtime_status(path: str = ".") -> dict:
    runtime_init(path)
    root = _root(path)
    streams = list((root / STREAMS_DIR).glob("*.jsonl"))
    assignments = list((root / ASSIGNMENTS_DIR).glob("*.json"))
    plans = list((root / CEO_PLANS_DIR).glob("*.json"))
    appointments = list((root / APPOINTMENTS_DIR).glob("*.json"))
    executive_reports = list((root / EXECUTIVE_REPORTS_DIR).glob("*.json"))
    role_reports = list((root / ROLE_REPORTS_DIR).glob("*.json"))
    current_path = root / CURRENT_STREAM
    current = json.loads(current_path.read_text(encoding="utf-8")) if current_path.exists() else None
    log_path = root / RUNTIME_LOG
    log_events = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    return {
        "ready": (root / ROLE_FILE).exists(),
        "streams": len(streams),
        "assignments": len(assignments),
        "ceo_plans": len(plans),
        "executive_appointments": len(appointments),
        "executive_reports": len(executive_reports),
        "role_reports": len(role_reports),
        "current": current,
        "runtime_events": log_events,
        "roles": str(root / ROLE_FILE),
    }


def stream_show(path: str = ".", stream: str = "") -> dict:
    events = _load_stream_events(path, stream)
    return {"stream": stream, "events": events, "count": len(events), "output": str(_stream_path(path, stream))}
