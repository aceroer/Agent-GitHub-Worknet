from __future__ import annotations

from collections import OrderedDict


ROOT_TEMPLATE = """# Structure Rule

This file is the entry point for AI agents working on this repository.

Before editing code, read these files in order:

1. `structure/project_plan.md`
2. `structure/rules.md`
3. `structure/roadmap.md`
4. `structure/important_files.md`
5. `structure/action_protocol.md`
6. `structure/metrics.md`
7. `structure/toolbox.md`
8. `structure/status.md`
9. `structure/agent_notes.md`

## Agent Rule

Do not start editing before understanding:

- the current project goal
- the current roadmap stage
- important files
- forbidden actions
- completion metrics

## Update Rule

When a meaningful task is completed, update:

- `structure/status.md`
- relevant roadmap or notes if needed

## Completion Rule

A task is not complete until it satisfies `structure/metrics.md`.
"""


STRUCTURE_TEMPLATES = OrderedDict(
    [
        (
            "project_plan.md",
            """# Project Plan

## Project Name

Not specified yet.

## Core Goal

Not specified yet.

## Current Stage

Not specified yet.

## Main Users

Not specified yet.

## Current Priority

Not specified yet.

## Non-Goals

Not specified yet.

## Open Questions

- Not specified yet.
""",
        ),
        (
            "roadmap.md",
            """# Roadmap

## Version 0.1

Create a stable project structure layer:

- `STRUCTURE_RULE.md`
- `structure/project_plan.md`
- `structure/roadmap.md`
- `structure/rules.md`
- `structure/action_protocol.md`
- `structure/metrics.md`
- `structure/toolbox.md`
- `structure/important_files.md`
- `structure/status.md`
- `structure/agent_notes.md`

Support `init`, `validate`, `summary`, and `export`.

## Version 0.2

Add scriptable agent integration tools rather than more templates:

- build a compact RAG index from the structure files
- export bounded context packs for coding and research agents
- generate and check MCP-facing tool/resource manifests
- scaffold local skill entry points from an existing project structure
- audit whether an agent has enough structure to start safely

## Version 0.3

Add a lightweight workflow runner:

- generate agent startup briefs
- run structured task files and record verification evidence
- standardize session start and session end
- write reusable config defaults
- scaffold a minimal MCP resource server

## Long-Term Direction

Become a lightweight structure/runtime bridge for agent workflows.

The kit should not become a template marketplace. It should help agents read,
index, validate, expose, and reuse the project structure that already exists.

## Version 0.5

Add a local agent network layer:

- local agent issues
- local exploration branches
- local PR records
- local review records
- local project board
- network sync into agent exports and skills

## Version 0.6

Add Context Git integration:

- local `.contextgit/` workflow state repository
- context snapshots
- semantic context branches
- stable context tags
- context export packets
- network snapshot links

## Version 0.7

Add local GitHub-like lifecycle semantics:

- issue assignment, labels, close, and reopen
- PR ready, close, and semantic merge
- comments and timelines
- milestones
- GitHub-ready markdown export

## Version 0.8

Add a dry-run GitHub bridge layer:

- remote metadata for local network records
- label export
- batch issue export
- milestone export
- dry-run sync plans
- no remote API writes in this phase

## Deferred Ideas

- Optional project presets, only if they support the scriptable integration layer.
""",
        ),
        (
            "rules.md",
            """# Rules

## General Rules

- Preserve project intent.

## Coding Rules

- Follow existing style.

## Documentation Rules

- Keep documentation accurate and concise.

## Testing Rules

- Run relevant checks before marking work complete.

## Safety Rules

- Do not expose secrets or credentials.

## Things Not To Do

- Do not rewrite unrelated files without a clear reason.
""",
        ),
        (
            "action_protocol.md",
            """# Action Protocol

## Before Editing

- Read `STRUCTURE_RULE.md`.
- Check important files and current status.

## During Editing

- Keep changes scoped.
- Preserve manual notes and user-owned content.

## After Editing

- Run relevant checks.
- Update status if the task meaningfully changes project state.

## When Unsure

- Prefer a small reversible step.

## Commit / PR Behavior

- Commit only intentional changes.

## Expected Response Format

- Summarize what changed, what was checked, and what remains.
""",
        ),
        (
            "metrics.md",
            """# Metrics

## Definition of Done

- The requested change is implemented.
- Relevant checks pass or limitations are clearly stated.

## Required Checks

- Not specified yet.

## Test Requirements

- Not specified yet.

## Documentation Requirements

- Update docs when behavior or workflow changes.

## Quality Bar

- Work should be understandable, scoped, and reproducible.

## Submission Checklist

- Important files checked.
- Tests or checks run.
- Status updated if needed.
""",
        ),
        (
            "toolbox.md",
            """# Toolbox

## Package Manager

Not specified yet.

## Build Commands

Not specified yet.

## Test Commands

Not specified yet.

## Lint Commands

Not specified yet.

## Format Commands

Not specified yet.

## Useful Scripts

Not specified yet.

## External Tools

Not specified yet.
""",
        ),
        (
            "important_files.md",
            """# Important Files

## Core Source Files

Not specified yet.

## Configuration Files

Not specified yet.

## Documentation Files

Not specified yet.

## Do-Not-Touch Files

Not specified yet.

## Generated Files

Not specified yet.

## Temporary Files

Not specified yet.
""",
        ),
        (
            "status.md",
            """# Status

## Current Task

Not specified yet.

## Last Completed Task

Not specified yet.

## Known Issues

- Not specified yet.

## Current Blockers

- Not specified yet.

## Next Step

Not specified yet.

## Recent Decisions

- Not specified yet.
""",
        ),
        (
            "agent_notes.md",
            """# Agent Notes

## Project-Specific Agent Instructions

Not specified yet.

## Common Mistakes

- Not specified yet.

## Preferred Working Style

Not specified yet.

## Context Hints

Not specified yet.

## Handoff Notes

Not specified yet.
""",
        ),
    ]
)


REQUIRED_STRUCTURE_FILES = list(STRUCTURE_TEMPLATES.keys())
