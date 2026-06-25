from structure_rule_kit import init_structure


def test_init_structure_creates_files(tmp_path):
    report = init_structure(str(tmp_path))
    assert report["created"]
    assert (tmp_path / "STRUCTURE_RULE.md").exists()
    assert (tmp_path / "structure" / "project_plan.md").exists()
    assert (tmp_path / "structure" / "protocols.md").exists()
    assert (tmp_path / "structure" / "agent_notes.md").exists()


def test_init_structure_skips_existing_without_force(tmp_path):
    init_structure(str(tmp_path))
    report = init_structure(str(tmp_path))
    assert report["skipped"]
