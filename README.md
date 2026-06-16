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
