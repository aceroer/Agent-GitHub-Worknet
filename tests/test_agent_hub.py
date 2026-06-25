import json
from pathlib import Path

from structure_rule_kit import (
    agent_hub_init,
    create_issue,
    init_structure,
    runner_adapters,
    runtime_status,
    stream_show,
    stream_start,
    subagent_create,
    subagent_events,
    subagent_ingest,
    subagent_run,
    subagent_spawn,
)
from structure_rule_kit.cli import main


def seed_hub_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Hub task", body="Test the Agent Runtime Hub.")
    subagent = subagent_create(str(tmp_path), name="QA Lead", permission="draft", issue="issue-0001")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=subagent["id"])
    return subagent, stream


def test_agent_hub_init_and_adapters(tmp_path):
    report = agent_hub_init(str(tmp_path))
    adapters = runner_adapters(str(tmp_path))

    assert Path(report["adapters"]).exists()
    assert adapters["version"] == "1.5.3"
    assert {"local", "codex", "pi", "mini-swe", "openhands", "sandbox-agent"}.issubset(adapters["adapters"])
    assert adapters["adapters"]["sandbox-agent"]["kind"] == "http-adapter"


def test_subagent_spawn_creates_spec_prompt_and_stream_event(tmp_path):
    subagent, stream = seed_hub_project(tmp_path)
    spawn = subagent_spawn(
        str(tmp_path),
        subagent=subagent["id"],
        runner="codex",
        role="QA Lead",
        issue="issue-0001",
        stream=stream["id"],
        task="Review test coverage.",
    )
    payload = json.loads(Path(spawn["output"]).read_text(encoding="utf-8"))
    prompt = Path(spawn["prompt"]).read_text(encoding="utf-8")
    shown = stream_show(str(tmp_path), stream=stream["id"])

    assert payload["runner"] == "codex"
    assert payload["role"] == "QA Lead"
    assert payload["governance"]["remote_publication_default"] == "blocked"
    assert "Review test coverage." in prompt
    assert "Do not push" in prompt
    assert shown["events"][-1]["type"] == "subagent_spawn"


def test_subagent_run_dry_run_apply_and_ingest(tmp_path):
    subagent, stream = seed_hub_project(tmp_path)
    spawn = subagent_spawn(
        str(tmp_path),
        subagent=subagent["id"],
        runner="local",
        role="QA Lead",
        issue="issue-0001",
        stream=stream["id"],
        task="Run a harmless check.",
        command="pwd",
    )

    dry = subagent_run(str(tmp_path), spawn=spawn["id"])
    run = subagent_run(str(tmp_path), spawn=spawn["id"], apply=True)
    ingest = subagent_ingest(
        str(tmp_path),
        spawn=spawn["id"],
        summary="Local runner produced a check artifact.",
        status="verdict",
        by=subagent["id"],
    )
    events = subagent_events(str(tmp_path), spawn=spawn["id"])
    status = runtime_status(str(tmp_path))

    assert dry["payload"]["status"] == "dry-run"
    assert run["payload"]["status"] == "completed"
    assert run["payload"]["returncode"] == 0
    assert ingest["role_report"]["payload"]["role"] == "QA Lead"
    assert events["count"] >= 3
    assert status["role_reports"] == 1


def test_agent_hub_cli(tmp_path):
    subagent, stream = seed_hub_project(tmp_path)

    assert main(["agent-hub-init", "--path", str(tmp_path)]) == 0
    assert main(["runner-adapters", "--path", str(tmp_path)]) == 0
    assert (
        main(
            [
                "subagent-spawn",
                "--path",
                str(tmp_path),
                "--subagent",
                subagent["id"],
                "--runner",
                "local",
                "--role",
                "QA Lead",
                "--issue",
                "issue-0001",
                "--stream",
                stream["id"],
                "--task",
                "Run CLI hub check.",
                "--cmd",
                "pwd",
            ]
        )
        == 0
    )
    assert main(["subagent-run", "spawn-0001", "--path", str(tmp_path)]) == 0
    assert main(["subagent-run", "spawn-0001", "--path", str(tmp_path), "--apply"]) == 0
    assert main(["subagent-ingest", "spawn-0001", "--path", str(tmp_path), "--summary", "CLI artifact ingested."]) == 0
    assert main(["subagent-events", "--path", str(tmp_path), "--spawn", "spawn-0001"]) == 0
