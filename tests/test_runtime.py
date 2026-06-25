import json
from pathlib import Path

from structure_rule_kit import (
    agent_promote,
    assignment_create,
    ceo_plan,
    create_issue,
    executive_appoint,
    executive_board,
    executive_delegate,
    executive_report,
    human_takeover,
    init_structure,
    level_allows,
    role_report,
    role_show,
    runtime_init,
    runtime_status,
    stream_event,
    stream_show,
    stream_start,
    subagent_create,
)
from structure_rule_kit.cli import main


def seed_runtime_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Stream runtime", body="Build a stream-structured runtime.")
    subagent = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    return subagent


def test_runtime_init_and_roles(tmp_path):
    report = runtime_init(str(tmp_path))
    roles = role_show(str(tmp_path))
    p12 = role_show(str(tmp_path), level="P12")

    assert Path(report["roles"]).exists()
    assert roles["philosophy"].startswith("Stream-structured")
    assert roles["supervision"]["ceo_agent"] == "P12"
    assert p12["role"]["title"] == "CEO Agent"
    assert role_show(str(tmp_path), level="P13")["role"]["title"] == "Human Supervisor"


def test_level_capabilities_are_cumulative(tmp_path):
    runtime_init(str(tmp_path))

    assert level_allows(str(tmp_path), level="P1", capability="read_context")["ok"] is True
    assert level_allows(str(tmp_path), level="P1", capability="verify_commands")["ok"] is False
    assert level_allows(str(tmp_path), level="P6", capability="verify_commands")["ok"] is True
    assert level_allows(str(tmp_path), level="P12", capability="global_orchestration")["ok"] is True
    assert level_allows(str(tmp_path), level="P13", capability="human_takeover")["ok"] is True


def test_agent_promote_and_assignment(tmp_path):
    subagent = seed_runtime_project(tmp_path)
    promoted = agent_promote(str(tmp_path), subagent=subagent["id"], level="P6")
    assigned = assignment_create(
        str(tmp_path),
        subagent=subagent["id"],
        issue="issue-0001",
        duty="Verify the stream runtime.",
    )

    payload = json.loads(Path(promoted["output"]).read_text(encoding="utf-8"))
    sandbox = json.loads((tmp_path / "structure" / "worknet" / "governance" / "sandboxes" / f"{subagent['id']}.json").read_text(encoding="utf-8"))
    assignment = json.loads(Path(assigned["output"]).read_text(encoding="utf-8"))
    assert payload["corporate_level"] == "P6"
    assert payload["corporate_title"] == "Verification Worker"
    assert payload["permission"] == "apply"
    assert sandbox["permission"] == "apply"
    assert "verify" in sandbox["command_levels"]
    assert assignment["level"] == "P6"
    assert assignment["duty"] == "Verify the stream runtime."


def test_stream_start_event_show_and_human_takeover(tmp_path):
    subagent = seed_runtime_project(tmp_path)
    agent_promote(str(tmp_path), subagent=subagent["id"], level="P12")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=subagent["id"])
    stream_event(str(tmp_path), stream=stream["id"], event_type="observation", message="Loaded context.", actor=subagent["id"])
    takeover = human_takeover(str(tmp_path), stream=stream["id"], reason="Manual review.", actor="owner")
    shown = stream_show(str(tmp_path), stream=stream["id"])
    status = runtime_status(str(tmp_path))

    assert stream["id"] == "stream-0001"
    assert takeover["event"]["type"] == "human_takeover"
    assert shown["count"] == 3
    assert shown["events"][0]["type"] == "stream_started"
    assert status["current"]["state"] == "human_control"


def test_ceo_plan_creates_stream_and_plan(tmp_path):
    subagent = seed_runtime_project(tmp_path)
    agent_promote(str(tmp_path), subagent=subagent["id"], level="P12")
    plan = ceo_plan(str(tmp_path), issue="issue-0001", ceo_agent=subagent["id"])
    payload = json.loads(Path(plan["output"]).read_text(encoding="utf-8"))
    shown = stream_show(str(tmp_path), stream=plan["stream"])

    assert payload["supervision"]["human"] == "P13 final supervisor"
    assert payload["supervision"]["ceo"] == "P12 global coordinator"
    assert any(item["level"] == "P13" for item in payload["delegation"])
    assert shown["events"][-1]["type"] == "ceo_plan"


