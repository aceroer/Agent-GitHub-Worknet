#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess


def run(command: list[str]) -> dict:
    result = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Experimental GitHub environment doctor.")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/name form.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args()

    report = {
        "repo": args.repo,
        "checks": [],
        "ok": True,
    }

    gh_path = shutil.which("gh")
    report["checks"].append({"name": "gh-installed", "ok": gh_path is not None, "path": gh_path})
    if gh_path is None:
        report["ok"] = False
        return print_report(report, args.json)

    for name, command in [
        ("gh-auth", ["gh", "auth", "status"]),
        ("repo-view", ["gh", "repo", "view", args.repo, "--json", "name,owner,visibility,url"]),
        ("issues-list", ["gh", "issue", "list", "--repo", args.repo, "--limit", "1", "--json", "number,state,title,url"]),
        ("labels-list", ["gh", "label", "list", "--repo", args.repo, "--json", "name", "--limit", "1000"]),
        ("milestones-list", ["gh", "api", f"repos/{args.repo}/milestones?state=all"]),
    ]:
        item = run(command)
        item["name"] = name
        report["checks"].append(item)
        if not item["ok"]:
            report["ok"] = False

    return print_report(report, args.json)


def print_report(report: dict, json_output: bool) -> int:
    if json_output:
        print(json.dumps(report, indent=2))
    else:
        print("OK" if report["ok"] else "FAILED")
        for check in report["checks"]:
            status = "ok" if check["ok"] else "failed"
            print(f"- {check['name']}: {status}")
            if not check["ok"] and check.get("stderr"):
                print(f"  {check['stderr']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
