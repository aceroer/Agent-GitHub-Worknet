from structure_rule_kit import export_structure, init_structure, summarize_structure


def test_summary_has_expected_keys(tmp_path):
    init_structure(str(tmp_path))
    summary = summarize_structure(str(tmp_path))
    assert "Project" in summary
    assert "Completion criteria" in summary


def test_export_structure(tmp_path):
    init_structure(str(tmp_path))
    report = export_structure(str(tmp_path))
    output = tmp_path / "STRUCTURE_CONTEXT.md"
    assert output.exists()
    assert "STRUCTURE_RULE.md" in output.read_text(encoding="utf-8")
    assert "project_plan.md" in output.read_text(encoding="utf-8")
    assert report["files"]
