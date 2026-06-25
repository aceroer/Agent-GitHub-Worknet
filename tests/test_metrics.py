import json
from pathlib import Path

from structure_rule_kit import (
    create_issue,
    init_structure,
    metric_record,
    metric_show,
    metrics_init,
    metrics_status,
    okr_review,
    okr_set,
    scorecard_build,
    stream_show,
    stream_start,
    subagent_create,
)
from structure_rule_kit.cli import main


def seed_metrics_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Agent metrics", body="Measure agent behavior quality.")
    subagent = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=subagent["id"])
    return subagent, stream


def test_metrics_init_and_definitions(tmp_path):
    report = metrics_init(str(tmp_path))
    definitions = metric_show(str(tmp_path))

    assert Path(report["definitions"]).exists()
    assert definitions["version"] == "1.4.2"
    assert set(definitions["metrics"]) == {
        "Reliability",
        "Delegation",
        "Coordination",
        "Correction",
        "Exploration",
    }
    assert "adopted" in definitions["metrics"]["Reliability"]["question"] or "accepted" in definitions["metrics"]["Reliability"]["question"]


def test_metric_record_scorecard_and_stream_event(tmp_path):
    subagent, stream = seed_metrics_project(tmp_path)
    metric_record(str(tmp_path), agent=subagent["id"], metric="Reliability", score=5, stream=stream["id"], evidence="Output accepted.")
    metric_record(str(tmp_path), agent=subagent["id"], metric="Correction", score=4, stream=stream["id"], evidence="Fixed review note.")
    scorecard = scorecard_build(str(tmp_path), agent=subagent["id"], stream=stream["id"])
    shown = stream_show(str(tmp_path), stream=stream["id"])

    payload = json.loads(Path(scorecard["output"]).read_text(encoding="utf-8"))
    assert payload["overall"] == 4.5
    assert payload["scores"]["Reliability"]["average"] == 5
    assert payload["scores"]["Correction"]["latest"] == 4
    assert shown["events"][-1]["type"] == "metric_record"


def test_okr_set_and_review(tmp_path):
    subagent, stream = seed_metrics_project(tmp_path)
    metric_record(str(tmp_path), agent=subagent["id"], metric="Exploration", score=4, stream=stream["id"])
    okr = okr_set(
        str(tmp_path),
        agent=subagent["id"],
        stream=stream["id"],
        objective="Improve useful route exploration.",
        metric="Exploration",
        target=3.5,
        owner="CRO",
    )
    review = okr_review(str(tmp_path), okr=okr["id"])

    assert review["review"]["achieved"] is True
    assert review["review"]["current"] == 4
    assert review["payload"]["status"] == "achieved"


def test_metric_record_rejects_bad_metric_or_score(tmp_path):
    subagent, _stream = seed_metrics_project(tmp_path)

    try:
        metric_record(str(tmp_path), agent=subagent["id"], metric="Speed", score=4)
    except ValueError as exc:
        assert "Unknown metric" in str(exc)
    else:
        raise AssertionError("Expected unknown metric to fail.")

    try:
        metric_record(str(tmp_path), agent=subagent["id"], metric="Reliability", score=9)
    except ValueError as exc:
        assert "between 0 and 5" in str(exc)
    else:
        raise AssertionError("Expected invalid score to fail.")


def test_metrics_cli(tmp_path):
    subagent, stream = seed_metrics_project(tmp_path)

    assert main(["metrics-init", "--path", str(tmp_path)]) == 0
    assert main(["metric-show", "--path", str(tmp_path), "--metric", "Reliability"]) == 0
    assert (
        main(
            [
                "metric-record",
                "--path",
                str(tmp_path),
                "--agent",
                subagent["id"],
                "--stream",
                stream["id"],
                "--metric",
                "Delegation",
                "--score",
                "5",
                "--evidence",
                "Split task well.",
            ]
        )
        == 0
    )
    assert main(["scorecard-build", "--path", str(tmp_path), "--agent", subagent["id"], "--stream", stream["id"]]) == 0
    assert (
        main(
            [
                "okr-set",
                "--path",
                str(tmp_path),
                "--agent",
                subagent["id"],
                "--stream",
                stream["id"],
                "--objective",
                "Improve delegation.",
                "--metric",
                "Delegation",
                "--target",
                "4.5",
            ]
        )
        == 0
    )
    assert main(["okr-review", "okr-0001", "--path", str(tmp_path)]) == 0
    assert main(["metrics-status", "--path", str(tmp_path)]) == 0

    status = metrics_status(str(tmp_path))
    assert status["metric_events"] == 1
    assert status["scorecards"] == 2
    assert status["okrs"] == 1
