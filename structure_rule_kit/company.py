from __future__ import annotations

import json
from pathlib import Path

from .network import _now, _slugify, _write_json
from .runtime import RUNTIME_DIR, runtime_init, stream_event


COMPANY_DIR = RUNTIME_DIR / "company"
METHODS_DIR = COMPANY_DIR / "methods"
ACTIONS_DIR = COMPANY_DIR / "actions"
REPORTS_DIR = COMPANY_DIR / "reports"
METHOD_REGISTRY_FILE = COMPANY_DIR / "office_methods.json"
COMPANY_LOG = COMPANY_DIR / "company_log.jsonl"


DEFAULT_OFFICE_METHODS = {
    "version": "1.6.0",
    "philosophy": "Office methods define how Agent Company roles act. Skills are methods; Agent Company is the governance runtime.",
    "sources": {
        "gstack": {
            "upstream": "https://github.com/garrytan/gstack",
            "fork": "https://github.com/aceroer/gstack",
            "license": "MIT",
            "rule": "Use as inspiration or attributed source material; do not silently copy skill text.",
        }
    },
    "methods": {
        "ceo-review": {
            "office": "CEO",
            "title": "CEO Route Review",
            "source": "gstack-inspired",
            "purpose": "Challenge product route, scope, and convergence before implementation.",
            "inputs": ["issue", "objective", "current plan", "constraints"],
            "allowed_actions": ["read_context", "create_plan", "delegate", "escalate_to_human"],
            "forbidden_actions": ["remote_publish_without_gate", "bypass_p13", "write_unreviewed_release"],
            "expected_artifact": "ceo route verdict with continue/stop/split recommendation",
            "required_verification": ["cite issue or stream", "name owner offices", "state unresolved risks"],
            "publication_authority": "recommend_only",
            "escalation_condition": "scope, safety, or publication authority is unclear",
        },
        "cto-plan": {
            "office": "CTO",
            "title": "CTO Architecture And Implementation Plan",
            "source": "gstack-inspired",
            "purpose": "Lock architecture, implementation route, edge cases, and verification strategy.",
            "inputs": ["issue", "repo map", "relevant files", "test surface"],
            "allowed_actions": ["read_context", "technical_plan", "verification_plan", "risk_table"],
            "forbidden_actions": ["merge", "publish", "ignore_existing_architecture"],
            "expected_artifact": "implementation route and verification matrix",
            "required_verification": ["identify test commands", "list risky files", "state rollback path"],
            "publication_authority": "none",
            "escalation_condition": "architecture affects public API, data model, or security boundary",
        },
        "cso-audit": {
            "office": "CSO",
            "title": "CSO Security And Boundary Audit",
            "source": "gstack-inspired",
            "purpose": "Review secrets, commands, sandbox paths, hooks, and remote-write boundaries.",
            "inputs": ["diff", "commands", "permissions", "publication intent"],
            "allowed_actions": ["read_context", "secret_scan", "command_review", "gate_review"],
            "forbidden_actions": ["approve_own_bypass", "hide_secret_findings", "skip_publication_gate"],
            "expected_artifact": "security verdict with blockers and required gates",
            "required_verification": ["secret scan when applicable", "gate-check for remote actions", "dangerous command review"],
            "publication_authority": "block_or_recommend",
            "escalation_condition": "any remote write, credential, destructive command, or policy bypass appears",
        },
        "cfo-scope": {
            "office": "CFO",
            "title": "CFO Scope And Cost Control",
            "source": "gstack-inspired",
            "purpose": "Prevent small tasks from becoming large; track token, time, and model/API cost risk.",
            "inputs": ["issue", "route", "estimated work", "agent count"],
            "allowed_actions": ["scope_review", "cost_estimate", "overkill_warning"],
            "forbidden_actions": ["expand_scope_without_owner", "hide_budget_risk"],
            "expected_artifact": "scope verdict and cost/effort note",
            "required_verification": ["state task scale", "state stop point", "name expansion risks"],
            "publication_authority": "none",
            "escalation_condition": "task scale or resource cost exceeds original board intent",
        },
        "cro-devex": {
            "office": "CRO",
            "title": "CRO Developer And Reader Experience Review",
            "source": "gstack-inspired",
            "purpose": "Check newcomer clarity, adoption risk, documentation readability, and external perception.",
            "inputs": ["docs", "README", "PR description", "user flow"],
            "allowed_actions": ["readability_review", "onboarding_review", "adoption_risk_note"],
            "forbidden_actions": ["replace_verification", "approve_unreadable_public_docs"],
            "expected_artifact": "reader/adoption verdict with concrete friction points",
            "required_verification": ["name target reader", "identify first-run friction", "state public wording risk"],
            "publication_authority": "recommend_only",
            "escalation_condition": "public-facing wording may misrepresent capability or maturity",
        },
        "qa-verify": {
            "office": "QA",
            "title": "QA Verification Method",
            "source": "gstack-inspired",
            "purpose": "Build and execute a test matrix; record evidence rather than trust implementation claims.",
            "inputs": ["issue", "diff", "test plan", "runtime surface"],
            "allowed_actions": ["run_verification", "browser_or_device_check", "regression_report"],
            "forbidden_actions": ["claim_pass_without_command", "merge", "publish"],
            "expected_artifact": "QA verdict with commands, outputs, and remaining gaps",
            "required_verification": ["commands run", "result status", "known gaps"],
            "publication_authority": "none",
            "escalation_condition": "tests are missing, flaky, or blocked",
        },
        "release-gate": {
            "office": "Release",
            "title": "Release Manager Publication Gate",
            "source": "gstack-inspired",
            "purpose": "Prepare commit, push, PR, release, or deploy actions without bypassing board/P13 gates.",
            "inputs": ["diff", "verification", "approval token", "remote target"],
            "allowed_actions": ["release_checklist", "gate_check", "pr_ready_note"],
            "forbidden_actions": ["commit_without_gate", "push_without_gate", "pr_without_gate", "deploy_without_gate"],
            "expected_artifact": "publication readiness report",
            "required_verification": ["gate-check", "verification summary", "remote target"],
            "publication_authority": "requires_p13_or_token",
            "escalation_condition": "approval token missing or remote target differs from board intent",
        },
        "retro-learn": {
            "office": "COO",
            "title": "Retro And Learning Method",
            "source": "gstack-inspired",
            "purpose": "Turn incidents and trials into process rules, metrics, and future action items.",
            "inputs": ["trace", "reports", "stream events", "incident notes"],
            "allowed_actions": ["retrospective", "lesson_record", "rule_update_recommendation"],
            "forbidden_actions": ["rewrite_history", "hide_governance_failure"],
            "expected_artifact": "retro report with lessons and protocol updates",
            "required_verification": ["cite trace", "classify incident", "name rule change"],
            "publication_authority": "none",
            "escalation_condition": "incident requires protocol or gate change",
        },
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _company_root(path: str = ".") -> Path:
    return _root(path) / COMPANY_DIR


def _append_company_log(path: str, event: str, payload: dict) -> None:
    root = _company_root(path)
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (_root(path) / COMPANY_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _next_id(directory: Path, prefix: str) -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*.json"):
        tail = item.name.removeprefix(f"{prefix}-").removesuffix(".json")
        number = tail.split("-", 1)[0]
        if number.isdigit():
            existing.append(int(number))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def company_init(path: str = ".", force: bool = False) -> dict:
    runtime_init(path)
    root = _root(path)
    for directory in [root / COMPANY_DIR, root / METHODS_DIR, root / ACTIONS_DIR, root / REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    registry_path = root / METHOD_REGISTRY_FILE
    created = False
    if force or not registry_path.exists():
        _write_json(registry_path, DEFAULT_OFFICE_METHODS)
        created = True
    log_path = root / COMPANY_LOG
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    _append_company_log(path, "company_init", {"registry": str(registry_path), "created": created})
    return {"output": str(root / COMPANY_DIR), "registry": str(registry_path), "created": created}


def load_office_methods(path: str = ".") -> dict:
    registry_path = _root(path) / METHOD_REGISTRY_FILE
    if not registry_path.exists():
        company_init(path)
    return json.loads(registry_path.read_text(encoding="utf-8"))


def office_method_list(path: str = ".", office: str = "", source: str = "") -> dict:
    registry = load_office_methods(path)
    methods = registry.get("methods", {})
    filtered = {}
    for name, method in methods.items():
        if office and method.get("office", "").upper() != office.upper():
            continue
        if source and method.get("source", "") != source:
            continue
        filtered[name] = method
    return {"version": registry["version"], "count": len(filtered), "methods": filtered}


def office_method_show(path: str = ".", method: str = "") -> dict:
    registry = load_office_methods(path)
    methods = registry.get("methods", {})
    if method not in methods:
        raise ValueError(f"Unknown office method: {method}")
    return {"method": method, "definition": methods[method], "sources": registry.get("sources", {})}


def office_method_register(
    path: str = ".",
    name: str = "",
    office: str = "",
    title: str = "",
    purpose: str = "",
    source: str = "local",
    expected_artifact: str = "",
    publication_authority: str = "none",
) -> dict:
    company_init(path)
    registry_path = _root(path) / METHOD_REGISTRY_FILE
    registry = load_office_methods(path)
    method_name = _slugify(name or title or office or "office-method")
    payload = {
        "office": office.strip() or "General",
        "title": title.strip() or method_name,
        "source": source.strip() or "local",
        "purpose": purpose.strip() or "Not specified.",
        "inputs": [],
        "allowed_actions": [],
        "forbidden_actions": [],
        "expected_artifact": expected_artifact.strip() or "role report",
        "required_verification": [],
        "publication_authority": publication_authority.strip() or "none",
        "escalation_condition": "Not specified.",
        "registered_at": _now(),
    }
    registry.setdefault("methods", {})[method_name] = payload
    _write_json(registry_path, registry)
    _append_company_log(path, "office_method_register", {"method": method_name, "office": payload["office"], "source": payload["source"]})
    return {"method": method_name, "output": str(registry_path), "definition": payload}


def office_action_start(
    path: str = ".",
    method: str = "",
    office: str = "",
    stream: str = "",
    issue: str = "",
    actor: str = "",
    objective: str = "",
) -> dict:
    company_init(path)
    method_report = office_method_show(path, method)
    definition = method_report["definition"]
    method_office = definition.get("office", "")
    if office and method_office.upper() != office.upper():
        raise ValueError(f"Method {method} belongs to {method_office}, not {office}.")
    root = _root(path)
    action_root = root / ACTIONS_DIR
    action_id = _next_id(action_root, "office-action")
    payload = {
        "id": action_id,
        "method": method,
        "office": method_office,
        "title": definition.get("title", method),
        "stream": stream,
        "issue": issue,
        "actor": actor,
        "objective": objective or definition.get("purpose", "Not specified."),
        "expected_artifact": definition.get("expected_artifact", ""),
        "required_verification": definition.get("required_verification", []),
        "publication_authority": definition.get("publication_authority", "none"),
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = action_root / f"{action_id}-{_slugify(method)}.json"
    _write_json(output, payload)
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="office_action_start",
            actor=actor,
            message=f"{method_office} starts {method}: {payload['objective']}",
            payload={"action": action_id, "method": method, "office": method_office},
        )
    _append_company_log(path, "office_action_start", {"action": action_id, "method": method, "office": method_office, "stream": stream, "issue": issue})
    return {"id": action_id, "output": str(output), "payload": payload}


def _action_path(path: str, action: str) -> Path:
    root = _root(path) / ACTIONS_DIR
    for candidate in root.glob(f"{action}*.json"):
        return candidate
    raise FileNotFoundError(f"office-action/{action}")


def office_action_report(
    path: str = ".",
    action: str = "",
    summary: str = "",
    status: str = "artifact",
    evidence: str = "",
    by: str = "",
) -> dict:
    company_init(path)
    action_path = _action_path(path, action)
    action_payload = json.loads(action_path.read_text(encoding="utf-8"))
    root = _root(path)
    report_root = root / REPORTS_DIR
    report_id = _next_id(report_root, "office-report")
    payload = {
        "id": report_id,
        "action": action_payload["id"],
        "method": action_payload["method"],
        "office": action_payload["office"],
        "stream": action_payload.get("stream", ""),
        "issue": action_payload.get("issue", ""),
        "reported_by": by or action_payload.get("actor", ""),
        "summary": summary or "Not specified.",
        "status": status or "artifact",
        "evidence": evidence,
        "created_at": _now(),
    }
    output = report_root / f"{report_id}-{_slugify(action_payload['method'])}.json"
    _write_json(output, payload)
    action_payload["status"] = payload["status"]
    action_payload["last_report"] = report_id
    action_payload["updated_at"] = _now()
    _write_json(action_path, action_payload)
    stream = action_payload.get("stream", "")
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="office_action_report",
            actor=payload["reported_by"],
            message=f"{payload['office']} {payload['method']} report: {payload['summary']}",
            payload={"action": action_payload["id"], "report": report_id, "status": payload["status"]},
        )
    _append_company_log(path, "office_action_report", {"action": action_payload["id"], "report": report_id, "status": payload["status"]})
    return {"id": report_id, "output": str(output), "payload": payload, "action": action_payload}


def company_status(path: str = ".") -> dict:
    company_init(path)
    root = _root(path)
    actions = list((root / ACTIONS_DIR).glob("*.json"))
    reports = list((root / REPORTS_DIR).glob("*.json"))
    registry = load_office_methods(path)
    log_path = root / COMPANY_LOG
    log_events = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    return {
        "ready": (root / METHOD_REGISTRY_FILE).exists(),
        "methods": len(registry.get("methods", {})),
        "actions": len(actions),
        "reports": len(reports),
        "company_log_events": log_events,
        "registry": str(root / METHOD_REGISTRY_FILE),
    }
