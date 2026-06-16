from pathlib import Path

from structure_rule_kit import (
    add_comment,
    assign_issue,
    create_issue,
    create_milestone,
    create_pr,
    github_export,
    init_structure,
    label_issue,
    list_comments,
    list_issues,
    list_milestones,
    merge_pr,
    timeline,
    update_issue_status,
    update_pr_status,
)


def test_issue_lifecycle(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Lifecycle issue")
    assign_issue(str(tmp_path), "issue-0001", "codex")
    label_issue(str(tmp_path), "issue-0001", ["bug", "agent"])
    update_issue_status(str(tmp_path), "issue-0001", "closed")
    update_issue_status(str(tmp_path), "issue-0001", "open")
    issue = list_issues(str(tmp_path))[0]
    assert issue["assignee"] == "codex"
    assert issue["status"] == "open"
    assert issue["labels"] == ["bug", "agent"]


def test_pr_ready_merge_closes_issue(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Merge issue")
    create_pr(str(tmp_path), title="Merge PR", issue="issue-0001", branch="merge-branch")
    update_pr_status(str(tmp_path), "pr-0001", "ready")
    merge_pr(str(tmp_path), "pr-0001")
    issue = list_issues(str(tmp_path))[0]
    pr_path = next((tmp_path / "structure" / "network" / "prs").glob("*.json"))
    assert issue["status"] == "closed"
    assert '"status": "merged"' in pr_path.read_text(encoding="utf-8")


def test_comments_and_timeline(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Comment issue")
    add_comment(str(tmp_path), target="issue-0001", author="agent-a", body="First comment")
    comments = list_comments(str(tmp_path), target="issue-0001")
    events = timeline(str(tmp_path), target="issue-0001")
    assert comments[0]["body"] == "First comment"
    assert any(event["event"] == "comment" for event in events)


def test_milestone_and_github_export(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Export issue", body="Issue body")
    create_milestone(str(tmp_path), title="v0.7", due="2026-06-30")
    export = github_export(str(tmp_path), item_type="issue", item_id="issue-0001")
    milestones = list_milestones(str(tmp_path))
    output = Path(export["output"])
    assert milestones[0]["title"] == "v0.7"
    assert output.exists()
    assert "Export issue" in output.read_text(encoding="utf-8")
