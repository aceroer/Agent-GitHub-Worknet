# Structure Rule Kit

Structure Rule Kit is a lightweight project-structure layer for AI coding agents.

It creates a standard `STRUCTURE_RULE.md` and `structure/` directory so agents can understand the project plan, roadmap, rules, tools, important files, and completion metrics before editing code.

## Why

AI agents often fail not because they cannot code, but because they lack project structure.

They do not know:

- what the current plan is
- where important files are
- what should not be changed
- what commands to run
- what counts as done

Structure Rule Kit solves this by making project-operating knowledge explicit.

## Install

```bash
pip install structure-rule-kit
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
structure-rule init
structure-rule validate
structure-rule summary
structure-rule export
```

Agent integration tools:

```bash
structure-rule rag-index
structure-rule context-pack
structure-rule mcp-manifest
structure-rule skill-scaffold
structure-rule agent-ready
structure-rule handoff-pack --task "implement parser"
structure-rule status-update --done "added parser" --next "run tests"
structure-rule toolbox-audit
structure-rule agent-task --title "add parser" --goal "..."
structure-rule verify-log --cmd "python3 -m py_compile ..." --result pass
structure-rule verify-log --cmd "python3 -m py_compile structure_rule_kit/*.py" --run
structure-rule decision-log --decision "0.2 focuses on scriptable tools"
structure-rule context-prune --budget 8000
structure-rule repo-map
```

These commands do not prescribe how a project must be organized beyond the
Structure Rule layer. They expose the structure in reusable forms so different
agent systems can choose how to consume it.

## Roadmap

Version 0.1 creates and validates the structure layer.

Version 0.2 will focus on scriptable agent integration:

- RAG index and compact context-pack generation
- MCP-facing manifest generation and checks
- Skill scaffold and audit helpers
- agent-readiness checks for existing repositories
- handoff packets, status updates, and toolbox audits
- structured task files, verification logs, decision logs, priority-pruned context, and repository maps

The goal is not to create many project templates. The goal is to make existing
project structure easier for coding agents, research agents, MCP servers, and
local skills to read and reuse.

## Agent Toolbox

`rag-index` writes `structure/rag_index.json`, a simple JSON index over the
structure files.

`context-pack` writes a bounded context pack that can be attached to a coding or
research agent task.

`mcp-manifest` writes `structure/mcp_manifest.json`, a small manifest describing
the structure resources and suggested tools an MCP server can expose.

`skill-scaffold` creates a local `SKILL.md` entry point that tells an agent how
to load this repository's structure before working.

`agent-ready` checks whether the repository has enough project intent, rules,
important files, metrics, status, and command information for an agent to start
without guessing. It reports one of three states: `ready`, `warning`, or
`blocked`.

`handoff-pack` writes `STRUCTURE_HANDOFF.md`, a task packet for another agent,
thread, or future session.

`status-update` updates `structure/status.md` from the command line and appends
an activity log entry.

`toolbox-audit` checks whether `structure/toolbox.md` records the practical
commands an agent needs for build, test, and useful scripts.

`agent-task` creates a structured task file under `structure/tasks/` so a larger
agent task can keep its own goal, scope, forbidden actions, checks, result, and
notes.

`verify-log` appends command verification evidence to
`structure/verification_log.md`. With `--run`, it executes the command, records
the exit code, and stores bounded stdout/stderr evidence.

`decision-log` appends durable project decisions to `structure/decision_log.md`
so future agents do not reopen settled direction.

`context-prune` creates a priority-pruned context pack under a character budget.
Rules, status, project plan, metrics, important files, and toolbox information
are kept before lower-priority notes.

`repo-map` scans the repository and writes `structure/repo_map.md` with source,
test, documentation, configuration, generated, and other files.

## Example Workflow

```bash
structure-rule init
structure-rule repo-map
structure-rule agent-ready
structure-rule agent-task --title "add parser" --goal "create parser utility"
structure-rule context-prune --budget 8000
structure-rule verify-log --cmd "python3 -m py_compile structure_rule_kit/*.py tests/*.py" --run
structure-rule status-update --done "added parser" --next "review tests"
structure-rule handoff-pack --task "review parser implementation"
```

This keeps the project structure, task state, verification evidence, and handoff
context in files that future agent runs can reuse.

## Generated Files

```text
STRUCTURE_RULE.md
structure/
├── project_plan.md
├── roadmap.md
├── rules.md
├── action_protocol.md
├── metrics.md
├── toolbox.md
├── important_files.md
├── status.md
└── agent_notes.md
```

## For Codex / Claude / Cursor

Tell the agent:

> Before editing, read `STRUCTURE_RULE.md`.

## Philosophy

Do not only give the model context. Give it structure.

Context tells the model what has happened.

Structure tells the model how to continue.
