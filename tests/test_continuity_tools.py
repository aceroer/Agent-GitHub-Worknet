import json

from structure_rule_kit import (
    append_decision_log,
    append_verify_log,
    build_context_prune,
    create_agent_task,
    init_structure,
    scan_repo_map,
)


def test_create_agent_task(tmp_path):
    init_structure(str(tmp_path))
    report = create_agent_task(
        str(tmp_path),
        title="Add Parser",
        goal="Create a parser utility.",
        scope="Parser files only.",
        checks="python3 -m py_compile structure_rule_kit/*.py",
    )
    output = tmp_path / report["output"]
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Agent Task: Add Parser" in text
    assert "Create a parser utility." in text


def test_append_verify_log(tmp_path):
    init_structure(str(tmp_path))
    append_verify_log(str(tmp_path), command="python3 -m py_compile", result="pass")
    append_verify_log(str(tmp_path), command="pytest", result="blocked", notes="pytest missing")
    text = (tmp_path / "structure" / "verification_log.md").read_text(encoding="utf-8")
    assert "python3 -m py_compile" in text
    assert "pytest missing" in text


def test_append_verify_log_run(tmp_path):
    init_structure(str(tmp_path))
    report = append_verify_log(str(tmp_path), command="python3 -c 'print(123)'", run=True)
    text = (tmp_path / "structure" / "verification_log.md").read_text(encoding="utf-8")
    assert report["ran"] is True
    assert report["exit_code"] == 0
    assert report["result"] == "pass"
    assert "123" in text


def test_append_decision_log(tmp_path):
    init_structure(str(tmp_path))
    append_decision_log(
        str(tmp_path),
        decision="Use scriptable tools.",
        rationale="Templates are too restrictive.",
        impact="Users can compose their own workflow.",
    )
    text = (tmp_path / "structure" / "decision_log.md").read_text(encoding="utf-8")
    assert "Use scriptable tools." in text
    assert "Templates are too restrictive." in text


def test_build_context_prune(tmp_path):
    init_structure(str(tmp_path))
    report = build_context_prune(str(tmp_path), budget=1200)
    output = tmp_path / "STRUCTURE_CONTEXT_PRUNED.md"
    assert report["files"] > 0
    assert len(output.read_text(encoding="utf-8")) <= 1400


def test_build_context_prune_json(tmp_path):
    init_structure(str(tmp_path))
    report = build_context_prune(str(tmp_path), output="pruned.json", budget=1200, json_output=True)
    payload = json.loads((tmp_path / "pruned.json").read_text(encoding="utf-8"))
    assert report["files"] > 0
    assert payload["kind"] == "structure-rule-context-pruned"


def test_scan_repo_map(tmp_path):
    init_structure(str(tmp_path))
    (tmp_path / "structure_rule_kit").mkdir()
    (tmp_path / "structure_rule_kit" / "example.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_ok(): pass\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "STRUCTURE_CONTEXT_PACK.md").write_text("generated\n", encoding="utf-8")
    report = scan_repo_map(str(tmp_path))
    text = (tmp_path / "structure" / "repo_map.md").read_text(encoding="utf-8")
    assert report["files"] > 0
    assert report["counts"]["generated"] > 0
    assert "`structure_rule_kit/example.py`" in text
    assert "`tests/test_example.py`" in text
    assert "`pyproject.toml`" in text
