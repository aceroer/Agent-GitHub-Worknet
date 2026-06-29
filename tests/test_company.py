import json
from pathlib import Path

from structure_rule_kit import (
    agent_promote,
    company_init,
    company_status,
    create_issue,
    init_structure,
    office_action_report,
    office_action_start,
    office_method_list,
    office_method_register,
    office_method_show,
    stream_show,
    stream_start,
    subagent_create,
)
from structure_rule_kit.cli import main


def seed_company_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Agent Company", body="Build office method registry.")
    ceo = subagent_create(str(tmp_path), name="CEO", permission="draft", issue="issue-0001")
    agent_promote(str(tmp_path), subagent=ceo["id"], level="P12")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=ceo["id"])
    return ceo, stream


def test_company_init_default_methods(tmp_path):
    report = company_init(str(tmp_path))
    methods = office_method_list(str(tmp_path))
    cso = office_method_show(str(tmp_path), "cso-audit")

    assert Path(report["registry"]).exists()
    assert methods["count"] >= 8
    assert "ceo-review" in methods["methods"]
    assert "gstack" in office_method_show(str(tmp_path), "ceo-review")["sources"]
    assert cso["definition"]["office"] == "CSO"
    assert cso["definition"]["publication_authority"] == "block_or_recommend"


def test_office_method_register_start_report_and_stream_event(tmp_path):
    ceo, stream = seed_company_project(tmp_path)
    registered = office_method_register(
        str(tmp_path),
        name="docs-polish",
        office="CRO",
        title="Docs Polish",
        purpose="Review public docs before release.",
        source="local",
        expected_artifact="docs readiness report",
    )
    action = office_action_start(
        str(tmp_path),
        method=registered["method"],
        office="CRO",
        stream=stream["id"],
        issue="issue-0001",
        actor=ceo["id"],
        objective="Check README clarity.",
    )
    report = office_action_report(
        str(tmp_path),
        action=action["id"],
        summary="README entry is clear enough for first readers.",
        status="verdict",
        evidence="Manual docs review.",
        by=ceo["id"],
    )
    shown = stream_show(str(tmp_path), stream=stream["id"])
    status = company_status(str(tmp_path))
    action_payload = json.loads(Path(action["output"]).read_text(encoding="utf-8"))

    assert registered["method"] == "docs-polish"
    assert action_payload["status"] == "verdict"
    assert report["payload"]["office"] == "CRO"
    assert shown["events"][-2]["type"] == "office_action_start"
    assert shown["events"][-1]["type"] == "office_action_report"
    assert status["actions"] == 1
    assert status["reports"] == 1


def test_office_action_rejects_wrong_office(tmp_path):
    seed_company_project(tmp_path)
    try:
        office_action_start(str(tmp_path), method="cso-audit", office="CTO")
    except ValueError as exc:
        assert "belongs to CSO" in str(exc)
    else:
        raise AssertionError("Expected wrong office to be rejected.")


def test_company_cli(tmp_path):
    ceo, stream = seed_company_project(tmp_path)

    assert main(["company-init", "--path", str(tmp_path)]) == 0
    assert main(["office-method-list", "--path", str(tmp_path)]) == 0
    assert main(["office-method-list", "--path", str(tmp_path), "--office", "CSO", "--json"]) == 0
    assert main(["office-method-show", "qa-verify", "--path", str(tmp_path)]) == 0
    assert (
        main(
            [
                "office-method-register",
                "--path",
                str(tmp_path),
                "--name",
                "release-note",
                "--office",
                "Release",
                "--title",
                "Release Note",
                "--purpose",
                "Prepare release note.",
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "office-action-start",
                "--path",
                str(tmp_path),
                "--method",
                "release-note",
                "--stream",
                stream["id"],
                "--actor",
                ceo["id"],
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "office-action-report",
                "office-action-0001",
                "--path",
                str(tmp_path),
                "--summary",
                "Release note drafted.",
                "--status",
                "artifact",
            ]
        )
        == 0
    )
    assert main(["company-status", "--path", str(tmp_path)]) == 0

    status = company_status(str(tmp_path))
    assert status["actions"] == 1
    assert status["reports"] == 1
