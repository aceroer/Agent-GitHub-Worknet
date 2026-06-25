import json
from pathlib import Path

from structure_rule_kit import (
    approval_grant,
    approval_request,
    command_check,
    create_issue,
    gate_check,
    governance_init,
    governance_status,
    init_structure,
    policy_show,
    sandbox_check,
    secret_scan,
    subagent_create,
    subagent_plan,
    token_is_active,
    token_revoke,
)
from structure_rule_kit.cli import main


def seed_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(
        str(tmp_path),
        title="Governed model agent",
        body="Prepare a safe subagent workflow.",
        labels=["agent", "governance"],
    )


def test_governance_init_and_policy(tmp_path):
    init_structure(str(tmp_path))
    report = governance_init(str(tmp_path))
    policy = policy_show(str(tmp_path))

    assert Path(report["policy"]).exists()
    assert policy["version"] == "1.2"
    assert set(policy["permissions"]) == {"plan", "draft", "apply"}
    assert (tmp_path / "structure" / "worknet" / "governance" / "audit_log.jsonl").exists()


def test_subagent_create_and_sandbox(tmp_path):
    seed_project(tmp_path)
    plan_agent = subagent_create(str(tmp_path), permission="plan", issue="issue-0001")
    agent = subagent_create(str(tmp_path), permission="draft", issue="issue-0001", goal="Draft the task split.")
    allowed = sandbox_check(str(tmp_path), agent["id"], "structure/tasks/task.md")
    denied = sandbox_check(str(tmp_path), agent["id"], "src/model.py")
    plan_denied = sandbox_check(str(tmp_path), plan_agent["id"], "structure/tasks/task.md")

    sandbox = json.loads(Path(agent["sandbox"]).read_text(encoding="utf-8"))
    assert sandbox["permission"] == "draft"
    assert allowed["ok"] is True
    assert denied["ok"] is False
    assert plan_denied["ok"] is False


def test_sandbox_blocks_symlink_escape(tmp_path):
    seed_project(tmp_path)
    outside = tmp_path.parent / "outside-secret.txt"
    outside.write_text("outside", encoding="utf-8")
    link = tmp_path / "structure" / "tasks" / "escape.txt"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside)
    agent = subagent_create(str(tmp_path), permission="draft")
    report = sandbox_check(str(tmp_path), agent["id"], "structure/tasks/escape.txt")
    assert report["ok"] is False


def test_command_check_permission_levels(tmp_path):
    seed_project(tmp_path)
    plan_agent = subagent_create(str(tmp_path), permission="plan")
    draft_agent = subagent_create(str(tmp_path), permission="draft")
    apply_agent = subagent_create(str(tmp_path), permission="apply")

    assert command_check(str(tmp_path), "rg TODO", subagent=plan_agent["id"])["ok"] is False
    assert command_check(str(tmp_path), "rg TODO", subagent=draft_agent["id"])["ok"] is True
    assert command_check(str(tmp_path), "python3 -m pytest", subagent=apply_agent["id"])["ok"] is True
    assert command_check(str(tmp_path), "rm -rf build", subagent=apply_agent["id"])["ok"] is False
    assert command_check(str(tmp_path), "pytest; rm -rf build", subagent=apply_agent["id"])["ok"] is False


def test_approval_flow_creates_capability_token(tmp_path):
    seed_project(tmp_path)
    agent = subagent_create(str(tmp_path), permission="apply", issue="issue-0001")
    request = approval_request(
        str(tmp_path),
        subagent=agent["id"],
        action="apply-patch",
        target="structure_rule_kit/governance.py",
        reason="Need to implement the approved governance layer.",
    )
    grant = approval_grant(str(tmp_path), request["id"], granted_by="tester")

    token_path = Path(grant["token"])
    token = json.loads(token_path.read_text(encoding="utf-8"))
    assert grant["payload"]["status"] == "granted"
    assert token["status"] == "active"
    assert token["subagent"] == agent["id"]
    assert "expires_at" in token
    assert token_is_active(token) is True


