from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exporter import export_structure
from .generator import init_structure
from .summary import summarize_structure
from .validator import validate_structure


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

    parser.error("Unknown command")
    return 2


app = main


if __name__ == "__main__":
    raise SystemExit(main())
