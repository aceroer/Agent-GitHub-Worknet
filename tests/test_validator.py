from structure_rule_kit import init_structure, validate_structure


def test_validate_generated_structure(tmp_path):
    init_structure(str(tmp_path))
    report = validate_structure(str(tmp_path))
    assert report["ok"] is True
    assert report["missing_files"] == []
    assert report["empty_files"] == []


def test_validate_missing_structure(tmp_path):
    report = validate_structure(str(tmp_path))
    assert report["ok"] is False
    assert report["missing_files"]
