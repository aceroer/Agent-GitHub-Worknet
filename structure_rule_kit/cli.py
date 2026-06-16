from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent_ready import check_agent_ready
from .context_pack import build_context_pack
from .context_prune import build_context_prune
from .decision_log import append_decision_log
from .exporter import export_structure
from .generator import init_structure
from .handoff import build_handoff_pack
from .mcp_manifest import build_mcp_manifest
from .rag_index import build_rag_index
from .repo_map import scan_repo_map
from .skill_scaffold import scaffold_skill
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

    parser.error("Unknown command")
    return 2


app = main


if __name__ == "__main__":
    raise SystemExit(main())
