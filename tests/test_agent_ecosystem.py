from pathlib import Path

from structure_rule_kit import (
    export_agent,
    export_all_agents,
    handle_jsonrpc,
    export_skill,
    init_structure,
    list_resources,
    read_resource,
    run_server,
    sync_agent,
)
from tests.test_workflow_tools import fill_ready_fields


def test_export_agent_targets(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    codex = export_agent(str(tmp_path), target="codex")
    claude = export_agent(str(tmp_path), target="claude", refresh=False)
    cursor = export_agent(str(tmp_path), target="cursor", refresh=False)

    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".cursor" / "rules" / "structure-rule.md").exists()
    assert codex["status"] == "ready"
    assert claude["outputs"]
    assert cursor["outputs"]


def test_export_all_agents(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = export_all_agents(str(tmp_path))
    assert "codex" in report["targets"]
    assert len(report["outputs"]) >= 4
    assert (tmp_path / "GENERIC_AGENT.md").exists()


def test_export_skill(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = export_skill(str(tmp_path), name="project-structure")
    output = tmp_path / "skills" / "project-structure" / "SKILL.md"
    assert report["status"] == "ready"
    assert output.exists()
    assert "STRUCTURE_AGENT_BRIEF.md" in output.read_text(encoding="utf-8")


def test_sync_agent(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = sync_agent(str(tmp_path), target="codex", budget=2400)
    assert report["ready"] is True
    assert (tmp_path / "AGENTS.md").exists()
    assert Path(report["skill"]).exists()
    assert Path(report["mcp_manifest"]).exists()


def test_mcp_server_resources(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    export_agent(str(tmp_path), target="codex")
    resources = list_resources(str(tmp_path))
    assert any(item["uri"] == "structure-rule://STRUCTURE_RULE.md" for item in resources)
    first_uri = resources[0]["uri"]
    read = read_resource(str(tmp_path), first_uri)
    assert read["text"]


def test_mcp_server_request(tmp_path):
    init_structure(str(tmp_path))
    result = run_server(str(tmp_path), '{"method":"resources/list"}')
    assert "resources" in result


def test_mcp_jsonrpc_initialize_and_read(tmp_path):
    init_structure(str(tmp_path))
    initialized = handle_jsonrpc(str(tmp_path), {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    listed = handle_jsonrpc(str(tmp_path), {"jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": {}})
    read = handle_jsonrpc(
        str(tmp_path),
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": "structure-rule://STRUCTURE_RULE.md"},
        },
    )

    assert initialized["result"]["serverInfo"]["name"] == "agent-github-worknet"
    assert listed["result"]["resources"]
    assert "Structure Rule" in read["result"]["contents"][0]["text"]


def test_mcp_jsonrpc_tool_call(tmp_path):
    init_structure(str(tmp_path))
    response = handle_jsonrpc(
        str(tmp_path),
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "structure_rule_summary", "arguments": {}},
        },
    )
    assert response["result"]["content"][0]["type"] == "text"
