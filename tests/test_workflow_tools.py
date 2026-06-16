import json

from structure_rule_kit import (
    audit_toolbox,
    build_handoff_pack,
    check_agent_ready,
    init_structure,
    update_status,
)


def fill_ready_fields(tmp_path):
    (tmp_path / "structure" / "project_plan.md").write_text(
        """# Project Plan

## Project Name

Example Project

## Core Goal

Build a small test project.

## Current Stage

Implementation

## Main Users

Developers.

## Current Priority

Finish the agent toolbox.

## Non-Goals

Do not add unrelated templates.

## Open Questions

- None.
""",
        encoding="utf-8",
    )
    (tmp_path / "structure" / "metrics.md").write_text(
        """# Metrics

## Definition of Done

- The requested behavior is implemented.

## Required Checks

- python3 -m py_compile structure_rule_kit/*.py tests/*.py

## Test Requirements

- Run workflow tool tests.

## Documentation Requirements

- Update README.

## Quality Bar

- Keep tools scriptable.

## Submission Checklist

- Checks run.
""",
        encoding="utf-8",
    )
    (tmp_path / "structure" / "important_files.md").write_text(
        """# Important Files

## Core Source Files

- structure_rule_kit/

## Configuration Files

- pyproject.toml

## Documentation Files

- README.md

## Do-Not-Touch Files

- None.

## Generated Files

- STRUCTURE_CONTEXT_PACK.md

## Temporary Files

- None.
""",
        encoding="utf-8",
    )
    (tmp_path / "structure" / "toolbox.md").write_text(
        """# Toolbox

## Package Manager

- pip

## Build Commands

- python3 -m build

## Test Commands

- pytest

## Lint Commands

- ruff check .

## Format Commands

- ruff format .

## Useful Scripts

- structure-rule validate

## External Tools

- git
""",
        encoding="utf-8",
    )
    update_status(
        str(tmp_path),
        current="Implement workflow tools.",
        done="Created structure layer.",
        next_step="Run tests.",
    )


def test_agent_ready_reports_missing_defaults(tmp_path):
    init_structure(str(tmp_path))
    report = check_agent_ready(str(tmp_path))
    assert report["ready"] is False
    assert report["status"] == "blocked"
    assert report["missing"]
    assert report["issues"]


def test_agent_ready_after_required_fields(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = check_agent_ready(str(tmp_path))
    assert report["ready"] is True
    assert report["status"] == "ready"


def test_handoff_pack(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = build_handoff_pack(str(tmp_path), task="Continue implementation")
    output = tmp_path / "STRUCTURE_HANDOFF.md"
    assert report["output"].endswith("STRUCTURE_HANDOFF.md")
    assert "Continue implementation" in output.read_text(encoding="utf-8")


def test_status_update(tmp_path):
    init_structure(str(tmp_path))
    report = update_status(str(tmp_path), done="Added tool", next_step="Run checks", decision="Keep tools modular")
    text = (tmp_path / "structure" / "status.md").read_text(encoding="utf-8")
    assert report["updated"] is True
    assert "Added tool" in text
    assert "Activity Log" in text


def test_toolbox_audit(tmp_path):
    init_structure(str(tmp_path))
    report = audit_toolbox(str(tmp_path))
    assert report["ok"] is False
    assert report["status"] == "blocked"
    fill_ready_fields(tmp_path)
    report = audit_toolbox(str(tmp_path))
    assert report["ok"] is True
    assert report["status"] == "ready"
