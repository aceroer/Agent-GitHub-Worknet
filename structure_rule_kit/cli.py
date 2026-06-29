from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_brief import build_agent_brief
from .agent_export import export_agent, export_all_agents
from .agent_hub import (
    agent_hub_init,
    runner_adapters,
    subagent_events,
    subagent_ingest,
    subagent_run,
    subagent_spawn,
)
from .agent_ready import check_agent_ready
from .agent_sync import sync_agent
from .company import (
    company_init,
    company_status,
    office_action_report,
    office_action_start,
    office_method_list,
    office_method_register,
    office_method_show,
)
from .config import write_config
from .context_git import (
    checkout_context_branch,
    create_context_branch,
    create_context_snapshot,
    create_context_tag,
    export_context,
    init_context,
    latest_context_snapshot,
    list_context_snapshots,
    route_context,
)
from .context_pack import build_context_pack
from .context_prune import build_context_prune
from .decision_log import append_decision_log
from .exporter import export_structure
from .generator import init_structure
from .github_bridge import (
    build_github_sync_plan,
    export_github_issues,
    export_github_labels,
    export_github_milestones,
    github_comment,
    github_doctor,
    github_issue_create,
    github_issues_create,
    github_labels_create,
    github_milestones_create,
    github_pull,
    github_sync,
    github_sync_report,
    write_github_config,
)
from .governance import (
    approval_grant,
    approval_request,
    command_check,
    gate_check,
    governance_init,
    governance_status,
    policy_show,
    sandbox_check,
    secret_scan,
    subagent_create,
    subagent_plan,
    token_revoke,
)
from .handoff import build_handoff_pack
from .mcp_manifest import build_mcp_manifest
from .mcp_scaffold import scaffold_mcp
from .mcp_server import run_http_server, run_server, run_stdio_server
from .metrics import (
    metric_record,
    metric_show,
    metrics_init,
    metrics_status,
    okr_review,
    okr_set,
    scorecard_build,
)
from .model_api import (
    load_model_providers,
    model_call,
    model_capability_check,
    model_config_init,
    model_doctor,
    model_provider_set,
    model_request_build,
)
from .network import (
    add_comment,
    assign_issue,
    build_project_board,
    create_milestone,
    create_issue,
    create_network_branch,
    create_pr,
    create_review,
    github_export,
    init_network,
    label_issue,
    list_comments,
    list_issues,
    list_milestones,
    merge_pr,
    snapshot_network,
    sync_network,
    timeline,
    update_issue_status,
    update_pr_status,
)
from .rag_index import build_rag_index
from .repo_map import scan_repo_map
from .roundtable import (
    meeting_post,
    meeting_show,
    meeting_start,
    minutes_generate,
    org_apply,
    org_review,
    roundtable_init,
    roundtable_status,
    vote_cast,
    vote_open,
    vote_tally,
)
from .run_task import run_agent_task
from .runtime import (
    agent_promote,
    assignment_create,
    ceo_plan,
    executive_appoint,
    executive_board,
    executive_delegate,
    executive_report,
    human_takeover,
    level_allows,
    role_show,
    role_report,
    runtime_init,
    runtime_status,
    stream_event,
    stream_show,
    stream_start,
)
from .session import end_session, start_session
from .skill_scaffold import scaffold_skill
from .skill_export import export_skill
from .status_update import update_status
from .summary import summarize_structure
from .task import create_agent_task
from .toolbox_audit import audit_toolbox
from .validator import validate_structure
from .verify_log import append_verify_log
from .worknet import issue_from_task, task_from_issue, work_end, work_start, worknet_status


