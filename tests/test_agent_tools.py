import json

from structure_rule_kit import (
    build_context_pack,
    build_mcp_manifest,
    build_rag_index,
    init_structure,
    scaffold_skill,
)


def test_build_rag_index(tmp_path):
    init_structure(str(tmp_path))
    report = build_rag_index(str(tmp_path))
    output = tmp_path / "structure" / "rag_index.json"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert report["documents"] > 0
    assert payload["kind"] == "structure-rule-rag-index"
    assert payload["documents"][0]["sections"]


def test_build_context_pack(tmp_path):
    init_structure(str(tmp_path))
    report = build_context_pack(str(tmp_path))
    output = tmp_path / "STRUCTURE_CONTEXT_PACK.md"
    assert report["files"] > 0
    assert "Structure Context Pack" in output.read_text(encoding="utf-8")


def test_build_mcp_manifest(tmp_path):
    init_structure(str(tmp_path))
    report = build_mcp_manifest(str(tmp_path))
    output = tmp_path / "structure" / "mcp_manifest.json"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert report["resources"] > 0
    assert payload["kind"] == "structure-rule-mcp-manifest"
    assert payload["tools"]


def test_scaffold_skill(tmp_path):
    init_structure(str(tmp_path))
    report = scaffold_skill(str(tmp_path))
    output = tmp_path / "skills" / "project-structure" / "SKILL.md"
    assert report["output"].endswith("SKILL.md")
    assert "Required Reading" in output.read_text(encoding="utf-8")
