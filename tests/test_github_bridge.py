import json
from pathlib import Path

from structure_rule_kit import (
    build_github_sync_plan,
    create_issue,
    create_milestone,
    create_pr,
    ensure_remote_metadata,
    export_github_issues,
    export_github_labels,
    export_github_milestones,
    github_sync,
    init_structure,
)
from structure_rule_kit.cli import main


def seed_network(tmp_path):
    init_structure(str(tmp_path))
    create_issue(
        str(tmp_path),
        title="Bridge issue",
        body="Prepare GitHub bridge.",
        labels=["agent", "github"],
        assignee="codex",
    )
    create_issue(str(tmp_path), title="Second issue", labels=["agent"])
    create_milestone(str(tmp_path), title="v0.8", due="2026-06-30", description="GitHub bridge dry-run.")
    create_pr(str(tmp_path), title="Bridge PR", issue="issue-0001", branch="bridge")


def test_ensure_remote_metadata(tmp_path):
    seed_network(tmp_path)
    report = ensure_remote_metadata(str(tmp_path))
    assert report["count"] >= 4

    issue_path = next((tmp_path / "structure" / "network" / "issues").glob("*.json"))
    payload = json.loads(issue_path.read_text(encoding="utf-8"))
    assert payload["remote"]["provider"] == "github"
    assert payload["remote"]["url"] is None


def test_github_bridge_exports(tmp_path):
    seed_network(tmp_path)
    labels = export_github_labels(str(tmp_path))
    issues = export_github_issues(str(tmp_path))
    milestones = export_github_milestones(str(tmp_path))

    label_payload = json.loads(Path(labels["output"]).read_text(encoding="utf-8"))
    milestone_payload = json.loads(Path(milestones["output"]).read_text(encoding="utf-8"))
    issue_text = (tmp_path / "structure" / "network" / "github_export" / "issues" / "issue-0001.md").read_text(
        encoding="utf-8"
    )

    assert labels["labels"] == 2
    assert issues["issues"] == 2
    assert milestones["milestones"] == 1
    assert {item["name"] for item in label_payload["labels"]} == {"agent", "github"}
    assert milestone_payload["milestones"][0]["title"] == "v0.8"
    assert "Bridge issue" in issue_text
    assert "Remote URL: Not synced" in issue_text


def test_github_sync_plan_and_sync(tmp_path):
    seed_network(tmp_path)
    plan = build_github_sync_plan(str(tmp_path))
    sync = github_sync(str(tmp_path))
    text = Path(plan["output"]).read_text(encoding="utf-8")

    assert plan["mode"] == "dry-run"
    assert sync["status"] == "dry-run"
    assert "No remote API calls" in text
    assert "Issues already linked: 0" in text


def test_github_bridge_cli(tmp_path):
    seed_network(tmp_path)
    assert main(["github-labels-export", "--path", str(tmp_path)]) == 0
    assert main(["github-issues-export", "--path", str(tmp_path)]) == 0
    assert main(["github-milestones-export", "--path", str(tmp_path)]) == 0
    assert main(["github-dry-run", "--path", str(tmp_path)]) == 0
    assert main(["github-sync", "--path", str(tmp_path), "--dry-run"]) == 0
    assert main(["github-sync", "--path", str(tmp_path), "--apply"]) == 1

    assert (tmp_path / "structure" / "network" / "github_export" / "sync_plan.md").exists()
