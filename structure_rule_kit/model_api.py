from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from .governance import TOKENS_DIR, governance_init, token_is_active
from .network import _ensure_network, _find_item, _next_id, _now, _write_json


MODEL_API_DIR = Path("structure/worknet/model_api")
PROVIDERS_FILE = MODEL_API_DIR / "providers.json"
REQUESTS_DIR = MODEL_API_DIR / "requests"
RESPONSES_DIR = MODEL_API_DIR / "responses"


DEFAULT_PROVIDERS = {
    "version": "1.3",
    "providers": {
        "openai": {
            "type": "chat-completions",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "api_key_env": "OPENAI_API_KEY",
            "default_model": "",
            "notes": "Set default_model or pass --model before making a live call.",
        }
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _model_root(path: str = ".") -> Path:
    return _root(path) / MODEL_API_DIR


def _append_model_log(path: str, event: str, payload: dict) -> None:
    root = _model_root(path)
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (root / "model_api_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def model_config_init(path: str = ".", force: bool = False) -> dict:
    governance_init(path)
    root = _root(path)
    for directory in [root / MODEL_API_DIR, root / REQUESTS_DIR, root / RESPONSES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    providers_path = root / PROVIDERS_FILE
    created = False
    if force or not providers_path.exists():
        _write_json(providers_path, DEFAULT_PROVIDERS)
        created = True
    log_path = root / MODEL_API_DIR / "model_api_log.jsonl"
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    _append_model_log(path, "model_config_init", {"providers": str(providers_path), "created": created})
    return {"output": str(root / MODEL_API_DIR), "providers": str(providers_path), "created": created}


def load_model_providers(path: str = ".") -> dict:
    providers_path = _root(path) / PROVIDERS_FILE
    if not providers_path.exists():
        model_config_init(path)
    return json.loads(providers_path.read_text(encoding="utf-8"))


def model_provider_set(
    path: str = ".",
    provider: str = "openai",
    endpoint: str = "",
    api_key_env: str = "",
    default_model: str = "",
    provider_type: str = "chat-completions",
) -> dict:
    config = load_model_providers(path)
    providers = config.setdefault("providers", {})
    current = providers.get(provider, {})
    current.update(
        {
            "type": provider_type or current.get("type", "chat-completions"),
            "endpoint": endpoint or current.get("endpoint", ""),
            "api_key_env": api_key_env or current.get("api_key_env", ""),
            "default_model": default_model or current.get("default_model", ""),
        }
    )
    providers[provider] = current
    output = _root(path) / PROVIDERS_FILE
    _write_json(output, config)
    _append_model_log(path, "model_provider_set", {"provider": provider, "endpoint": current.get("endpoint", "")})
    return {"output": str(output), "provider": provider, "config": current}


def model_doctor(path: str = ".", provider: str = "openai") -> dict:
    config = load_model_providers(path)
    provider_config = config.get("providers", {}).get(provider, {})
    api_key_env = provider_config.get("api_key_env", "")
    has_key = bool(api_key_env and os.environ.get(api_key_env))
    endpoint = provider_config.get("endpoint", "")
    default_model = provider_config.get("default_model", "")
    ok = bool(provider_config) and bool(endpoint) and bool(api_key_env) and has_key
    report = {
        "ok": ok,
        "provider": provider,
        "configured": bool(provider_config),
        "endpoint": endpoint,
        "api_key_env": api_key_env,
        "api_key_present": has_key,
        "default_model": default_model,
        "ready_for_live_call": ok and bool(default_model),
    }
    _append_model_log(path, "model_doctor", {"provider": provider, "ok": ok, "ready_for_live_call": report["ready_for_live_call"]})
    return report


def _read_issue_context(path: str, issue: str) -> dict:
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


def build_model_messages(prompt: str = "", issue_context: dict | None = None, system: str = "") -> list[dict]:
    messages = []
    messages.append(
        {
            "role": "system",
            "content": system
            or "You are a governed coding/research subagent. Return concise, auditable output and do not claim to have changed files.",
        }
    )
    if issue_context:
        messages.append({"role": "user", "content": "Local issue context:\n" + json.dumps(issue_context, indent=2)})
    messages.append({"role": "user", "content": prompt.strip() or "Produce a short implementation plan."})
    return messages


def model_request_build(
    path: str = ".",
    provider: str = "openai",
    model: str = "",
    prompt: str = "",
    issue: str = "",
    subagent: str = "",
    system: str = "",
    output_dir: str = str(REQUESTS_DIR),
) -> dict:
    model_config_init(path)
    providers = load_model_providers(path)
    provider_config = providers.get("providers", {}).get(provider, {})
    selected_model = model or provider_config.get("default_model", "")
    issue_context = _read_issue_context(path, issue)
    payload = {
        "provider": provider,
        "provider_type": provider_config.get("type", "chat-completions"),
        "model": selected_model,
        "subagent": subagent,
        "issue": issue,
        "created_at": _now(),
        "request": {
            "model": selected_model,
            "messages": build_model_messages(prompt=prompt, issue_context=issue_context, system=system),
        },
    }
    request_root = _root(path) / output_dir
    request_id = _next_id(request_root, "model-request")
    output = request_root / f"{request_id}.json"
    _write_json(output, payload)
    _append_model_log(path, "model_request_build", {"provider": provider, "request": str(output), "subagent": subagent, "issue": issue})
    return {"id": request_id, "output": str(output), "payload": payload}


def _load_request(path: str, request: str) -> tuple[Path, dict]:
    request_root = _root(path) / REQUESTS_DIR
    for candidate in request_root.glob(f"{request}*.json"):
        return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    request_path = Path(request)
    if not request_path.is_absolute():
        request_path = _root(path) / request
    if request_path.exists():
        return request_path, json.loads(request_path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"model request/{request}")


def _token_matches(token: dict, subagent: str, action: str, target: str) -> bool:
    if not token_is_active(token):
        return False
    if subagent and token.get("subagent") != subagent:
        return False
    if token.get("action") not in {action, "model-api", "*"}:
        return False
    token_target = token.get("target", "")
    return token_target in {"", "*", target}


def model_capability_check(path: str = ".", subagent: str = "", action: str = "model-call", target: str = "openai") -> dict:
    governance_init(path)
    token_root = _root(path) / TOKENS_DIR
    matches = []
    for candidate in sorted(token_root.glob("*.json")):
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        if _token_matches(payload, subagent, action, target):
            matches.append({"token": payload.get("id", candidate.stem), "path": str(candidate)})
    ok = bool(matches)
    _append_model_log(path, "model_capability_check", {"subagent": subagent, "action": action, "target": target, "ok": ok})
    return {"ok": ok, "subagent": subagent, "action": action, "target": target, "matches": matches}


def _openai_chat_call(provider_config: dict, request_payload: dict) -> dict:
    api_key_env = provider_config.get("api_key_env", "")
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        return {"ok": False, "status": "missing-api-key", "message": f"{api_key_env} is not set."}
    endpoint = provider_config.get("endpoint", "")
    data = json.dumps(request_payload["request"]).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
            return {"ok": True, "status": "called", "status_code": response.status, "body": json.loads(body)}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return {"ok": False, "status": "http-error", "status_code": exc.code, "body": body}
    except urllib.error.URLError as exc:
        return {"ok": False, "status": "url-error", "message": str(exc.reason)}


def model_call(path: str = ".", request: str = "", apply: bool = False, require_token: bool = True) -> dict:
    model_config_init(path)
    _request_path, request_payload = _load_request(path, request)
    providers = load_model_providers(path)
    provider = request_payload.get("provider", "openai")
    provider_config = providers.get("providers", {}).get(provider, {})
    subagent = request_payload.get("subagent", "")
    capability = model_capability_check(path, subagent=subagent, action="model-call", target=provider) if require_token else {"ok": True}
    if not apply:
        report = {
            "ok": True,
            "status": "dry-run",
            "provider": provider,
            "subagent": subagent,
            "capability_ok": capability["ok"],
            "request": request,
        }
        _append_model_log(path, "model_call_dry_run", report)
        return report
    if not capability["ok"]:
        report = {"ok": False, "status": "missing-capability-token", "provider": provider, "subagent": subagent}
        _append_model_log(path, "model_call_blocked", report)
        return report
    if not request_payload.get("model"):
        return {"ok": False, "status": "missing-model", "message": "Set provider default_model or pass --model when building the request."}

    if provider_config.get("type") != "chat-completions":
        return {"ok": False, "status": "unsupported-provider-type", "provider_type": provider_config.get("type")}
    response = _openai_chat_call(provider_config, request_payload)
    response_root = _root(path) / RESPONSES_DIR
    response_id = _next_id(response_root, "model-response")
    output = response_root / f"{response_id}.json"
    _write_json(output, {"request": request, "created_at": _now(), "response": response})
    response["output"] = str(output)
    _append_model_log(path, "model_call", {"provider": provider, "request": request, "output": str(output), "ok": response["ok"]})
    return response
