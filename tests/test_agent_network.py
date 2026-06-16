from pathlib import Path

from structure_rule_kit import (
    build_project_board,
    create_issue,
    create_network_branch,
    create_pr,
    create_review,
    init_network,
    init_structure,
    list_issues,
    sync_network,
)
from tests.test_workflow_tools import fill_ready_fields


def test_init_network(tmp_path):
    init_structure(str(tmp_path))
    report = init_network(str(tmp_path))
    root = tmp_path / "structure" / "network"
    assert report["output"].endswith("structure/network")
    assert (root / "issues").exists()
    assert (root / "prs").exists()
    assert (root / "network_log.jsonl").exists()


def test_create_and_list_issue(tmp_path):
    init_structure(str(tmp_path))
    report = create_issue(str(tmp_path), title="Add parser", body="Create parser utility.", labels=["enhancement"])
    issues = list_issues(str(tmp_path))
    assert report["id"] == "issue-0001"
    assert len(issues) == 1
    assert issues[0]["title"] == "Add parser"
    assert issues[0]["labels"] == ["enhancement"]


def test_branch_pr_review_and_board(tmp_path):
    init_structure(str(tmp_path))
    issue = create_issue(str(tmp_path), title="Add parser")
    branch = create_network_branch(str(tmp_path), name="parser", purpose="Implement parser", issue=issue["id"])
    pr = create_pr(
        str(tmp_path),
        title="Implement parser",
        issue=issue["id"],
        branch=branch["id"],
        checks=["pytest"],
    )
    review = create_review(str(tmp_path), pr=pr["id"], reviewer="agent-reviewer", decision="approve")
    board = build_project_board(str(tmp_path))
    text = Path(board["output"]).read_text(encoding="utf-8")

    assert pr["id"] == "pr-0001"
    assert review["id"] == "review-0001"
    assert "issue-0001" in text
    assert "pr-0001" in text
    assert "review-0001" in text


def test_sync_network(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    create_issue(str(tmp_path), title="Sync agent network")
    report = sync_network(str(tmp_path), target="codex")
    assert report["ready"] is True
    assert Path(report["board"]).exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "skills" / "project-structure" / "SKILL.md").exists()