def test_executive_board_appointments_delegate_and_report(tmp_path):
    ceo = seed_runtime_project(tmp_path)
    cto = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    cfo = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    agent_promote(str(tmp_path), subagent=ceo["id"], level="P12")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=ceo["id"])

    board = executive_board(str(tmp_path))
    appointment = executive_appoint(str(tmp_path), office="CTO", subagent=cto["id"], by=ceo["id"])
    executive_appoint(str(tmp_path), office="CFO", subagent=cfo["id"], by=ceo["id"])
    delegated = executive_delegate(
        str(tmp_path),
        office="CTO",
        stream=stream["id"],
        duty="Own the technical route.",
        by=ceo["id"],
    )
    report = executive_report(
        str(tmp_path),
        office="CFO",
        stream=stream["id"],
        summary="Token usage is within budget.",
    )
    shown = stream_show(str(tmp_path), stream=stream["id"])
    status = runtime_status(str(tmp_path))

    assert {"COO", "CTO", "CFO", "CSO", "CRO"}.issubset(board["offices"])
    assert appointment["payload"]["title"] == "Chief Technology Officer Agent"
    assert appointment["payload"]["level"] == "P11"
    assert executive_board(str(tmp_path), office="CTO")["appointment"]["subagent"] == cto["id"]
    assert delegated["assignment"]["payload"]["subagent"] == cto["id"]
    assert report["payload"]["office"] == "CFO"
    assert shown["events"][-2]["type"] == "executive_delegate"
    assert shown["events"][-1]["type"] == "executive_report"
    assert status["executive_appointments"] == 2
    assert status["executive_reports"] == 1


def test_executive_appoint_requires_ceo_or_human(tmp_path):
    junior = seed_runtime_project(tmp_path)
    cto = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")

    try:
        executive_appoint(str(tmp_path), office="CTO", subagent=cto["id"], by=junior["id"])
    except PermissionError as exc:
        assert "P12 CEO" in str(exc)
    else:
        raise AssertionError("Expected junior executive appointment to be denied.")

    human = executive_appoint(str(tmp_path), office="CTO", subagent=cto["id"], by="human")
    assert human["payload"]["appointed_by"] == "human"


def test_role_report_accepts_non_executive_artifacts(tmp_path):
    subagent = seed_runtime_project(tmp_path)
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=subagent["id"])
    report = role_report(
        str(tmp_path),
        role="QA Lead",
        stream=stream["id"],
        summary="Relevant checks passed.",
        by=subagent["id"],
        status="verdict",
    )
    shown = stream_show(str(tmp_path), stream=stream["id"])
    status = runtime_status(str(tmp_path))

    payload = json.loads(Path(report["output"]).read_text(encoding="utf-8"))
    assert payload["role"] == "QA Lead"
    assert payload["status"] == "verdict"
    assert shown["events"][-1]["type"] == "role_report"
    assert status["role_reports"] == 1


def test_runtime_cli_commands(tmp_path):
    subagent = seed_runtime_project(tmp_path)

    assert main(["runtime-init", "--path", str(tmp_path)]) == 0
    assert main(["role-show", "--path", str(tmp_path), "--level", "P12"]) == 0
    assert main(["level-check", "--path", str(tmp_path), "--level", "P6", "--capability", "verify_commands"]) == 0
    assert main(["level-check", "--path", str(tmp_path), "--level", "P2", "--capability", "verify_commands"]) == 1
    assert main(["agent-promote", subagent["id"], "--path", str(tmp_path), "--level", "P9"]) == 0
    assert main(["stream-start", "--path", str(tmp_path), "--issue", "issue-0001", "--ceo-agent", subagent["id"]]) == 0
    assert main(["assignment-create", "--path", str(tmp_path), "--subagent", subagent["id"], "--stream", "stream-0001"]) == 0
    assert main(["stream-event", "stream-0001", "--path", str(tmp_path), "--type", "observation", "--message", "Observed."]) == 0
    assert main(["ceo-plan", "--path", str(tmp_path), "--issue", "issue-0001", "--stream", "stream-0001", "--ceo-agent", subagent["id"]]) == 0
    assert main(["human-takeover", "stream-0001", "--path", str(tmp_path), "--reason", "Review."]) == 0
    assert main(["executive-board", "--path", str(tmp_path)]) == 0
    assert main(["executive-appoint", "--path", str(tmp_path), "--office", "COO", "--subagent", subagent["id"], "--by", "human"]) == 0
    assert main(["executive-delegate", "--path", str(tmp_path), "--office", "COO", "--stream", "stream-0001", "--duty", "Own delivery."]) == 0
    assert main(["executive-report", "--path", str(tmp_path), "--office", "COO", "--stream", "stream-0001", "--summary", "Delivery stream stable."]) == 0
    assert main(["role-report", "--path", str(tmp_path), "--role", "QA Lead", "--stream", "stream-0001", "--summary", "Checks reviewed.", "--status", "verdict"]) == 0
    assert main(["stream-show", "stream-0001", "--path", str(tmp_path)]) == 0
    assert main(["runtime-status", "--path", str(tmp_path)]) == 0

    status = runtime_status(str(tmp_path))
    assert status["streams"] == 1
    assert status["assignments"] == 2
    assert status["ceo_plans"] == 1
    assert status["executive_appointments"] == 1
    assert status["executive_reports"] == 1
    assert status["role_reports"] == 1
