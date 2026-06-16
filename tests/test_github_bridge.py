import json
import subprocess
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
    github_issue_create,
    github_issues_create,
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


def mock_gh(labels=None, issue_url="https://github.com/aceroer/example/issues/17"):
    if labels is None:
        labels = ["agent", "github"]
    calls = []

    def runner(command, capture_output=True, text=True):
        calls.append(command)
        if command[:3] == ["gh", "label", "list"]:
            payload = [{"name": label} for label in labels]
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")
        if command[:3] == ["gh", "issue", "create"]:
            return subprocess.CompletedProcess(command, 0, stdout=f"{issue_url}\n", stderr="")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    runner.calls = calls
    return runner


def test_github_issue_create_dry_run(tmp_path):
    seed_network(tmp_path)
    runner = mock_gh()
    report = github_issue_create(str(tmp_path), issue="issue-0001", repo="aceroer/example", runner=runner)

    assert report["status"] == "dry-run"
    assert report["command"][:5] == ["gh", "issue", "create", "--repo", "aceroer/example"]
    assert not any(call[:3] == ["gh", "issue", "create"] for call in runner.calls)


def test_github_issue_create_missing_labels(tmp_path):
    seed_network(tmp_path)
    report = github_issue_create(str(tmp_path), issue="issue-0001", repo="aceroer/example", runner=mock_gh(labels=[]))

    assert report["ok"] is False
    assert report["status"] == "missing-labels"
    assert report["missing_labels"] == ["agent", "github"]


def test_github_issue_create_apply_updates_remote(tmp_path):
    seed_network(tmp_path)
    report = github_issue_create(
        str(tmp_path),
        issue="issue-0001",
        repo="aceroer/example",
        apply=True,
        runner=mock_gh(issue_url="https://github.com/aceroer/example/issues/42"),
    )
    issue_path = next((tmp_path / "structure" / "network" / "issues").glob("issue-0001*.json"))
    payload = json.loads(issue_path.read_text(encoding="utf-8"))

    assert report["status"] == "created"
    assert report["number"] == 42
    assert payload["remote"]["repo"] == "aceroer/example"
    assert payload["remote"]["number"] == 42
    assert payload["remote"]["url"] == "https://github.com/aceroer/example/issues/42"
    assert payload["remote"]["synced_at"]


def test_github_issues_create_batch_and_sync_apply(tmp_path):
    seed_network(tmp_path)
    runner = mock_gh(issue_url="https://github.com/aceroer/example/issues/50")
    report = github_issues_create(str(tmp_path), repo="aceroer/example", apply=True, runner=runner)
    sync = github_sync(str(tmp_path), dry_run=False, repo="aceroer/example", runner=runner)

    assert report["ok"] is True
    assert report["created"] == 2
    assert sync["ok"] is True
    assert sync["issue_create"]["skipped"] == 2
