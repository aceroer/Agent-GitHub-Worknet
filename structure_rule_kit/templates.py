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
6. `structure/protocols.md`
7. `structure/metrics.md`
8. `structure/toolbox.md`
9. `structure/status.md`
10. `structure/agent_notes.md`

## Agent Rule

Do not start editing before understanding:

- the current project goal
- the current roadmap stage
- important files
- forbidden actions
- completion metrics
- active protocols

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
- `structure/protocols.md`
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

## Version 0.9

Add real GitHub issue creation through `gh`:

- single issue creation with explicit `--apply`
- batch issue creation for unlinked local issues
- remote URL and issue number write-back
- duplicate protection for already-linked issues
- missing-label checks before remote creation

## Version 1.0

Close the first Agent GitHub Worknet loop:

- GitHub repo config
- GitHub environment doctor
- explicit label and milestone creation
- remote issue state pullback
- local worknet status classification
- sync report generation

## Version 1.1

Add agent workflow commands:

- GitHub repo auto-detection
- GitHub issue comments
- task-from-issue and issue-from-task binding
- work-start and work-end sessions
- verification-aware work endings
- worknet status summaries

## Version 1.2

Add model-agent governance foundations:

- governance policy initialization
- plan/draft/apply permission levels
- governed subagent records
- path sandbox checks
- command classification checks
- approval requests and capability tokens
- audit log for governance actions

## Version 1.3

Prepare real model API integration:

- provider config and API doctor checks
- model request packet generation
- dry-run model-call path
- capability-token gate for live calls
- response records and model API audit log
- OpenAI-compatible chat-completions transport

## Version 1.4

Add a stream-structured runtime backend:

- P1-P13 corporate role model
- P12 CEO agent orchestration layer
- P13 human supervisor takeover layer
- append-only runtime streams
- subagent assignments to streams and issues
- CEO plans and runtime status summaries

## Version 1.4.1

Add an executive layer under the CEO agent:

- COO/CTO/CFO/CSO/CRO executive offices
- CEO or human supervisor appointments
- executive delegation to streams and issues
- executive reports
- executive board status

## Version 1.4.2

Add agent-native KPI/OKR metrics:

- Reliability: accepted or adopted outputs
- Delegation: useful task decomposition and assignment
- Coordination: net collaborative benefit
- Correction: fast, accurate response to feedback
- Exploration: valuable new routes rather than mechanical repetition
- scorecards, OKRs, metric events, and metrics status

## Version 1.4.3

Add a roundtable meeting layer:

- append-only meeting terminals for agents and human board members
- meeting minutes generation
- weighted voting by explicit weight or actor P-level
- organization applications
- P12/P13 organization review gate

## Version 1.4.4

Stabilize protocols and operating flows:

- fixed object protocol for issues, tasks, streams, meetings, votes, and applications
- fixed authority protocol for governance, P-levels, executives, and human takeover
- fixed workflow protocol from issue intake to verification and publication
- fixed roundtable protocol for meeting minutes, weighted votes, and organization review
- fixed handoff and audit protocol for agent continuity

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
- Update `structure/protocols.md` if a workflow, authority rule, or data contract changes.

## When Unsure

- Prefer a small reversible step.

## Commit / PR Behavior

- Commit only intentional changes.

## Expected Response Format

- Summarize what changed, what was checked, and what remains.
""",
        ),
        (
            "protocols.md",
            """# Protocols

This file fixes the operating contracts for the project.

Protocols are stronger than notes and weaker than source code. They describe how
agents, humans, tools, and records are expected to interact.

## Protocol Hierarchy

When instructions conflict, follow this order:

1. Human instruction.
2. Project safety rules in `structure/rules.md`.
3. Protocols in this file.
4. Current task instructions and local notes.
5. Agent preference or convenience.

## Object Protocol

Work should be represented as explicit objects before it becomes action:

- `issue`: a problem, request, defect, or research question.
- `task`: an executable slice derived from an issue.
- `branch`: a local exploration or implementation route.
- `pr`: a proposed merge or closure package.
- `stream`: an append-only runtime flow.
- `meeting`: a roundtable terminal for deliberation.
- `vote`: a weighted decision attached to a meeting.
- `application`: an organization request such as appointment, promotion, or scope change.
- `metric`: an evidence-backed behavior signal for an agent.

Objects should carry stable IDs. Prefer adding events or linked records over
rewriting history.

## Authority Protocol

Authority is explicit and recorded:

- Human owners are final supervisors.
- P13 represents human supervisor authority.
- P12 represents CEO agent authority.
- Executive offices operate below P12 and do not bypass P13.
- Lower P-level agents can plan, draft, verify, or apply only within their granted scope.
- Remote writes, live model calls, broad file writes, and organization changes require explicit gates.

When authority is unclear, pause the action and record the uncertainty.

## Workflow Protocol

The default work flow is:

1. Intake: identify or create the issue.
2. Route: choose a stream, branch, task, or meeting path.
3. Delegate: assign agents, offices, or human reviewers.
4. Execute: make scoped changes and record meaningful events.
5. Verify: run checks or explain why checks could not run.
6. Review: use comments, roundtable discussion, or PR review when needed.
7. Close: update status, metrics, remote links, and handoff notes.

Do not skip verification unless the limitation is recorded.

## Roundtable Protocol

Use a roundtable when a decision benefits from deliberation:

- Start a meeting with a topic, organizer, and optional stream.
- Post agent and human positions as append-only messages.
- Open a vote for a concrete motion when a decision is needed.
- Tally votes with explicit or P-level weights.
- Generate minutes before closing or handing off the decision.
- Use organization applications for appointments, promotions, scope changes, and new roles.
- Organization reviews require P12 CEO or P13 human authority.

Meeting minutes should summarize positions, decisions, open questions, and next actions.

## Model API Protocol

Model-backed work is gated:

- Build a request packet before a live call.
- Default to dry-run unless `--apply` is supplied.
- Require a matching capability token for live model calls.
- Store responses as records rather than hidden transient output.
- Treat model output as a proposal until reviewed, verified, or adopted.

## GitHub Protocol

GitHub sync is explicit:

- Local objects are the source of agent work structure.
- GitHub issues are remote collaboration records.
- Remote writes require `--apply`.
- Pull remote state before claiming remote closure when practical.
- Preserve remote URLs and issue numbers once linked.
- Write a sync report when local and remote state diverge.

## Metrics Protocol

Agent metrics must be evidence-backed:

- Reliability records accepted or adopted output.
- Delegation records useful task splitting and assignment.
- Coordination records collaborative benefit.
- Correction records response to feedback.
- Exploration records valuable new routes or hypotheses.

Metrics are not hidden judgments. They should point to streams, issues, meetings,
or explicit evidence.

## Handoff Protocol

A useful handoff includes:

- current issue, stream, meeting, or PR
- changed files and object IDs
- checks run and their results
- decisions made and by whom
- remaining risks or next actions

If the next agent cannot resume from the handoff, the handoff is incomplete.
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