def test_gate_check_requires_active_approval_token(tmp_path):
    seed_project(tmp_path)
    agent = subagent_create(str(tmp_path), permission="apply", issue="issue-0001")

    blocked = gate_check(str(tmp_path), action="gh-pr-create", subagent=agent["id"])
    assert blocked["ok"] is False
    assert blocked["status"] == "blocked"

    request = approval_request(
        str(tmp_path),
        subagent=agent["id"],
        action="gh-pr-create",
        target="",
        reason="Board approved draft PR publication.",
    )
    approval_grant(str(tmp_path), request["id"], granted_by="human")
    approved = gate_check(str(tmp_path), action="gh pr create", subagent=agent["id"])
    assert approved["ok"] is True
    assert approved["status"] == "approved"
    assert approved["matching_tokens"] == ["token-0001"]


def test_token_revoke_and_secret_scan(tmp_path):
    seed_project(tmp_path)
    agent = subagent_create(str(tmp_path), permission="apply", issue="issue-0001")
    request = approval_request(str(tmp_path), subagent=agent["id"], action="model-call", target="openai")
    grant = approval_grant(str(tmp_path), request["id"])
    token_path = Path(grant["token"])
    token = json.loads(token_path.read_text(encoding="utf-8"))
    revoked = token_revoke(str(tmp_path), token["id"], reason="test revoke")
    revoked_token = json.loads(Path(revoked["output"]).read_text(encoding="utf-8"))

    secret_file = tmp_path / "structure" / "tasks" / "draft.env"
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    secret_file.write_text("OPENAI_API_KEY=sk-testsecretvalue1234567890\n", encoding="utf-8")
    scan = secret_scan(str(tmp_path), "structure/tasks/draft.env")

    assert revoked_token["status"] == "revoked"
    assert token_is_active(revoked_token) is False
    assert scan["ok"] is False
    assert scan["findings"]


def test_subagent_plan_from_issue(tmp_path):
    seed_project(tmp_path)
    plan = subagent_plan(str(tmp_path), issue="issue-0001")
    payload = json.loads(Path(plan["output"]).read_text(encoding="utf-8"))

    assert payload["issue"] == "issue-0001"
    assert payload["subagents"][0]["permission"] == "plan"
    assert "sandbox-check" in payload["checks"][0]


def test_governance_cli_commands(tmp_path):
    seed_project(tmp_path)
    assert main(["governance-init", "--path", str(tmp_path)]) == 0
    assert main(["policy-show", "--path", str(tmp_path), "--json"]) == 0
    assert main(["subagent-plan", "issue-0001", "--path", str(tmp_path)]) == 0
    assert main(["subagent-create", "--path", str(tmp_path), "--permission", "draft", "--issue", "issue-0001"]) == 0
    assert main(["sandbox-check", "subagent-0001", "--path", str(tmp_path), "--target", "structure/tasks/task.md"]) == 0
    assert main(["sandbox-check", "subagent-0001", "--path", str(tmp_path), "--target", "src/model.py"]) == 1
    assert main(["command-check", "--path", str(tmp_path), "--subagent", "subagent-0001", "--cmd", "rg TODO"]) == 0
    assert main(["command-check", "--path", str(tmp_path), "--subagent", "subagent-0001", "--cmd", "pytest"]) == 1
    assert main(["gate-check", "--path", str(tmp_path), "--action", "gh-pr-create", "--subagent", "subagent-0001"]) == 1
    assert main(["approval-request", "subagent-0001", "--path", str(tmp_path), "--action", "apply-patch"]) == 0
    assert main(["approval-grant", "approval-0001", "--path", str(tmp_path)]) == 0
    assert main(["governance-status", "--path", str(tmp_path)]) == 0

    status = governance_status(str(tmp_path))
    assert status["subagents"] == 1
    assert status["approvals"] == 1
    assert status["tokens"] == 1
