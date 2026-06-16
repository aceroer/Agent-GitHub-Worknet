from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_brief import build_agent_brief
from .agent_export import export_agent, export_all_agents
from .agent_ready import check_agent_ready
from .agent_sync import sync_agent
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
from .handoff import build_handoff_pack
from .mcp_manifest import build_mcp_manifest
from .mcp_scaffold import scaffold_mcp
from .mcp_server import run_server
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
from .run_task import run_agent_task
from .session import end_session, start_session
from .skill_scaffold import scaffold_skill
from .skill_export import export_skill
from .status_update import update_status
from .summary import summarize_structure
from .task import create_agent_task
from .toolbox_audit import audit_toolbox
from .validator import validate_structure
from .verify_log import append_verify_log


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

    mcp_server_parser = subparsers.add_parser("mcp-server", help="Run a minimal JSON MCP-like resource endpoint")
    mcp_server_parser.add_argument("--path", default=".")
    mcp_server_parser.add_argument("--request", default="")

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

    parser.error("Unknown command")
    return 2


app = main


if __name__ == "__main__":
    raise SystemExit(main())