def print_summary(summary: dict) -> None:
    for key, value in summary.items():
        print(f"{key}:")
        print(value)
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="structure-rule")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create structure rule files")
    init_parser.add_argument("--path", default=".")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--minimal", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate structure rule files")
    validate_parser.add_argument("--path", default=".")
    validate_parser.add_argument("--allow-todo", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    summary_parser = subparsers.add_parser("summary", help="Print compact agent-facing summary")
    summary_parser.add_argument("--path", default=".")
    summary_parser.add_argument("--json", action="store_true")

    export_parser = subparsers.add_parser("export", help="Export structure context")
    export_parser.add_argument("--path", default=".")
    export_parser.add_argument("--output", default="STRUCTURE_CONTEXT.md")

    rag_parser = subparsers.add_parser("rag-index", help="Build a JSON RAG index from structure files")
    rag_parser.add_argument("--path", default=".")
    rag_parser.add_argument("--output", default="structure/rag_index.json")

    context_parser = subparsers.add_parser("context-pack", help="Build a bounded agent context pack")
    context_parser.add_argument("--path", default=".")
    context_parser.add_argument("--output", default="STRUCTURE_CONTEXT_PACK.md")
    context_parser.add_argument("--max-chars-per-file", type=int, default=2400)
    context_parser.add_argument("--json", action="store_true")

    mcp_parser = subparsers.add_parser("mcp-manifest", help="Build an MCP-facing structure manifest")
    mcp_parser.add_argument("--path", default=".")
    mcp_parser.add_argument("--output", default="structure/mcp_manifest.json")

    skill_parser = subparsers.add_parser("skill-scaffold", help="Create a local skill entry point")
    skill_parser.add_argument("--path", default=".")
    skill_parser.add_argument("--output", default="skills/project-structure")

    ready_parser = subparsers.add_parser("agent-ready", help="Check whether an agent can start safely")
    ready_parser.add_argument("--path", default=".")
    ready_parser.add_argument("--json", action="store_true")

    handoff_parser = subparsers.add_parser("handoff-pack", help="Build a task handoff packet")
    handoff_parser.add_argument("--path", default=".")
    handoff_parser.add_argument("--task", default="")
    handoff_parser.add_argument("--output", default="STRUCTURE_HANDOFF.md")

    status_parser = subparsers.add_parser("status-update", help="Update structure/status.md")
    status_parser.add_argument("--path", default=".")
    status_parser.add_argument("--current", default="")
    status_parser.add_argument("--done", default="")
    status_parser.add_argument("--next", default="", dest="next_step")
    status_parser.add_argument("--issue", default="")
    status_parser.add_argument("--decision", default="")

    toolbox_parser = subparsers.add_parser("toolbox-audit", help="Check structure/toolbox.md commands")
    toolbox_parser.add_argument("--path", default=".")
    toolbox_parser.add_argument("--json", action="store_true")

    task_parser = subparsers.add_parser("agent-task", help="Create a structured agent task file")
    task_parser.add_argument("--path", default=".")
    task_parser.add_argument("--title", default="")
    task_parser.add_argument("--goal", default="")
    task_parser.add_argument("--scope", default="")
    task_parser.add_argument("--forbidden", default="")
    task_parser.add_argument("--checks", default="")
    task_parser.add_argument("--output-dir", default="structure/tasks")

    verify_parser = subparsers.add_parser("verify-log", help="Append a verification log entry")
    verify_parser.add_argument("--path", default=".")
    verify_parser.add_argument("--cmd", default="")
    verify_parser.add_argument("--result", default="")
    verify_parser.add_argument("--notes", default="")
    verify_parser.add_argument("--output", default="structure/verification_log.md")
    verify_parser.add_argument("--run", action="store_true")
    verify_parser.add_argument("--timeout", type=int, default=120)

    decision_parser = subparsers.add_parser("decision-log", help="Append a decision log entry")
    decision_parser.add_argument("--path", default=".")
    decision_parser.add_argument("--decision", default="")
    decision_parser.add_argument("--rationale", default="")
    decision_parser.add_argument("--impact", default="")
    decision_parser.add_argument("--output", default="structure/decision_log.md")

    prune_parser = subparsers.add_parser("context-prune", help="Build a priority-pruned context pack")
    prune_parser.add_argument("--path", default=".")
    prune_parser.add_argument("--output", default="STRUCTURE_CONTEXT_PRUNED.md")
    prune_parser.add_argument("--budget", type=int, default=8000)
    prune_parser.add_argument("--json", action="store_true")

    repo_parser = subparsers.add_parser("repo-map", help="Scan repository files into structure/repo_map.md")
    repo_parser.add_argument("--path", default=".")
    repo_parser.add_argument("--output", default="structure/repo_map.md")
    repo_parser.add_argument("--max-files", type=int, default=240)

    config_parser = subparsers.add_parser("config", help="Write structure/config.json defaults")
    config_parser.add_argument("--path", default=".")
    config_parser.add_argument("--output", default="structure/config.json")
    config_parser.add_argument("--force", action="store_true")

    brief_parser = subparsers.add_parser("agent-brief", help="Build an agent startup brief")
    brief_parser.add_argument("--path", default=".")
    brief_parser.add_argument("--task", default="")
    brief_parser.add_argument("--output", default="")
    brief_parser.add_argument("--budget", type=int, default=None)
    brief_parser.add_argument("--no-refresh", action="store_true")

    run_parser = subparsers.add_parser("run-task", help="Run a structured agent task")
    run_parser.add_argument("task_file")
    run_parser.add_argument("--path", default=".")
    run_parser.add_argument("--cmd", default="")
    run_parser.add_argument("--timeout", type=int, default=120)
    run_parser.add_argument("--update-status", action="store_true")

    start_parser = subparsers.add_parser("session-start", help="Start an agent session")
    start_parser.add_argument("--path", default=".")
    start_parser.add_argument("--task", default="")
    start_parser.add_argument("--goal", default="")
    start_parser.add_argument("--budget", type=int, default=None)
    start_parser.add_argument("--output", default="")

    end_parser = subparsers.add_parser("session-end", help="End an agent session")
    end_parser.add_argument("--path", default=".")
    end_parser.add_argument("--done", default="")
    end_parser.add_argument("--next", default="", dest="next_step")
    end_parser.add_argument("--cmd", default="")
    end_parser.add_argument("--run", action="store_true")
    end_parser.add_argument("--handoff-output", default="")

    mcp_scaffold_parser = subparsers.add_parser("mcp-scaffold", help="Create a minimal MCP resource server scaffold")
    mcp_scaffold_parser.add_argument("--path", default=".")
    mcp_scaffold_parser.add_argument("--output", default="structure/mcp_server.py")
    mcp_scaffold_parser.add_argument("--force", action="store_true")

    agent_export_parser = subparsers.add_parser("agent-export", help="Export instructions for external agent ecosystems")
    agent_export_parser.add_argument("--path", default=".")
    agent_export_parser.add_argument("--target", default="generic", choices=["codex", "claude", "cursor", "generic", "all"])
    agent_export_parser.add_argument("--output", default="")
    agent_export_parser.add_argument("--no-refresh", action="store_true")

    skill_export_parser = subparsers.add_parser("skill-export", help="Export a richer local skill from project structure")
    skill_export_parser.add_argument("--path", default=".")
    skill_export_parser.add_argument("--name", default="project-structure")
    skill_export_parser.add_argument("--output-dir", default="skills")
    skill_export_parser.add_argument("--no-refresh", action="store_true")

    sync_parser = subparsers.add_parser("agent-sync", help="Run the full agent ecosystem sync")
    sync_parser.add_argument("--path", default=".")
    sync_parser.add_argument("--target", default="codex", choices=["codex", "claude", "cursor", "generic"])
    sync_parser.add_argument("--skill-name", default="project-structure")
    sync_parser.add_argument("--budget", type=int, default=None)

    mcp_server_parser = subparsers.add_parser("mcp-server", help="Run the Agent GitHub Worknet MCP server")
    mcp_server_parser.add_argument("--path", default=".")
    mcp_server_parser.add_argument("--request", default="")
    mcp_server_parser.add_argument("--stdio", action="store_true")
    mcp_server_parser.add_argument("--http", action="store_true")
    mcp_server_parser.add_argument("--host", default="127.0.0.1")
    mcp_server_parser.add_argument("--port", type=int, default=8765)

    network_parser = subparsers.add_parser("network-init", help="Initialize local agent network folders")
    network_parser.add_argument("--path", default=".")

    issue_create_parser = subparsers.add_parser("issue-create", help="Create a local agent issue")
    issue_create_parser.add_argument("--path", default=".")
    issue_create_parser.add_argument("--title", default="")
    issue_create_parser.add_argument("--body", default="")
    issue_create_parser.add_argument("--label", action="append", default=[])
    issue_create_parser.add_argument("--assignee", default="")
    issue_create_parser.add_argument("--snapshot", default="")

    issue_list_parser = subparsers.add_parser("issue-list", help="List local agent issues")
    issue_list_parser.add_argument("--path", default=".")
    issue_list_parser.add_argument("--status", default="")
    issue_list_parser.add_argument("--json", action="store_true")

    branch_create_parser = subparsers.add_parser("branch-create", help="Create a local agent branch record")
    branch_create_parser.add_argument("--path", default=".")
    branch_create_parser.add_argument("--name", default="")
    branch_create_parser.add_argument("--purpose", default="")
    branch_create_parser.add_argument("--issue", default="")
    branch_create_parser.add_argument("--context-branch", default="")

    pr_create_parser = subparsers.add_parser("pr-create", help="Create a local agent PR record")
    pr_create_parser.add_argument("--path", default=".")
    pr_create_parser.add_argument("--title", default="")
    pr_create_parser.add_argument("--body", default="")
    pr_create_parser.add_argument("--issue", default="")
    pr_create_parser.add_argument("--branch", default="")
    pr_create_parser.add_argument("--check", action="append", default=[])
    pr_create_parser.add_argument("--snapshot", default="")

    review_create_parser = subparsers.add_parser("review-create", help="Create a local agent review record")
    review_create_parser.add_argument("--path", default=".")
    review_create_parser.add_argument("--pr", default="")
    review_create_parser.add_argument("--reviewer", default="")
    review_create_parser.add_argument("--decision", default="comment", choices=["approve", "request-changes", "comment"])
    review_create_parser.add_argument("--body", default="")

    board_parser = subparsers.add_parser("project-board", help="Build local agent network board")
    board_parser.add_argument("--path", default=".")
    board_parser.add_argument("--output", default="structure/network/projects/board.md")

    network_sync_parser = subparsers.add_parser("network-sync", help="Sync local agent network with agent ecosystem outputs")
    network_sync_parser.add_argument("--path", default=".")
    network_sync_parser.add_argument("--target", default="codex", choices=["codex", "claude", "cursor", "generic"])

    context_init_parser = subparsers.add_parser("context-init", help="Initialize local Context Git state")
    context_init_parser.add_argument("--path", default=".")
    context_init_parser.add_argument("--project-name", default="")
    context_init_parser.add_argument("--force", action="store_true")

    context_snapshot_parser = subparsers.add_parser("context-snapshot", help="Create a context snapshot")
    context_snapshot_parser.add_argument("--path", default=".")
    context_snapshot_parser.add_argument("--message", default="")
    context_snapshot_parser.add_argument("--from-file", default="")
    context_snapshot_parser.add_argument("--branch", default="")

    context_log_parser = subparsers.add_parser("context-log", help="List context snapshots")
    context_log_parser.add_argument("--path", default=".")
    context_log_parser.add_argument("--json", action="store_true")

    context_latest_parser = subparsers.add_parser("context-latest", help="Print latest context snapshot")
    context_latest_parser.add_argument("--path", default=".")

    context_branch_parser = subparsers.add_parser("context-branch", help="Create a context branch")
    context_branch_parser.add_argument("name")
    context_branch_parser.add_argument("--path", default=".")
    context_branch_parser.add_argument("--purpose", default="")

    context_checkout_parser = subparsers.add_parser("context-checkout", help="Switch context branch")
    context_checkout_parser.add_argument("name")
    context_checkout_parser.add_argument("--path", default=".")

    context_tag_parser = subparsers.add_parser("context-tag", help="Create a context tag")
    context_tag_parser.add_argument("name")
    context_tag_parser.add_argument("--path", default=".")
    context_tag_parser.add_argument("--snapshot", default="")
    context_tag_parser.add_argument("--meaning", default="")

    context_export_parser = subparsers.add_parser("context-export", help="Export context recovery packet")
    context_export_parser.add_argument("--path", default=".")
    context_export_parser.add_argument("--output", default=".contextgit/exports/CONTEXT_EXPORT.md")
    context_export_parser.add_argument("--include-roots", action="store_true")

    context_route_parser = subparsers.add_parser("context-route", help="Create context routing template")
    context_route_parser.add_argument("--path", default=".")
    context_route_parser.add_argument("--output", default=".contextgit/exports/routing.json")

    network_snapshot_parser = subparsers.add_parser("network-snapshot", help="Snapshot local agent network into Context Git")
    network_snapshot_parser.add_argument("--path", default=".")
    network_snapshot_parser.add_argument("--message", default="Agent network snapshot")
    network_snapshot_parser.add_argument("--target", default="codex", choices=["codex", "claude", "cursor", "generic"])

    issue_close_parser = subparsers.add_parser("issue-close", help="Close a local agent issue")
    issue_close_parser.add_argument("issue")
    issue_close_parser.add_argument("--path", default=".")

    issue_reopen_parser = subparsers.add_parser("issue-reopen", help="Reopen a local agent issue")
    issue_reopen_parser.add_argument("issue")
    issue_reopen_parser.add_argument("--path", default=".")

    issue_assign_parser = subparsers.add_parser("issue-assign", help="Assign a local agent issue")
    issue_assign_parser.add_argument("issue")
    issue_assign_parser.add_argument("--assignee", default="")
    issue_assign_parser.add_argument("--path", default=".")

    issue_label_parser = subparsers.add_parser("issue-label", help="Add labels to a local agent issue")
    issue_label_parser.add_argument("issue")
    issue_label_parser.add_argument("--label", action="append", default=[])
    issue_label_parser.add_argument("--path", default=".")

    pr_ready_parser = subparsers.add_parser("pr-ready", help="Mark a local agent PR ready for review")
    pr_ready_parser.add_argument("pr")
    pr_ready_parser.add_argument("--path", default=".")

    pr_close_parser = subparsers.add_parser("pr-close", help="Close a local agent PR")
    pr_close_parser.add_argument("pr")
    pr_close_parser.add_argument("--path", default=".")

    pr_merge_parser = subparsers.add_parser("pr-merge", help="Semantically merge a local agent PR")
    pr_merge_parser.add_argument("pr")
    pr_merge_parser.add_argument("--path", default=".")
    pr_merge_parser.add_argument("--method", default="semantic")

    comment_add_parser = subparsers.add_parser("comment-add", help="Add a comment to an issue or PR")
    comment_add_parser.add_argument("--target", required=True)
    comment_add_parser.add_argument("--author", default="agent")
    comment_add_parser.add_argument("--body", default="")
    comment_add_parser.add_argument("--path", default=".")

    comment_list_parser = subparsers.add_parser("comment-list", help="List comments for an issue or PR")
    comment_list_parser.add_argument("--target", default="")
    comment_list_parser.add_argument("--path", default=".")
    comment_list_parser.add_argument("--json", action="store_true")

    timeline_parser = subparsers.add_parser("timeline", help="Show local network timeline")
    timeline_parser.add_argument("--target", default="")
    timeline_parser.add_argument("--path", default=".")
    timeline_parser.add_argument("--json", action="store_true")

    milestone_create_parser = subparsers.add_parser("milestone-create", help="Create a local milestone")
    milestone_create_parser.add_argument("--title", default="")
    milestone_create_parser.add_argument("--due", default="")
    milestone_create_parser.add_argument("--description", default="")
    milestone_create_parser.add_argument("--path", default=".")

    milestone_list_parser = subparsers.add_parser("milestone-list", help="List local milestones")
    milestone_list_parser.add_argument("--path", default=".")
    milestone_list_parser.add_argument("--json", action="store_true")

    github_export_parser = subparsers.add_parser("github-export", help="Export issue or PR as GitHub-ready markdown")
    github_export_parser.add_argument("--type", choices=["issue", "pr"], default="issue")
    github_export_parser.add_argument("--id", required=True)
    github_export_parser.add_argument("--path", default=".")

    github_dry_run_parser = subparsers.add_parser("github-dry-run", help="Build a dry-run GitHub sync plan")
    github_dry_run_parser.add_argument("--path", default=".")
    github_dry_run_parser.add_argument("--output", default="structure/network/github_export/sync_plan.md")

    github_labels_parser = subparsers.add_parser("github-labels-export", help="Export local labels as GitHub JSON")
    github_labels_parser.add_argument("--path", default=".")
    github_labels_parser.add_argument("--output", default="structure/network/github_export/labels.json")

    github_issues_parser = subparsers.add_parser("github-issues-export", help="Export all local issues as markdown")
    github_issues_parser.add_argument("--path", default=".")
    github_issues_parser.add_argument("--output-dir", default="structure/network/github_export/issues")

    github_milestones_parser = subparsers.add_parser("github-milestones-export", help="Export local milestones as JSON")
    github_milestones_parser.add_argument("--path", default=".")
    github_milestones_parser.add_argument("--output", default="structure/network/github_export/milestones.json")

    github_sync_parser = subparsers.add_parser("github-sync", help="Run GitHub bridge sync preparation")
    github_sync_parser.add_argument("--path", default=".")
    github_sync_parser.add_argument("--dry-run", action="store_true", default=True)
    github_sync_parser.add_argument("--apply", action="store_true", help="Reserved for a future real API sync")
    github_sync_parser.add_argument("--repo", default="")
    github_sync_parser.add_argument("--skip-missing-labels", action="store_true")

    github_issue_create_parser = subparsers.add_parser("github-issue-create", help="Create one local issue on GitHub")
    github_issue_create_parser.add_argument("issue")
    github_issue_create_parser.add_argument("--path", default=".")
    github_issue_create_parser.add_argument("--repo", default="")
    github_issue_create_parser.add_argument("--apply", action="store_true")
    github_issue_create_parser.add_argument("--skip-missing-labels", action="store_true")

    github_issues_create_parser = subparsers.add_parser("github-issues-create", help="Create local issues on GitHub")
    github_issues_create_parser.add_argument("--path", default=".")
    github_issues_create_parser.add_argument("--repo", default="")
    github_issues_create_parser.add_argument("--apply", action="store_true")
    github_issues_create_parser.add_argument("--skip-missing-labels", action="store_true")

    github_config_parser = subparsers.add_parser("github-config", help="Write Agent GitHub Worknet config")
    github_config_parser.add_argument("--path", default=".")
    github_config_parser.add_argument("--repo", default="")
    github_config_parser.add_argument("--output", default="structure/network/github_config.json")
    github_config_parser.add_argument("--force", action="store_true")
    github_config_parser.add_argument("--auto", action="store_true")

    github_doctor_parser = subparsers.add_parser("github-doctor", help="Check GitHub CLI and repo access")
    github_doctor_parser.add_argument("--path", default=".")
    github_doctor_parser.add_argument("--repo", default="")
    github_doctor_parser.add_argument("--json", action="store_true")

    github_labels_create_parser = subparsers.add_parser("github-labels-create", help="Create missing GitHub labels")
    github_labels_create_parser.add_argument("--path", default=".")
    github_labels_create_parser.add_argument("--repo", default="")
    github_labels_create_parser.add_argument("--apply", action="store_true")

    github_milestones_create_parser = subparsers.add_parser("github-milestones-create", help="Create missing GitHub milestones")
    github_milestones_create_parser.add_argument("--path", default=".")
    github_milestones_create_parser.add_argument("--repo", default="")
    github_milestones_create_parser.add_argument("--apply", action="store_true")

    github_pull_parser = subparsers.add_parser("github-pull", help="Pull linked GitHub issue state into local records")
    github_pull_parser.add_argument("--path", default=".")
    github_pull_parser.add_argument("--repo", default="")

    github_sync_report_parser = subparsers.add_parser("github-sync-report", help="Write Agent GitHub Worknet sync report")
    github_sync_report_parser.add_argument("--path", default=".")
    github_sync_report_parser.add_argument("--repo", default="")
    github_sync_report_parser.add_argument("--output", default="structure/network/github_export/sync_report.md")

    github_comment_parser = subparsers.add_parser("github-comment", help="Comment on a linked GitHub issue")
    github_comment_parser.add_argument("issue")
    github_comment_parser.add_argument("--path", default=".")
    github_comment_parser.add_argument("--repo", default="")
    github_comment_parser.add_argument("--body", default="")
    github_comment_parser.add_argument("--apply", action="store_true")

    task_from_issue_parser = subparsers.add_parser("task-from-issue", help="Create an agent task from a local issue")
    task_from_issue_parser.add_argument("issue")
    task_from_issue_parser.add_argument("--path", default=".")
    task_from_issue_parser.add_argument("--output-dir", default="structure/tasks")

    issue_from_task_parser = subparsers.add_parser("issue-from-task", help="Create a local issue from an agent task")
    issue_from_task_parser.add_argument("task_file")
    issue_from_task_parser.add_argument("--path", default=".")
    issue_from_task_parser.add_argument("--label", action="append", default=[])

    work_start_parser = subparsers.add_parser("work-start", help="Start an agent work session for an issue")
    work_start_parser.add_argument("issue")
    work_start_parser.add_argument("--path", default=".")
    work_start_parser.add_argument("--task", default="")
    work_start_parser.add_argument("--note", default="")

    work_end_parser = subparsers.add_parser("work-end", help="End the current agent work session")
    work_end_parser.add_argument("--path", default=".")
    work_end_parser.add_argument("--issue", default="")
    work_end_parser.add_argument("--done", default="")
    work_end_parser.add_argument("--next", default="", dest="next_step")
    work_end_parser.add_argument("--cmd", default="")
    work_end_parser.add_argument("--run", action="store_true")
    work_end_parser.add_argument("--github-comment", default="")
    work_end_parser.add_argument("--apply-comment", action="store_true")

    worknet_status_parser = subparsers.add_parser("worknet-status", help="Show Agent GitHub Worknet status")
    worknet_status_parser.add_argument("--path", default=".")
    worknet_status_parser.add_argument("--json", action="store_true")

    governance_init_parser = subparsers.add_parser("governance-init", help="Initialize model-agent governance files")
    governance_init_parser.add_argument("--path", default=".")
    governance_init_parser.add_argument("--force", action="store_true")

    policy_show_parser = subparsers.add_parser("policy-show", help="Show model-agent governance policy")
    policy_show_parser.add_argument("--path", default=".")
    policy_show_parser.add_argument("--json", action="store_true")

    subagent_plan_parser = subparsers.add_parser("subagent-plan", help="Plan subagent roles for a local issue")
    subagent_plan_parser.add_argument("issue")
    subagent_plan_parser.add_argument("--path", default=".")
    subagent_plan_parser.add_argument("--output-dir", default="structure/worknet/plans")

    subagent_create_parser = subparsers.add_parser("subagent-create", help="Create a governed subagent record")
    subagent_create_parser.add_argument("--path", default=".")
    subagent_create_parser.add_argument("--name", default="")
    subagent_create_parser.add_argument("--permission", default="plan", choices=["plan", "draft", "apply"])
    subagent_create_parser.add_argument("--goal", default="")
    subagent_create_parser.add_argument("--issue", default="")
    subagent_create_parser.add_argument("--allowed-path", action="append", default=[])

    approval_request_parser = subparsers.add_parser("approval-request", help="Request approval for a subagent action")
    approval_request_parser.add_argument("subagent")
    approval_request_parser.add_argument("--path", default=".")
    approval_request_parser.add_argument("--action", default="")
    approval_request_parser.add_argument("--target", default="")
    approval_request_parser.add_argument("--reason", default="")

    approval_grant_parser = subparsers.add_parser("approval-grant", help="Grant an approval and issue a capability token")
    approval_grant_parser.add_argument("approval")
    approval_grant_parser.add_argument("--path", default=".")
    approval_grant_parser.add_argument("--granted-by", default="human")
    approval_grant_parser.add_argument("--ttl-hours", type=int, default=24)

    token_revoke_parser = subparsers.add_parser("token-revoke", help="Revoke a capability token")
    token_revoke_parser.add_argument("token")
    token_revoke_parser.add_argument("--path", default=".")
    token_revoke_parser.add_argument("--revoked-by", default="human")
    token_revoke_parser.add_argument("--reason", default="")

    sandbox_check_parser = subparsers.add_parser("sandbox-check", help="Check whether a subagent may write a path")
    sandbox_check_parser.add_argument("subagent")
    sandbox_check_parser.add_argument("--path", default=".")
    sandbox_check_parser.add_argument("--target", required=True)
    sandbox_check_parser.add_argument("--json", action="store_true")

    command_check_parser = subparsers.add_parser("command-check", help="Check whether a subagent may run a command")
    command_check_parser.add_argument("--path", default=".")
    command_check_parser.add_argument("--subagent", default="")
    command_check_parser.add_argument("--permission", default="")
    command_check_parser.add_argument("--cmd", required=True)
    command_check_parser.add_argument("--json", action="store_true")

    gate_check_parser = subparsers.add_parser("gate-check", help="Check approval for commit, push, PR, or other gated actions")
    gate_check_parser.add_argument("--path", default=".")
    gate_check_parser.add_argument("--action", required=True)
    gate_check_parser.add_argument("--subagent", default="")
    gate_check_parser.add_argument("--target", default="")
    gate_check_parser.add_argument("--json", action="store_true")

    secret_scan_parser = subparsers.add_parser("secret-scan", help="Scan one file for common secret patterns")
    secret_scan_parser.add_argument("--path", default=".")
    secret_scan_parser.add_argument("--target", required=True)
    secret_scan_parser.add_argument("--json", action="store_true")

    governance_status_parser = subparsers.add_parser("governance-status", help="Show model-agent governance status")
    governance_status_parser.add_argument("--path", default=".")
    governance_status_parser.add_argument("--json", action="store_true")

    model_config_parser = subparsers.add_parser("model-config", help="Initialize or show model API provider config")
    model_config_parser.add_argument("--path", default=".")
    model_config_parser.add_argument("--force", action="store_true")
    model_config_parser.add_argument("--json", action="store_true")

    model_provider_parser = subparsers.add_parser("model-provider-set", help="Set a model API provider")
    model_provider_parser.add_argument("--path", default=".")
    model_provider_parser.add_argument("--provider", default="openai")
    model_provider_parser.add_argument("--endpoint", default="")
    model_provider_parser.add_argument("--api-key-env", default="")
    model_provider_parser.add_argument("--model", default="")
    model_provider_parser.add_argument("--type", default="chat-completions", dest="provider_type")

    model_doctor_parser = subparsers.add_parser("model-doctor", help="Check model API provider readiness")
    model_doctor_parser.add_argument("--path", default=".")
    model_doctor_parser.add_argument("--provider", default="openai")
    model_doctor_parser.add_argument("--json", action="store_true")

    model_request_parser = subparsers.add_parser("model-request", help="Build a governed model API request packet")
    model_request_parser.add_argument("--path", default=".")
    model_request_parser.add_argument("--provider", default="openai")
    model_request_parser.add_argument("--model", default="")
    model_request_parser.add_argument("--prompt", default="")
    model_request_parser.add_argument("--issue", default="")
    model_request_parser.add_argument("--subagent", default="")
    model_request_parser.add_argument("--system", default="")
    model_request_parser.add_argument("--output-dir", default="structure/worknet/model_api/requests")

    model_capability_parser = subparsers.add_parser("model-capability-check", help="Check model API capability token")
    model_capability_parser.add_argument("--path", default=".")
    model_capability_parser.add_argument("--subagent", default="")
    model_capability_parser.add_argument("--provider", default="openai")
    model_capability_parser.add_argument("--action", default="model-call")
    model_capability_parser.add_argument("--json", action="store_true")

    model_call_parser = subparsers.add_parser("model-call", help="Call a model API request packet")
    model_call_parser.add_argument("request")
    model_call_parser.add_argument("--path", default=".")
    model_call_parser.add_argument("--apply", action="store_true")
    model_call_parser.add_argument("--json", action="store_true")

    runtime_init_parser = subparsers.add_parser("runtime-init", help="Initialize stream runtime and corporate roles")
    runtime_init_parser.add_argument("--path", default=".")
    runtime_init_parser.add_argument("--force", action="store_true")

    role_show_parser = subparsers.add_parser("role-show", help="Show P1-P13 corporate role model")
    role_show_parser.add_argument("--path", default=".")
    role_show_parser.add_argument("--level", default="")
    role_show_parser.add_argument("--json", action="store_true")

    level_check_parser = subparsers.add_parser("level-check", help="Check whether a P-level has a capability")
    level_check_parser.add_argument("--path", default=".")
    level_check_parser.add_argument("--level", default="P1")
    level_check_parser.add_argument("--capability", default="")
    level_check_parser.add_argument("--json", action="store_true")

    agent_promote_parser = subparsers.add_parser("agent-promote", help="Assign a P-level to a governed subagent")
    agent_promote_parser.add_argument("subagent")
    agent_promote_parser.add_argument("--path", default=".")
    agent_promote_parser.add_argument("--level", default="P3")
    agent_promote_parser.add_argument("--title", default="")

    assignment_parser = subparsers.add_parser("assignment-create", help="Assign a subagent to a stream or issue")
    assignment_parser.add_argument("--path", default=".")
    assignment_parser.add_argument("--subagent", default="")
    assignment_parser.add_argument("--stream", default="")
    assignment_parser.add_argument("--issue", default="")
    assignment_parser.add_argument("--duty", default="")
    assignment_parser.add_argument("--level", default="")

    stream_start_parser = subparsers.add_parser("stream-start", help="Start a stream-structured runtime flow")
    stream_start_parser.add_argument("--path", default=".")
    stream_start_parser.add_argument("--issue", default="")
    stream_start_parser.add_argument("--title", default="")
    stream_start_parser.add_argument("--ceo-agent", default="")
    stream_start_parser.add_argument("--supervisor", default="human")

    stream_event_parser = subparsers.add_parser("stream-event", help="Append an event to a runtime stream")
    stream_event_parser.add_argument("stream")
    stream_event_parser.add_argument("--path", default=".")
    stream_event_parser.add_argument("--type", default="observation", dest="event_type")
    stream_event_parser.add_argument("--message", default="")
    stream_event_parser.add_argument("--actor", default="")
    stream_event_parser.add_argument("--payload", default="")

    stream_show_parser = subparsers.add_parser("stream-show", help="Show stream events")
    stream_show_parser.add_argument("stream")
    stream_show_parser.add_argument("--path", default=".")
    stream_show_parser.add_argument("--json", action="store_true")

    ceo_plan_parser = subparsers.add_parser("ceo-plan", help="Create a CEO agent stream plan")
    ceo_plan_parser.add_argument("--path", default=".")
    ceo_plan_parser.add_argument("--issue", default="")
    ceo_plan_parser.add_argument("--stream", default="")
    ceo_plan_parser.add_argument("--ceo-agent", default="")
    ceo_plan_parser.add_argument("--objective", default="")

    human_takeover_parser = subparsers.add_parser("human-takeover", help="Let a P13 human supervisor take over a stream")
    human_takeover_parser.add_argument("stream")
    human_takeover_parser.add_argument("--path", default=".")
    human_takeover_parser.add_argument("--reason", default="")
    human_takeover_parser.add_argument("--actor", default="human")

    runtime_status_parser = subparsers.add_parser("runtime-status", help="Show stream runtime status")
    runtime_status_parser.add_argument("--path", default=".")
    runtime_status_parser.add_argument("--json", action="store_true")

    executive_board_parser = subparsers.add_parser("executive-board", help="Show executive offices and appointments")
    executive_board_parser.add_argument("--path", default=".")
    executive_board_parser.add_argument("--office", default="")
    executive_board_parser.add_argument("--json", action="store_true")

    executive_appoint_parser = subparsers.add_parser("executive-appoint", help="Appoint a subagent to an executive office")
    executive_appoint_parser.add_argument("--path", default=".")
    executive_appoint_parser.add_argument("--office", required=True)
    executive_appoint_parser.add_argument("--subagent", required=True)
    executive_appoint_parser.add_argument("--by", default="")
    executive_appoint_parser.add_argument("--level", default="")
    executive_appoint_parser.add_argument("--mandate", default="")

    executive_delegate_parser = subparsers.add_parser("executive-delegate", help="Delegate stream or issue duty to an executive office")
    executive_delegate_parser.add_argument("--path", default=".")
    executive_delegate_parser.add_argument("--office", required=True)
    executive_delegate_parser.add_argument("--stream", default="")
    executive_delegate_parser.add_argument("--issue", default="")
    executive_delegate_parser.add_argument("--duty", default="")
    executive_delegate_parser.add_argument("--by", default="")

    executive_report_parser = subparsers.add_parser("executive-report", help="Write an executive office report")
    executive_report_parser.add_argument("--path", default=".")
    executive_report_parser.add_argument("--office", required=True)
    executive_report_parser.add_argument("--stream", default="")
    executive_report_parser.add_argument("--summary", default="")
    executive_report_parser.add_argument("--by", default="")

    role_report_parser = subparsers.add_parser("role-report", help="Write a report for any role, including CEO, QA, or Docs")
    role_report_parser.add_argument("--path", default=".")
    role_report_parser.add_argument("--role", required=True)
    role_report_parser.add_argument("--stream", default="")
    role_report_parser.add_argument("--summary", default="")
    role_report_parser.add_argument("--by", default="")
    role_report_parser.add_argument("--status", default="artifact")

    company_init_parser = subparsers.add_parser("company-init", help="Initialize Agent Company office method registry")
    company_init_parser.add_argument("--path", default=".")
    company_init_parser.add_argument("--force", action="store_true")

    office_method_list_parser = subparsers.add_parser("office-method-list", help="List Agent Company office methods")
    office_method_list_parser.add_argument("--path", default=".")
    office_method_list_parser.add_argument("--office", default="")
    office_method_list_parser.add_argument("--source", default="")
    office_method_list_parser.add_argument("--json", action="store_true")

    office_method_show_parser = subparsers.add_parser("office-method-show", help="Show one Agent Company office method")
    office_method_show_parser.add_argument("method")
    office_method_show_parser.add_argument("--path", default=".")
    office_method_show_parser.add_argument("--json", action="store_true")

    office_method_register_parser = subparsers.add_parser("office-method-register", help="Register a local Agent Company office method")
    office_method_register_parser.add_argument("--path", default=".")
    office_method_register_parser.add_argument("--name", required=True)
    office_method_register_parser.add_argument("--office", required=True)
    office_method_register_parser.add_argument("--title", default="")
    office_method_register_parser.add_argument("--purpose", default="")
    office_method_register_parser.add_argument("--source", default="local")
    office_method_register_parser.add_argument("--expected-artifact", default="")
    office_method_register_parser.add_argument("--publication-authority", default="none")

    office_action_start_parser = subparsers.add_parser("office-action-start", help="Start an office method action on a stream or issue")
    office_action_start_parser.add_argument("--path", default=".")
    office_action_start_parser.add_argument("--method", required=True)
    office_action_start_parser.add_argument("--office", default="")
    office_action_start_parser.add_argument("--stream", default="")
    office_action_start_parser.add_argument("--issue", default="")
    office_action_start_parser.add_argument("--actor", default="")
    office_action_start_parser.add_argument("--objective", default="")

    office_action_report_parser = subparsers.add_parser("office-action-report", help="Report the result of an office method action")
    office_action_report_parser.add_argument("action")
    office_action_report_parser.add_argument("--path", default=".")
    office_action_report_parser.add_argument("--summary", default="")
    office_action_report_parser.add_argument("--status", default="artifact")
    office_action_report_parser.add_argument("--evidence", default="")
    office_action_report_parser.add_argument("--by", default="")

    company_status_parser = subparsers.add_parser("company-status", help="Show Agent Company office method status")
    company_status_parser.add_argument("--path", default=".")
    company_status_parser.add_argument("--json", action="store_true")

    agent_hub_init_parser = subparsers.add_parser("agent-hub-init", help="Initialize the Agent Runtime Hub layer")
    agent_hub_init_parser.add_argument("--path", default=".")
    agent_hub_init_parser.add_argument("--force", action="store_true")

    runner_adapters_parser = subparsers.add_parser("runner-adapters", help="Show supported external agent runner adapters")
    runner_adapters_parser.add_argument("--path", default=".")
    runner_adapters_parser.add_argument("--json", action="store_true")

    subagent_spawn_parser = subparsers.add_parser("subagent-spawn", help="Create a runnable subagent spawn spec and prompt")
    subagent_spawn_parser.add_argument("--path", default=".")
    subagent_spawn_parser.add_argument("--subagent", default="")
    subagent_spawn_parser.add_argument("--runner", default="local")
    subagent_spawn_parser.add_argument("--role", default="")
    subagent_spawn_parser.add_argument("--issue", default="")
    subagent_spawn_parser.add_argument("--stream", default="")
    subagent_spawn_parser.add_argument("--task", default="")
    subagent_spawn_parser.add_argument("--cmd", default="")

    subagent_run_parser = subparsers.add_parser("subagent-run", help="Run or dry-run a subagent spawn through a runner adapter")
    subagent_run_parser.add_argument("spawn")
    subagent_run_parser.add_argument("--path", default=".")
    subagent_run_parser.add_argument("--apply", action="store_true")
    subagent_run_parser.add_argument("--cmd", default="")
    subagent_run_parser.add_argument("--timeout", type=int, default=120)
    subagent_run_parser.add_argument("--json", action="store_true")

    subagent_ingest_parser = subparsers.add_parser("subagent-ingest", help="Ingest a subagent output as a role report")
    subagent_ingest_parser.add_argument("spawn")
    subagent_ingest_parser.add_argument("--path", default=".")
    subagent_ingest_parser.add_argument("--summary", default="")
    subagent_ingest_parser.add_argument("--artifact", default="")
    subagent_ingest_parser.add_argument("--status", default="artifact")
    subagent_ingest_parser.add_argument("--by", default="")

    subagent_events_parser = subparsers.add_parser("subagent-events", help="Show Agent Runtime Hub events")
    subagent_events_parser.add_argument("--path", default=".")
    subagent_events_parser.add_argument("--spawn", default="")
    subagent_events_parser.add_argument("--json", action="store_true")

    metrics_init_parser = subparsers.add_parser("metrics-init", help="Initialize agent KPI/OKR metrics")
    metrics_init_parser.add_argument("--path", default=".")
    metrics_init_parser.add_argument("--force", action="store_true")

    metric_show_parser = subparsers.add_parser("metric-show", help="Show agent behavior metric definitions")
    metric_show_parser.add_argument("--path", default=".")
    metric_show_parser.add_argument("--metric", default="")
    metric_show_parser.add_argument("--json", action="store_true")

    metric_record_parser = subparsers.add_parser("metric-record", help="Record one agent behavior metric event")
    metric_record_parser.add_argument("--path", default=".")
    metric_record_parser.add_argument("--agent", default="")
    metric_record_parser.add_argument("--metric", required=True)
    metric_record_parser.add_argument("--score", type=int, required=True)
    metric_record_parser.add_argument("--stream", default="")
    metric_record_parser.add_argument("--issue", default="")
    metric_record_parser.add_argument("--evidence", default="")
    metric_record_parser.add_argument("--evaluator", default="")

    scorecard_parser = subparsers.add_parser("scorecard-build", help="Build an agent metric scorecard")
    scorecard_parser.add_argument("--path", default=".")
    scorecard_parser.add_argument("--agent", default="")
    scorecard_parser.add_argument("--stream", default="")
    scorecard_parser.add_argument("--json", action="store_true")

    okr_set_parser = subparsers.add_parser("okr-set", help="Set an agent-native OKR")
    okr_set_parser.add_argument("--path", default=".")
    okr_set_parser.add_argument("--agent", default="")
    okr_set_parser.add_argument("--objective", default="")
    okr_set_parser.add_argument("--metric", default="")
    okr_set_parser.add_argument("--target", type=float, default=0.0)
    okr_set_parser.add_argument("--stream", default="")
    okr_set_parser.add_argument("--owner", default="")

    okr_review_parser = subparsers.add_parser("okr-review", help="Review an agent-native OKR against scorecards")
    okr_review_parser.add_argument("okr")
    okr_review_parser.add_argument("--path", default=".")
    okr_review_parser.add_argument("--json", action="store_true")

    metrics_status_parser = subparsers.add_parser("metrics-status", help="Show agent metrics status")
    metrics_status_parser.add_argument("--path", default=".")
    metrics_status_parser.add_argument("--json", action="store_true")

    roundtable_init_parser = subparsers.add_parser("roundtable-init", help="Initialize roundtable meeting layer")
    roundtable_init_parser.add_argument("--path", default=".")
    roundtable_init_parser.add_argument("--force", action="store_true")

    meeting_start_parser = subparsers.add_parser("meeting-start", help="Start a roundtable meeting terminal")
    meeting_start_parser.add_argument("--path", default=".")
    meeting_start_parser.add_argument("--topic", default="")
    meeting_start_parser.add_argument("--stream", default="")
    meeting_start_parser.add_argument("--organizer", default="human")
    meeting_start_parser.add_argument("--agenda", default="")

    meeting_post_parser = subparsers.add_parser("meeting-post", help="Post a message into a roundtable meeting")
    meeting_post_parser.add_argument("meeting")
    meeting_post_parser.add_argument("--path", default=".")
    meeting_post_parser.add_argument("--actor", default="")
    meeting_post_parser.add_argument("--role", default="")
    meeting_post_parser.add_argument("--message", default="")

    meeting_show_parser = subparsers.add_parser("meeting-show", help="Show roundtable meeting terminal events")
    meeting_show_parser.add_argument("meeting")
    meeting_show_parser.add_argument("--path", default=".")
    meeting_show_parser.add_argument("--json", action="store_true")

    minutes_parser = subparsers.add_parser("minutes-generate", help="Generate meeting minutes")
    minutes_parser.add_argument("meeting")
    minutes_parser.add_argument("--path", default=".")

    vote_open_parser = subparsers.add_parser("vote-open", help="Open a weighted roundtable vote")
    vote_open_parser.add_argument("--path", default=".")
    vote_open_parser.add_argument("--meeting", required=True)
    vote_open_parser.add_argument("--motion", default="")
    vote_open_parser.add_argument("--by", default="")

    vote_cast_parser = subparsers.add_parser("vote-cast", help="Cast a weighted vote")
    vote_cast_parser.add_argument("vote")
    vote_cast_parser.add_argument("--path", default=".")
    vote_cast_parser.add_argument("--voter", default="")
    vote_cast_parser.add_argument("--choice", required=True)
    vote_cast_parser.add_argument("--weight", type=float, default=None)
    vote_cast_parser.add_argument("--reason", default="")

    vote_tally_parser = subparsers.add_parser("vote-tally", help="Tally a weighted vote")
    vote_tally_parser.add_argument("vote")
    vote_tally_parser.add_argument("--path", default=".")
    vote_tally_parser.add_argument("--close", action="store_true")
    vote_tally_parser.add_argument("--json", action="store_true")

    org_apply_parser = subparsers.add_parser("org-apply", help="Submit an organization application")
    org_apply_parser.add_argument("--path", default=".")
    org_apply_parser.add_argument("--applicant", default="")
    org_apply_parser.add_argument("--kind", default="")
    org_apply_parser.add_argument("--target", default="")
    org_apply_parser.add_argument("--justification", default="")
    org_apply_parser.add_argument("--meeting", default="")

    org_review_parser = subparsers.add_parser("org-review", help="Review an organization application")
    org_review_parser.add_argument("application")
    org_review_parser.add_argument("--path", default=".")
    org_review_parser.add_argument("--decision", required=True)
    org_review_parser.add_argument("--reviewer", default="")
    org_review_parser.add_argument("--notes", default="")

    roundtable_status_parser = subparsers.add_parser("roundtable-status", help="Show roundtable status")
    roundtable_status_parser.add_argument("--path", default=".")
    roundtable_status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "init":
        report = init_structure(args.path, force=args.force, minimal=args.minimal)
        print(f"Created {len(report['created'])} files. Skipped {len(report['skipped'])} existing files.")
        return 0

    if args.command == "validate":
        report = validate_structure(args.path, allow_todo=args.allow_todo)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("OK" if report["ok"] else "FAILED")
            if report["missing_files"]:
                print("Missing files:")
                for item in report["missing_files"]:
                    print(f"- {item}")
            if report["empty_files"]:
                print("Empty files:")
                for item in report["empty_files"]:
                    print(f"- {item}")
            if report["warnings"]:
                print("Warnings:")
                for item in report["warnings"]:
                    print(f"- {item}")
        return 0 if report["ok"] else 1

    if args.command == "summary":
        summary = summarize_structure(args.path)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print_summary(summary)
        return 0

    if args.command == "export":
        report = export_structure(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "rag-index":
        report = build_rag_index(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])} with {report['documents']} documents.")
        return 0

    if args.command == "context-pack":
        report = build_context_pack(
            args.path,
            output=args.output,
            max_chars_per_file=args.max_chars_per_file,
            json_output=args.json,
        )
        print(f"Wrote {Path(report['output'])} with {report['files']} files.")
        return 0

    if args.command == "mcp-manifest":
        report = build_mcp_manifest(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])} with {report['resources']} resources.")
        return 0

    if args.command == "skill-scaffold":
        report = scaffold_skill(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "agent-ready":
        report = check_agent_ready(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(report["status"].upper())
            if report["missing"]:
                print("Missing:")
                for item in report["missing"]:
                    print(f"- {item}")
            if report["warnings"]:
                print("Warnings:")
                for item in report["warnings"]:
                    print(f"- {item}")
        return 0 if report["ready"] else 1

    if args.command == "handoff-pack":
        report = build_handoff_pack(args.path, task=args.task, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "status-update":
        report = update_status(
            args.path,
            current=args.current,
            done=args.done,
            next_step=args.next_step,
            issue=args.issue,
            decision=args.decision,
        )
        print(f"Updated {Path(report['output'])}" if report["updated"] else "No status fields provided.")
        return 0

    if args.command == "toolbox-audit":
        report = audit_toolbox(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(report["status"].upper())
            if report["missing"]:
                print("Missing:")
                for item in report["missing"]:
                    print(f"- {item}")
            if report["warnings"]:
                print("Warnings:")
                for item in report["warnings"]:
                    print(f"- {item}")
        return 0 if report["ok"] else 1

    if args.command == "agent-task":
        report = create_agent_task(
            args.path,
            title=args.title,
            goal=args.goal,
            scope=args.scope,
            forbidden=args.forbidden,
            checks=args.checks,
            output_dir=args.output_dir,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "verify-log":
        report = append_verify_log(
            args.path,
            command=args.cmd,
            result=args.result,
            notes=args.notes,
            output=args.output,
            run=args.run,
            timeout=args.timeout,
        )
        print(f"Updated {Path(report['output'])}")
        if report["ran"]:
            print(f"Result: {report['result']} (exit {report['exit_code']})")
        return 0 if report["exit_code"] in (None, 0) else 1

    if args.command == "decision-log":
        report = append_decision_log(
            args.path,
            decision=args.decision,
            rationale=args.rationale,
            impact=args.impact,
            output=args.output,
        )
        print(f"Updated {Path(report['output'])}")
        return 0

    if args.command == "context-prune":
        report = build_context_prune(
            args.path,
            output=args.output,
            budget=args.budget,
            json_output=args.json,
        )
        print(f"Wrote {Path(report['output'])} with {report['files']} files.")
        return 0

    if args.command == "repo-map":
        report = scan_repo_map(args.path, output=args.output, max_files=args.max_files)
        print(f"Wrote {Path(report['output'])} with {report['files']} files.")
        return 0

    if args.command == "config":
        report = write_config(args.path, output=args.output, force=args.force)
        print(f"{'Wrote' if report['created'] else 'Exists'} {Path(report['output'])}")
        return 0

    if args.command == "agent-brief":
        report = build_agent_brief(
            args.path,
            task=args.task,
            output=args.output,
            budget=args.budget,
            refresh=not args.no_refresh,
        )
        print(f"Wrote {Path(report['output'])} ({report['status']})")
        return 0 if report["ready"] else 1

    if args.command == "run-task":
        report = run_agent_task(
            args.task_file,
            command=args.cmd,
            path=args.path,
            update_project_status=args.update_status,
            timeout=args.timeout,
        )
        print(f"Task result: {report['result']} ({report['task']})")
        return 0 if report["exit_code"] in (None, 0) else 1

    if args.command == "session-start":
        report = start_session(
            args.path,
            task=args.task,
            goal=args.goal,
            budget=args.budget,
            output=args.output,
        )
        print(f"Wrote {Path(report['brief'])} ({report['status']})")
        print(f"Task: {Path(report['task'])}")
        return 0 if report["status"] == "ready" else 1

    if args.command == "session-end":
        report = end_session(
            args.path,
            done=args.done,
            next_step=args.next_step,
            command=args.cmd,
            run=args.run,
            handoff_output=args.handoff_output,
        )
        print(f"Updated {Path(report['status'])}")
        print(f"Wrote {Path(report['handoff'])}")
        if report["verification"]:
            print(f"Verification: {Path(report['verification'])}")
        return 0

    if args.command == "mcp-scaffold":
        report = scaffold_mcp(args.path, output=args.output, force=args.force)
        print(f"{'Wrote' if report['created'] else 'Exists'} {Path(report['output'])}")
        return 0

    if args.command == "agent-export":
        if args.target == "all":
            report = export_all_agents(args.path, refresh=not args.no_refresh)
            for item in report["outputs"]:
                print(f"Wrote {Path(item)}")
        else:
            report = export_agent(args.path, target=args.target, output=args.output, refresh=not args.no_refresh)
            for item in report["outputs"]:
                print(f"Wrote {Path(item)}")
        return 0

    if args.command == "skill-export":
        report = export_skill(args.path, name=args.name, output_dir=args.output_dir, refresh=not args.no_refresh)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "agent-sync":
        report = sync_agent(args.path, target=args.target, skill_name=args.skill_name, budget=args.budget)
        print(f"Agent sync: {report['status']}")
        print(f"Brief: {Path(report['brief'])}")
        for item in report["agent_outputs"]:
            print(f"Agent file: {Path(item)}")
        print(f"Skill: {Path(report['skill'])}")
        return 0 if report["ready"] else 1

    if args.command == "mcp-server":
        if args.stdio:
            run_stdio_server(args.path)
            return 0
        if args.http:
            run_http_server(args.path, host=args.host, port=args.port)
            return 0
        print(json.dumps(run_server(args.path, args.request), indent=2))
        return 0

    if args.command == "network-init":
        report = init_network(args.path)
        print(f"Initialized {Path(report['output'])}")
        return 0

    if args.command == "issue-create":
        report = create_issue(
            args.path,
            title=args.title,
            body=args.body,
            labels=args.label,
            assignee=args.assignee,
            linked_snapshot=args.snapshot,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "issue-list":
        issues = list_issues(args.path, status=args.status)
        if args.json:
            print(json.dumps(issues, indent=2))
        else:
            for issue in issues:
                print(f"{issue['id']} [{issue['status']}] {issue['title']}")
        return 0

    if args.command == "branch-create":
        report = create_network_branch(
            args.path,
            name=args.name,
            purpose=args.purpose,
            issue=args.issue,
            context_branch=args.context_branch,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "pr-create":
        report = create_pr(
            args.path,
            title=args.title,
            body=args.body,
            issue=args.issue,
            branch=args.branch,
            checks=args.check,
            linked_snapshot=args.snapshot,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "review-create":
        report = create_review(
            args.path,
            pr=args.pr,
            reviewer=args.reviewer,
            decision=args.decision,
            body=args.body,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "project-board":
        report = build_project_board(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "network-sync":
        report = sync_network(args.path, target=args.target)
        print(f"Network sync: {report['status']}")
        print(f"Board: {Path(report['board'])}")
        return 0 if report["ready"] else 1

    if args.command == "context-init":
        report = init_context(args.path, project_name=args.project_name, force=args.force)
        print(f"Initialized {Path(report['output'])}")
        return 0

    if args.command == "context-snapshot":
        report = create_context_snapshot(
            args.path,
            message=args.message,
            from_file=args.from_file,
            branch=args.branch,
        )
        print(f"Snapshot {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "context-log":
        entries = list_context_snapshots(args.path)
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            for item in entries:
                print(f"{item['id']} {item['branch']} {item.get('message', '')}")
        return 0

    if args.command == "context-latest":
        print(latest_context_snapshot(args.path))
        return 0

    if args.command == "context-branch":
        report = create_context_branch(args.path, name=args.name, purpose=args.purpose)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "context-checkout":
        report = checkout_context_branch(args.path, name=args.name)
        print(f"Checked out context branch {report['branch']}")
        return 0

    if args.command == "context-tag":
        report = create_context_tag(args.path, name=args.name, snapshot=args.snapshot, meaning=args.meaning)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "context-export":
        report = export_context(args.path, output=args.output, include_roots=args.include_roots)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "context-route":
        report = route_context(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "network-snapshot":
        report = snapshot_network(args.path, message=args.message, target=args.target)
        print(f"Snapshot {report['snapshot']}: {Path(report['snapshot_file'])}")
        print(f"Updated network records: {len(report['updated'])}")
        return 0

    if args.command == "issue-close":
        report = update_issue_status(args.path, args.issue, "closed")
        print(f"Closed {report['id']}")
        return 0

    if args.command == "issue-reopen":
        report = update_issue_status(args.path, args.issue, "open")
        print(f"Reopened {report['id']}")
        return 0

    if args.command == "issue-assign":
        report = assign_issue(args.path, args.issue, args.assignee)
        print(f"Assigned {report['id']} to {args.assignee}")
        return 0

    if args.command == "issue-label":
        report = label_issue(args.path, args.issue, args.label)
        print(f"Labeled {report['id']}")
        return 0

    if args.command == "pr-ready":
        report = update_pr_status(args.path, args.pr, "ready")
        print(f"Ready {report['id']}")
        return 0

    if args.command == "pr-close":
        report = update_pr_status(args.path, args.pr, "closed")
        print(f"Closed {report['id']}")
        return 0

    if args.command == "pr-merge":
        report = merge_pr(args.path, args.pr, method=args.method)
        print(f"Merged {report['id']}")
        return 0

    if args.command == "comment-add":
        report = add_comment(args.path, target=args.target, author=args.author, body=args.body)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "comment-list":
        comments = list_comments(args.path, target=args.target)
        if args.json:
            print(json.dumps(comments, indent=2))
        else:
            for comment in comments:
                print(f"{comment['id']} {comment['target']} {comment['author']}: {comment['body']}")
        return 0

    if args.command == "timeline":
        events = timeline(args.path, target=args.target)
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            for event in events:
                print(f"{event.get('timestamp', '')} {event.get('event', '')} {event.get('id', '')}")
        return 0

    if args.command == "milestone-create":
        report = create_milestone(args.path, title=args.title, due=args.due, description=args.description)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "milestone-list":
        milestones = list_milestones(args.path)
        if args.json:
            print(json.dumps(milestones, indent=2))
        else:
            for milestone in milestones:
                print(f"{milestone['id']} [{milestone['status']}] {milestone['title']}")
        return 0

    if args.command == "github-export":
        report = github_export(args.path, item_type=args.type, item_id=args.id)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "github-dry-run":
        report = build_github_sync_plan(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        print(f"Mode: {report['mode']}")
        return 0

    if args.command == "github-labels-export":
        report = export_github_labels(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])} with {report['labels']} labels.")
        return 0

    if args.command == "github-issues-export":
        report = export_github_issues(args.path, output_dir=args.output_dir)
        print(f"Wrote {report['issues']} issues to {Path(report['output_dir'])}")
        return 0

    if args.command == "github-milestones-export":
        report = export_github_milestones(args.path, output=args.output)
        print(f"Wrote {Path(report['output'])} with {report['milestones']} milestones.")
        return 0

    if args.command == "github-sync":
        report = github_sync(
            args.path,
            dry_run=not args.apply,
            repo=args.repo,
            skip_missing_labels=args.skip_missing_labels,
        )
        if not report["ok"]:
            print(report.get("message") or "GitHub sync failed.")
            return 1
        print(f"GitHub bridge: {report['status']}")
        print(f"Plan: {Path(report['plan']['output'])}")
        return 0

    if args.command == "github-issue-create":
        report = github_issue_create(
            args.path,
            issue=args.issue,
            repo=args.repo,
            apply=args.apply,
            skip_missing_labels=args.skip_missing_labels,
        )
        if not report["ok"]:
            print(report.get("message") or "GitHub issue create failed.")
            return 1
        print(f"{report['status']}: {report['id']}")
        if report.get("url"):
            print(report["url"])
        return 0

    if args.command == "github-issues-create":
        report = github_issues_create(
            args.path,
            repo=args.repo,
            apply=args.apply,
            skip_missing_labels=args.skip_missing_labels,
        )
        if not report["ok"]:
            print("GitHub issues create failed.")
            print(f"Failed: {report['failed']}")
            return 1
        print(f"GitHub issues: {report['status']}")
        print(f"Created: {report['created']}; skipped: {report['skipped']}; dry-run: {report['dry_run']}")
        return 0

    if args.command == "github-config":
        report = write_github_config(args.path, repo=args.repo, output=args.output, force=args.force, auto=args.auto)
        print(f"{'Wrote' if report['created'] else 'Exists'} {Path(report['output'])}")
        return 0

    if args.command == "github-doctor":
        report = github_doctor(args.path, repo=args.repo)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("OK" if report["ok"] else "FAILED")
            for check in report["checks"]:
                print(f"- {check['name']}: {'ok' if check['ok'] else 'failed'}")
        return 0 if report["ok"] else 1

    if args.command == "github-labels-create":
        report = github_labels_create(args.path, repo=args.repo, apply=args.apply)
        if not report["ok"]:
            print(report.get("message") or "GitHub labels create failed.")
            return 1
        print(f"GitHub labels: {report['status']}; missing: {report['missing']}; created: {report['created']}")
        return 0

    if args.command == "github-milestones-create":
        report = github_milestones_create(args.path, repo=args.repo, apply=args.apply)
        if not report["ok"]:
            print("GitHub milestones create failed.")
            return 1
        print(f"GitHub milestones: {report['status']}")
        return 0

    if args.command == "github-pull":
        report = github_pull(args.path, repo=args.repo)
        if not report["ok"]:
            print(report.get("message") or "GitHub pull failed.")
            return 1
        print(f"GitHub pull: {len(report['results'])} issues")
        return 0

    if args.command == "github-sync-report":
        report = github_sync_report(args.path, repo=args.repo, output=args.output)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "github-comment":
        report = github_comment(args.path, issue=args.issue, body=args.body, repo=args.repo, apply=args.apply)
        if not report["ok"]:
            print(report.get("message") or "GitHub comment failed.")
            return 1
        print(f"{report['status']}: {report['id']}")
        return 0

    if args.command == "task-from-issue":
        report = task_from_issue(args.path, issue=args.issue, output_dir=args.output_dir)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "issue-from-task":
        report = issue_from_task(args.path, task_file=args.task_file, label=args.label)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "work-start":
        report = work_start(args.path, issue=args.issue, task=args.task, note=args.note)
        print(f"Started {report['issue']}: {Path(report['session'])}")
        return 0

    if args.command == "work-end":
        report = work_end(
            args.path,
            done=args.done,
            next_step=args.next_step,
            command=args.cmd,
            run=args.run,
            issue=args.issue,
            github_comment_body=args.github_comment,
            apply_comment=args.apply_comment,
        )
        print(f"Ended {report['issue'] or 'work session'}")
        print(f"Report: {Path(report['sync_report'])}")
        return 0

    if args.command == "worknet-status":
        report = worknet_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Repo: {report['repo'] or 'not configured'}")
            print(f"Issues: {report['issues']}")
            if report["current"]:
                print(f"Current: {report['current'].get('issue')}")
        return 0 if report["ready"] else 1

    if args.command == "governance-init":
        report = governance_init(args.path, force=args.force)
        print(f"Governance: {Path(report['output'])}")
        print(f"Policy: {Path(report['policy'])}")
        return 0

    if args.command == "policy-show":
        report = policy_show(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Policy version: {report['version']}")
            print("Permissions:")
            for name in report["permissions"]:
                print(f"- {name}")
        return 0

    if args.command == "subagent-plan":
        report = subagent_plan(args.path, issue=args.issue, output_dir=args.output_dir)
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "subagent-create":
        report = subagent_create(
            args.path,
            name=args.name,
            permission=args.permission,
            goal=args.goal,
            issue=args.issue,
            allowed_paths=args.allowed_path or None,
        )
        print(f"Created {report['id']}: {Path(report['output'])}")
        print(f"Sandbox: {Path(report['sandbox'])}")
        return 0

    if args.command == "approval-request":
        report = approval_request(
            args.path,
            subagent=args.subagent,
            action=args.action,
            target=args.target,
            reason=args.reason,
        )
        print(f"Requested {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "approval-grant":
        report = approval_grant(args.path, approval=args.approval, granted_by=args.granted_by, ttl_hours=args.ttl_hours)
        print(f"Granted {report['id']}")
        print(f"Token: {Path(report['token'])}")
        return 0

    if args.command == "token-revoke":
        report = token_revoke(args.path, token=args.token, revoked_by=args.revoked_by, reason=args.reason)
        print(f"Revoked {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "sandbox-check":
        report = sandbox_check(args.path, subagent=args.subagent, target_path=args.target)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{report['status'].upper()}: {report['path']}")
        return 0 if report["ok"] else 1

    if args.command == "command-check":
        report = command_check(args.path, command=args.cmd, subagent=args.subagent, permission=args.permission)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{report['status'].upper()}: {report['level']} command under {report['permission']}")
        return 0 if report["ok"] else 1

    if args.command == "gate-check":
        report = gate_check(args.path, action=args.action, subagent=args.subagent, target=args.target)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{'APPROVED' if report['ok'] else 'BLOCKED'}: {report['action']}")
            print(report["message"])
            if report["matching_tokens"]:
                print(f"Tokens: {', '.join(report['matching_tokens'])}")
        return 0 if report["ok"] else 1

    if args.command == "secret-scan":
        report = secret_scan(args.path, target_path=args.target)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{'CLEAR' if report['ok'] else 'FINDINGS'}: {report['path']}")
        return 0 if report["ok"] else 1

    if args.command == "governance-status":
        report = governance_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Subagents: {report['subagents']}")
            print(f"Approvals: {report['approvals']}")
            print(f"Tokens: {report['tokens']}")
            print(f"Audit events: {report['audit_events']}")
        return 0 if report["ready"] else 1

    if args.command == "model-config":
        report = model_config_init(args.path, force=args.force)
        if args.json:
            print(json.dumps(load_model_providers(args.path), indent=2))
        else:
            print(f"Model API: {Path(report['output'])}")
            print(f"Providers: {Path(report['providers'])}")
        return 0

    if args.command == "model-provider-set":
        report = model_provider_set(
            args.path,
            provider=args.provider,
            endpoint=args.endpoint,
            api_key_env=args.api_key_env,
            default_model=args.model,
            provider_type=args.provider_type,
        )
        print(f"Updated {report['provider']}: {Path(report['output'])}")
        return 0

    if args.command == "model-doctor":
        report = model_doctor(args.path, provider=args.provider)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready_for_live_call"] else "NEEDS SETUP")
            print(f"Provider: {report['provider']}")
            print(f"Endpoint: {report['endpoint'] or 'not configured'}")
            print(f"API key env: {report['api_key_env'] or 'not configured'}")
            print(f"API key present: {report['api_key_present']}")
            print(f"Default model: {report['default_model'] or 'not configured'}")
        return 0 if report["ok"] else 1

    if args.command == "model-request":
        report = model_request_build(
            args.path,
            provider=args.provider,
            model=args.model,
            prompt=args.prompt,
            issue=args.issue,
            subagent=args.subagent,
            system=args.system,
            output_dir=args.output_dir,
        )
        print(f"Wrote {Path(report['output'])}")
        return 0

    if args.command == "model-capability-check":
        report = model_capability_check(args.path, subagent=args.subagent, action=args.action, target=args.provider)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("ALLOWED" if report["ok"] else "DENIED")
            print(f"Subagent: {report['subagent'] or 'not specified'}")
            print(f"Provider: {report['target']}")
        return 0 if report["ok"] else 1

    if args.command == "model-call":
        report = model_call(args.path, request=args.request, apply=args.apply)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{report['status'].upper()}: {args.request}")
            if report.get("output"):
                print(f"Response: {Path(report['output'])}")
            if report.get("message"):
                print(report["message"])
        return 0 if report["ok"] else 1

    if args.command == "runtime-init":
        report = runtime_init(args.path, force=args.force)
        print(f"Runtime: {Path(report['output'])}")
        print(f"Roles: {Path(report['roles'])}")
        return 0

    if args.command == "role-show":
        report = role_show(args.path, level=args.level)
        if args.json:
            print(json.dumps(report, indent=2))
        elif args.level:
            role = report["role"]
            print(f"{report['level']}: {role['title']}")
            print(role["scope"])
        else:
            print(f"Role model version: {report['version']}")
            for level, role in report["levels"].items():
                print(f"- {level}: {role['title']}")
        return 0

    if args.command == "level-check":
        report = level_allows(args.path, level=args.level, capability=args.capability)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("ALLOWED" if report["ok"] else "DENIED")
            print(f"Level: {report['level']}")
            if args.capability:
                print(f"Capability: {args.capability}")
        return 0 if report["ok"] else 1

    if args.command == "agent-promote":
        report = agent_promote(args.path, subagent=args.subagent, level=args.level, title=args.title)
        print(f"Promoted {report['id']} to {report['level']}: {Path(report['output'])}")
        return 0

    if args.command == "assignment-create":
        report = assignment_create(
            args.path,
            subagent=args.subagent,
            stream=args.stream,
            issue=args.issue,
            duty=args.duty,
            level=args.level,
        )
        print(f"Assigned {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "stream-start":
        report = stream_start(
            args.path,
            issue=args.issue,
            title=args.title,
            ceo_agent=args.ceo_agent,
            supervisor=args.supervisor,
        )
        print(f"Started {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "stream-event":
        payload = json.loads(args.payload) if args.payload else {}
        report = stream_event(
            args.path,
            stream=args.stream,
            event_type=args.event_type,
            message=args.message,
            actor=args.actor,
            payload=payload,
        )
        print(f"Appended {report['event']['event_id']} to {report['stream']}")
        return 0

    if args.command == "stream-show":
        report = stream_show(args.path, stream=args.stream)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Stream: {report['stream']}")
            print(f"Events: {report['count']}")
            for event in report["events"]:
                print(f"- {event['event_id']} {event['type']}: {event.get('message', '')}")
        return 0

    if args.command == "ceo-plan":
        report = ceo_plan(
            args.path,
            issue=args.issue,
            stream=args.stream,
            ceo_agent=args.ceo_agent,
            objective=args.objective,
        )
        print(f"CEO plan {report['id']}: {Path(report['output'])}")
        print(f"Stream: {report['stream']}")
        return 0

    if args.command == "human-takeover":
        report = human_takeover(args.path, stream=args.stream, reason=args.reason, actor=args.actor)
        print(f"Human takeover: {report['event']['event_id']} on {report['stream']}")
        return 0

    if args.command == "runtime-status":
        report = runtime_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Streams: {report['streams']}")
            print(f"Assignments: {report['assignments']}")
            print(f"CEO plans: {report['ceo_plans']}")
            print(f"Executive appointments: {report['executive_appointments']}")
            print(f"Executive reports: {report['executive_reports']}")
            print(f"Role reports: {report['role_reports']}")
            if report["current"]:
                print(f"Current stream: {report['current'].get('stream')} ({report['current'].get('state')})")
        return 0 if report["ready"] else 1

    if args.command == "executive-board":
        report = executive_board(args.path, office=args.office)
        if args.json:
            print(json.dumps(report, indent=2))
        elif args.office:
            appointment = report.get("appointment") or {}
            definition = report["definition"]
            print(f"{report['office']}: {definition['title']}")
            print(definition["domain"])
            print(f"Appointed: {appointment.get('subagent', 'not appointed')}")
        else:
            print(f"Executive board version: {report['version']}")
            for office, definition in report["offices"].items():
                appointed = report.get("appointments", {}).get(office, {}).get("subagent", "open")
                print(f"- {office}: {definition['title']} ({appointed})")
        return 0

    if args.command == "executive-appoint":
        try:
            report = executive_appoint(
                args.path,
                office=args.office,
                subagent=args.subagent,
                by=args.by,
                level=args.level,
                mandate=args.mandate,
            )
        except PermissionError as exc:
            print(str(exc))
            return 1
        print(f"Appointed {report['office']} -> {report['payload']['subagent']}: {Path(report['output'])}")
        return 0

    if args.command == "executive-delegate":
        try:
            report = executive_delegate(
                args.path,
                office=args.office,
                stream=args.stream,
                issue=args.issue,
                duty=args.duty,
                by=args.by,
            )
        except (PermissionError, ValueError) as exc:
            print(str(exc))
            return 1
        print(f"Delegated {report['office']} via {report['assignment']['id']}")
        return 0

    if args.command == "executive-report":
        report = executive_report(
            args.path,
            office=args.office,
            stream=args.stream,
            summary=args.summary,
            by=args.by,
        )
        print(f"Report {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "role-report":
        report = role_report(
            args.path,
            role=args.role,
            stream=args.stream,
            summary=args.summary,
            by=args.by,
            status=args.status,
        )
        print(f"Role report {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "company-init":
        report = company_init(args.path, force=args.force)
        print(f"Agent Company: {Path(report['output'])}")
        print(f"Office methods: {Path(report['registry'])}")
        return 0

    if args.command == "office-method-list":
        report = office_method_list(args.path, office=args.office, source=args.source)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Office methods: {report['count']}")
            for name, method in report["methods"].items():
                print(f"- {name}: {method['office']} - {method['title']} ({method['source']})")
        return 0

    if args.command == "office-method-show":
        try:
            report = office_method_show(args.path, args.method)
        except ValueError as exc:
            print(str(exc))
            return 1
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            definition = report["definition"]
            print(f"{report['method']}: {definition['title']}")
            print(f"Office: {definition['office']}")
            print(f"Source: {definition['source']}")
            print(f"Purpose: {definition['purpose']}")
            print(f"Expected artifact: {definition['expected_artifact']}")
            print(f"Publication authority: {definition['publication_authority']}")
        return 0

    if args.command == "office-method-register":
        report = office_method_register(
            args.path,
            name=args.name,
            office=args.office,
            title=args.title,
            purpose=args.purpose,
            source=args.source,
            expected_artifact=args.expected_artifact,
            publication_authority=args.publication_authority,
        )
        print(f"Registered office method {report['method']}: {Path(report['output'])}")
        return 0

    if args.command == "office-action-start":
        try:
            report = office_action_start(
                args.path,
                method=args.method,
                office=args.office,
                stream=args.stream,
                issue=args.issue,
                actor=args.actor,
                objective=args.objective,
            )
        except (ValueError, FileNotFoundError) as exc:
            print(str(exc))
            return 1
        print(f"Office action {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "office-action-report":
        try:
            report = office_action_report(
                args.path,
                action=args.action,
                summary=args.summary,
                status=args.status,
                evidence=args.evidence,
                by=args.by,
            )
        except FileNotFoundError as exc:
            print(str(exc))
            return 1
        print(f"Office report {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "company-status":
        report = company_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Methods: {report['methods']}")
            print(f"Actions: {report['actions']}")
            print(f"Reports: {report['reports']}")
            print(f"Company log events: {report['company_log_events']}")
        return 0 if report["ready"] else 1

    if args.command == "agent-hub-init":
        report = agent_hub_init(args.path, force=args.force)
        print(f"Agent hub: {Path(report['output'])}")
        print(f"Adapters: {Path(report['adapters'])}")
        return 0

    if args.command == "runner-adapters":
        report = runner_adapters(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Runner adapter version: {report['version']}")
            for name, adapter in report["adapters"].items():
                print(f"- {name}: {adapter['kind']} - {adapter['summary']}")
        return 0

    if args.command == "subagent-spawn":
        try:
            report = subagent_spawn(
                args.path,
                subagent=args.subagent,
                runner=args.runner,
                role=args.role,
                issue=args.issue,
                stream=args.stream,
                task=args.task,
                command=args.cmd,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(str(exc))
            return 1
        print(f"Spawn {report['id']}: {Path(report['output'])}")
        print(f"Prompt: {Path(report['prompt'])}")
        return 0

    if args.command == "subagent-run":
        try:
            report = subagent_run(
                args.path,
                spawn=args.spawn,
                apply=args.apply,
                command=args.cmd,
                timeout=args.timeout,
            )
        except FileNotFoundError as exc:
            print(str(exc))
            return 1
        if args.json:
            print(json.dumps(report["payload"], indent=2))
        else:
            print(f"{report['payload']['status'].upper()}: {report['id']}")
            print(f"Run: {Path(report['output'])}")
            if report["payload"].get("stderr"):
                print(report["payload"]["stderr"])
        return 0 if report["ok"] else 1

    if args.command == "subagent-ingest":
        try:
            report = subagent_ingest(
                args.path,
                spawn=args.spawn,
                summary=args.summary,
                artifact=args.artifact,
                status=args.status,
                by=args.by,
            )
        except FileNotFoundError as exc:
            print(str(exc))
            return 1
        print(f"Ingest {report['id']}: {Path(report['output'])}")
        print(f"Role report: {Path(report['role_report']['output'])}")
        return 0

    if args.command == "subagent-events":
        report = subagent_events(args.path, spawn=args.spawn)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Events: {report['count']}")
            for event in report["events"]:
                print(f"- {event['timestamp']} {event['event']}")
        return 0

    if args.command == "metrics-init":
        report = metrics_init(args.path, force=args.force)
        print(f"Metrics: {Path(report['output'])}")
        print(f"Definitions: {Path(report['definitions'])}")
        return 0

    if args.command == "metric-show":
        report = metric_show(args.path, metric=args.metric)
        if args.json:
            print(json.dumps(report, indent=2))
        elif args.metric:
            definition = report["definition"]
            print(f"{report['metric']}")
            print(definition["question"])
        else:
            print(f"Metric model version: {report['version']}")
            for metric, definition in report["metrics"].items():
                print(f"- {metric}: {definition['question']}")
        return 0

    if args.command == "metric-record":
        try:
            report = metric_record(
                args.path,
                agent=args.agent,
                metric=args.metric,
                score=args.score,
                stream=args.stream,
                issue=args.issue,
                evidence=args.evidence,
                evaluator=args.evaluator,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print(f"Metric {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "scorecard-build":
        report = scorecard_build(args.path, agent=args.agent, stream=args.stream)
        if args.json:
            print(json.dumps(report["payload"], indent=2))
        else:
            print(f"Scorecard {report['id']}: {Path(report['output'])}")
            print(f"Overall: {report['payload']['overall']}")
        return 0

    if args.command == "okr-set":
        try:
            report = okr_set(
                args.path,
                agent=args.agent,
                objective=args.objective,
                metric=args.metric,
                target=args.target,
                stream=args.stream,
                owner=args.owner,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print(f"OKR {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "okr-review":
        report = okr_review(args.path, okr=args.okr)
        if args.json:
            print(json.dumps(report["review"], indent=2))
        else:
            print("ACHIEVED" if report["review"]["achieved"] else "ACTIVE")
            print(f"Current: {report['review']['current']}")
            print(f"Target: {report['review']['target']}")
        return 0

    if args.command == "metrics-status":
        report = metrics_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Metric events: {report['metric_events']}")
            print(f"Scorecards: {report['scorecards']}")
            print(f"OKRs: {report['okrs']}")
        return 0 if report["ready"] else 1

    if args.command == "roundtable-init":
        report = roundtable_init(args.path, force=args.force)
        print(f"Roundtable: {Path(report['output'])}")
        print(f"Rules: {Path(report['rules'])}")
        return 0

    if args.command == "meeting-start":
        report = meeting_start(
            args.path,
            topic=args.topic,
            stream=args.stream,
            organizer=args.organizer,
            agenda=args.agenda,
        )
        print(f"Meeting {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "meeting-post":
        report = meeting_post(args.path, meeting=args.meeting, actor=args.actor, role=args.role, message=args.message)
        print(f"Posted {report['event']['event_id']} to {report['meeting']}")
        return 0

    if args.command == "meeting-show":
        report = meeting_show(args.path, meeting=args.meeting)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Meeting: {report['meeting']}")
            print(f"Events: {report['count']}")
            for event in report["events"]:
                actor = event.get("actor") or event.get("organizer") or event.get("voter") or ""
                print(f"- {event['event_id']} {event['type']} {actor}: {event.get('message', event.get('motion', ''))}")
        return 0

    if args.command == "minutes-generate":
        report = minutes_generate(args.path, meeting=args.meeting)
        print(f"Minutes {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "vote-open":
        report = vote_open(args.path, meeting=args.meeting, motion=args.motion, by=args.by)
        print(f"Vote {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "vote-cast":
        try:
            report = vote_cast(args.path, vote=args.vote, voter=args.voter, choice=args.choice, weight=args.weight, reason=args.reason)
        except ValueError as exc:
            print(str(exc))
            return 1
        print(f"Vote cast by {report['record']['voter']} with weight {report['record']['weight']}")
        return 0

    if args.command == "vote-tally":
        report = vote_tally(args.path, vote=args.vote, close=args.close)
        if args.json:
            print(json.dumps(report["tally"], indent=2))
        else:
            print("PASSED" if report["tally"]["passed"] else "FAILED")
            print(f"Yes: {report['tally']['totals']['yes']}")
            print(f"No: {report['tally']['totals']['no']}")
            print(f"Abstain: {report['tally']['totals']['abstain']}")
        return 0

    if args.command == "org-apply":
        report = org_apply(
            args.path,
            applicant=args.applicant,
            kind=args.kind,
            target=args.target,
            justification=args.justification,
            meeting=args.meeting,
        )
        print(f"Application {report['id']}: {Path(report['output'])}")
        return 0

    if args.command == "org-review":
        try:
            report = org_review(args.path, application=args.application, decision=args.decision, reviewer=args.reviewer, notes=args.notes)
        except (PermissionError, ValueError) as exc:
            print(str(exc))
            return 1
        print(f"{report['review']['decision'].upper()}: {args.application}")
        return 0

    if args.command == "roundtable-status":
        report = roundtable_status(args.path)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("READY" if report["ready"] else "NEEDS SETUP")
            print(f"Meetings: {report['meetings']}")
            print(f"Minutes: {report['minutes']}")
            print(f"Votes: {report['votes']}")
            print(f"Applications: {report['applications']}")
        return 0 if report["ready"] else 1

    parser.error("Unknown command")
    return 2


app = main


if __name__ == "__main__":
    raise SystemExit(main())
