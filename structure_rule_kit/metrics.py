from __future__ import annotations

import json
from pathlib import Path

from .network import _now, _write_json
from .runtime import RUNTIME_DIR, runtime_init, stream_event


METRICS_DIR = RUNTIME_DIR / "metrics"
METRIC_DEFINITIONS_FILE = METRICS_DIR / "agent_metrics.json"
METRIC_EVENTS_DIR = METRICS_DIR / "events"
SCORECARDS_DIR = METRICS_DIR / "scorecards"
OKRS_DIR = METRICS_DIR / "okrs"
METRICS_LOG = METRICS_DIR / "metrics_log.jsonl"


AGENT_METRICS = {
    "version": "1.4.2",
    "philosophy": "Agent metrics measure behavior quality in a stream worknet, not generic corporate KPI output.",
    "scale": {
        "min": 0,
        "max": 5,
        "meaning": "0 means no evidence or harmful behavior; 5 means strong, repeated, stream-backed evidence.",
    },
    "metrics": {
        "Reliability": {
            "question": "How often are the agent's outputs accepted or adopted?",
            "positive_signal": "Outputs are merged, used, or accepted without major rewrite.",
            "negative_signal": "Outputs are rejected, reverted, or repeatedly unusable.",
        },
        "Delegation": {
            "question": "Can the agent decompose work and assign it to appropriate agents or offices?",
            "positive_signal": "Tasks are split into clear roles with suitable P-levels or executive offices.",
            "negative_signal": "The agent hoards work, fragments it badly, or assigns it to unsuitable agents.",
        },
        "Coordination": {
            "question": "Does collaboration with the agent improve the combined stream outcome?",
            "positive_signal": "The agent integrates evidence, resolves handoff friction, and improves team throughput.",
            "negative_signal": "The agent creates duplicated work, unclear ownership, or coordination loss.",
        },
        "Correction": {
            "question": "Can the agent respond to critique and fix errors quickly?",
            "positive_signal": "After feedback, the agent narrows the issue and corrects course with minimal churn.",
            "negative_signal": "The agent repeats the same mistake or resists useful correction.",
        },
        "Exploration": {
            "question": "Does the agent propose valuable new routes rather than mechanically repeating patterns?",
            "positive_signal": "The agent contributes useful options, hypotheses, or implementation routes.",
            "negative_signal": "The agent loops, copies templates, or offers low-value novelty.",
        },
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _append_metrics_log(path: str, event: str, payload: dict) -> None:
    root = _root(path) / METRICS_DIR
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (_root(path) / METRICS_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _next_metric_id(directory: Path, prefix: str) -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*.json"):
        tail = item.stem.removeprefix(f"{prefix}-")
        number = tail.split("-", 1)[0]
        if number.isdigit():
            existing.append(int(number))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def metrics_init(path: str = ".", force: bool = False) -> dict:
    runtime_init(path)
    root = _root(path)
    for directory in [root / METRICS_DIR, root / METRIC_EVENTS_DIR, root / SCORECARDS_DIR, root / OKRS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    definitions = root / METRIC_DEFINITIONS_FILE
    created = False
    if force or not definitions.exists():
        _write_json(definitions, AGENT_METRICS)
        created = True
    log_path = root / METRICS_LOG
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    _append_metrics_log(path, "metrics_init", {"definitions": str(definitions), "created": created})
    return {"output": str(root / METRICS_DIR), "definitions": str(definitions), "created": created}


def load_metric_definitions(path: str = ".") -> dict:
    definitions = _root(path) / METRIC_DEFINITIONS_FILE
    if not definitions.exists():
        metrics_init(path)
    return json.loads(definitions.read_text(encoding="utf-8"))


def metric_show(path: str = ".", metric: str = "") -> dict:
    definitions = load_metric_definitions(path)
    if metric:
        return {"version": definitions["version"], "metric": metric, "definition": definitions["metrics"][metric]}
    return definitions


def metric_record(
    path: str = ".",
    agent: str = "",
    metric: str = "",
    score: int = 0,
    stream: str = "",
    issue: str = "",
    evidence: str = "",
    evaluator: str = "",
) -> dict:
    metrics_init(path)
    definitions = load_metric_definitions(path)
    if metric not in definitions["metrics"]:
        raise ValueError(f"Unknown metric: {metric}")
    if score < 0 or score > 5:
        raise ValueError("Metric score must be between 0 and 5.")
    root = _root(path)
    event_root = root / METRIC_EVENTS_DIR
    event_id = _next_metric_id(event_root, "metric-event")
    payload = {
        "id": event_id,
        "agent": agent,
        "metric": metric,
        "score": score,
        "stream": stream,
        "issue": issue,
        "evidence": evidence or "Not specified.",
        "evaluator": evaluator or "human",
        "created_at": _now(),
    }
    output = event_root / f"{event_id}-{metric.lower()}.json"
    _write_json(output, payload)
    if stream:
        stream_event(
            path,
            stream=stream,
            event_type="metric_record",
            actor=payload["evaluator"],
            message=f"{metric}={score} for {agent}",
            payload={"metric_event": str(output), "metric": metric, "score": score, "agent": agent},
        )
    _append_metrics_log(path, "metric_record", {"agent": agent, "metric": metric, "score": score, "stream": stream, "output": str(output)})
    return {"id": event_id, "output": str(output), "payload": payload}


def _metric_events(path: str = ".", agent: str = "", stream: str = "") -> list[dict]:
    metrics_init(path)
    events = []
    for event_path in sorted((_root(path) / METRIC_EVENTS_DIR).glob("*.json")):
        payload = json.loads(event_path.read_text(encoding="utf-8"))
        if agent and payload.get("agent") != agent:
            continue
        if stream and payload.get("stream") != stream:
            continue
        payload["_path"] = str(event_path)
        events.append(payload)
    return events


def scorecard_build(path: str = ".", agent: str = "", stream: str = "") -> dict:
    metrics_init(path)
    definitions = load_metric_definitions(path)
    events = _metric_events(path, agent=agent, stream=stream)
    scores = {}
    for metric in definitions["metrics"]:
        values = [event["score"] for event in events if event["metric"] == metric]
        scores[metric] = {
            "count": len(values),
            "average": round(sum(values) / len(values), 3) if values else None,
            "latest": values[-1] if values else None,
        }
    populated = [item["average"] for item in scores.values() if item["average"] is not None]
    overall = round(sum(populated) / len(populated), 3) if populated else None
    payload = {
        "agent": agent,
        "stream": stream,
        "created_at": _now(),
        "overall": overall,
        "scores": scores,
        "events": len(events),
    }
    scorecard_root = _root(path) / SCORECARDS_DIR
    scorecard_id = _next_metric_id(scorecard_root, "scorecard")
    output = scorecard_root / f"{scorecard_id}.json"
    _write_json(output, payload)
    _append_metrics_log(path, "scorecard_build", {"agent": agent, "stream": stream, "overall": overall, "output": str(output)})
    return {"id": scorecard_id, "output": str(output), "payload": payload}


def okr_set(
    path: str = ".",
    agent: str = "",
    objective: str = "",
    metric: str = "",
    target: float = 0.0,
    stream: str = "",
    owner: str = "",
) -> dict:
    metrics_init(path)
    definitions = load_metric_definitions(path)
    if metric and metric not in definitions["metrics"]:
        raise ValueError(f"Unknown metric: {metric}")
    okr_root = _root(path) / OKRS_DIR
    okr_id = _next_metric_id(okr_root, "okr")
    payload = {
        "id": okr_id,
        "agent": agent,
        "stream": stream,
        "objective": objective or "Not specified.",
        "key_result": {
            "metric": metric,
            "target": target,
        },
        "owner": owner or "CEO/Executive board",
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = okr_root / f"{okr_id}.json"
    _write_json(output, payload)
    _append_metrics_log(path, "okr_set", {"okr": okr_id, "agent": agent, "metric": metric, "target": target, "output": str(output)})
    return {"id": okr_id, "output": str(output), "payload": payload}


def okr_review(path: str = ".", okr: str = "") -> dict:
    metrics_init(path)
    okr_root = _root(path) / OKRS_DIR
    okr_path = None
    for candidate in sorted(okr_root.glob(f"{okr}*.json")):
        okr_path = candidate
        break
    if okr_path is None:
        raise FileNotFoundError(f"okr/{okr}")
    payload = json.loads(okr_path.read_text(encoding="utf-8"))
    scorecard = scorecard_build(path, agent=payload.get("agent", ""), stream=payload.get("stream", ""))
    metric = payload.get("key_result", {}).get("metric", "")
    target = payload.get("key_result", {}).get("target", 0.0)
    current = scorecard["payload"]["scores"].get(metric, {}).get("average") if metric else None
    achieved = current is not None and current >= target
    review = {
        "okr": payload["id"],
        "agent": payload.get("agent", ""),
        "stream": payload.get("stream", ""),
        "metric": metric,
        "target": target,
        "current": current,
        "achieved": achieved,
        "reviewed_at": _now(),
        "scorecard": scorecard["output"],
    }
    payload["last_review"] = review
    payload["status"] = "achieved" if achieved else "active"
    payload["updated_at"] = _now()
    _write_json(okr_path, payload)
    _append_metrics_log(path, "okr_review", {"okr": payload["id"], "achieved": achieved, "current": current})
    return {"output": str(okr_path), "payload": payload, "review": review}


def metrics_status(path: str = ".") -> dict:
    metrics_init(path)
    root = _root(path)
    events = list((root / METRIC_EVENTS_DIR).glob("*.json"))
    scorecards = list((root / SCORECARDS_DIR).glob("*.json"))
    okrs = list((root / OKRS_DIR).glob("*.json"))
    log_path = root / METRICS_LOG
    log_events = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    return {
        "ready": (root / METRIC_DEFINITIONS_FILE).exists(),
        "definitions": str(root / METRIC_DEFINITIONS_FILE),
        "metric_events": len(events),
        "scorecards": len(scorecards),
        "okrs": len(okrs),
        "metrics_log_events": log_events,
    }
