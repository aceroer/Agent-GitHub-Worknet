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
structure-rule config
structure-rule agent-brief --task "implement parser"
structure-rule run-task structure/tasks/20260616-add-parser.md --cmd "python3 -m pytest"
structure-rule session-start --task "implement parser"
structure-rule session-end --done "added parser" --next "review tests"
structure-rule mcp-scaffold
structure-rule agent-export --target codex
structure-rule agent-export --target all
structure-rule skill-export --name project-structure
structure-rule agent-sync --target codex
structure-rule mcp-server
structure-rule network-init
structure-rule issue-create --title "add parser"
structure-rule branch-create --name parser --issue issue-0001
structure-rule pr-create --title "implement parser" --issue issue-0001 --branch parser
structure-rule review-create --pr pr-0001 --decision approve
structure-rule project-board
structure-rule network-sync --target codex
structure-rule context-init
structure-rule context-snapshot --message "finished parser"
structure-rule context-log
structure-rule context-latest
structure-rule context-branch experiment
structure-rule context-checkout experiment
structure-rule context-tag v0.6-plan --snapshot 0001
structure-rule context-export
structure-rule context-route
structure-rule network-snapshot --message "parser ready for review"
structure-rule issue-close issue-0001
structure-rule issue-reopen issue-0001
structure-rule issue-assign issue-0001 --assignee codex
structure-rule issue-label issue-0001 --label enhancement
structure-rule pr-ready pr-0001
structure-rule pr-merge pr-0001
structure-rule comment-add --target issue-0001 --body "needs tests"
structure-rule timeline --target issue-0001
structure-rule milestone-create --title "v0.7"
structure-rule github-export --type issue --id issue-0001
structure-rule github-labels-export
structure-rule github-issues-export
structure-rule github-milestones-export
structure-rule github-dry-run
structure-rule github-sync --dry-run
structure-rule github-issue-create issue-0001 --repo owner/name
structure-rule github-issue-create issue-0001 --repo owner/name --apply
structure-rule github-issues-create --repo owner/name --apply
structure-rule github-config --repo owner/name
structure-rule github-doctor
structure-rule github-labels-create --apply
structure-rule github-milestones-create --apply
structure-rule github-pull
structure-rule github-sync-report
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

Version 0.3 turns the toolbox into a lightweight workflow runner:

- `agent-brief` builds a startup packet from readiness, repo map, pruned context,
  task state, decision log, and verification log
- `run-task` executes a structured task and writes verification evidence back
  into the task result
- `session-start` and `session-end` standardize agent session entry and exit
- `config` writes reusable defaults such as context budget and output paths
- `mcp-scaffold` creates a minimal MCP resource server scaffold

Version 0.4 adapts the workflow runner to external agent ecosystems:

- `agent-export` writes agent entry files such as `AGENTS.md`, `CLAUDE.md`, and
  `.cursor/rules/structure-rule.md`
- `skill-export` writes a richer local skill backed by the current agent brief
- `agent-sync` runs the full sync path for a target agent
- `mcp-server` exposes Structure Rule files through a minimal JSON resource
  endpoint

Version 0.5 adds a local agent network layer, a lightweight GitHub-like workflow
for agent collaboration:

- `issue-create` and `issue-list` manage local agent issues
- `branch-create` records local exploration branches
- `pr-create` records delivery packages and checks
- `review-create` records review decisions
- `project-board` writes a local board summary
- `network-sync` connects the local network to agent exports, skills, brief, and
  MCP manifest output

Version 0.6 adds a Context Git integration layer:

- `context-init` creates `.contextgit/`
- `context-snapshot` versions workflow state as agent-readable snapshots
- `context-log` and `context-latest` recover snapshot history
- `context-branch` and `context-checkout` track semantic workflow branches
- `context-tag` marks stable checkpoints
- `context-export` writes a recovery packet for future agents
- `network-snapshot` links local agent network objects to a context snapshot

Version 0.7 adds local GitHub-like lifecycle semantics:

- issue close/reopen/assign/label
- PR ready/close/merge
- comments and timelines
- milestones
- GitHub-ready markdown export

Version 0.8 adds a dry-run GitHub bridge layer:

- local remote metadata for issues, PRs, and milestones
- label export to `github_export/labels.json`
- batch issue export to `github_export/issues/`
- milestone export to `github_export/milestones.json`
- dry-run sync plan generation
- `github-sync --dry-run` for a complete export pass without remote API calls

Version 0.9 adds real GitHub issue creation through the GitHub CLI:

- `github-issue-create issue-0001 --repo owner/name` builds a safe dry run
- `github-issue-create issue-0001 --repo owner/name --apply` creates one remote issue
- `github-issues-create --repo owner/name --apply` creates all unlinked local issues
- successful creates write `repo`, `number`, `url`, and `synced_at` into local `remote` metadata
- existing remote links are skipped to avoid duplicate issues
- missing remote labels are reported before creation unless `--skip-missing-labels` is used

Version 1.0 closes the first Agent GitHub Worknet loop:

- `github-config` stores the default GitHub repository
- `github-doctor` checks `gh`, auth, repo, issue, label, and milestone access
- `github-labels-create` creates missing labels explicitly
- `github-milestones-create` creates missing milestones explicitly
- `github-pull` pulls linked GitHub issue state back into local records
- `github-sync-report` writes a local closure report
- `github-sync --apply` creates issues, pulls remote state, and writes the report

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

## Workflow Runner

`config` writes `structure/config.json` with reusable defaults for context
budget, repo-map size, and output paths.

`agent-brief` refreshes the repo map and pruned context pack, then writes
`STRUCTURE_AGENT_BRIEF.md`, a startup packet for a coding or research agent.

`run-task` runs a command for a task file under `structure/tasks/`, appends
verification evidence, and updates the task's `Result` section.

`session-start` creates a task, updates status, and writes an agent brief.

`session-end` updates status, optionally records final verification, and writes
a handoff packet.

`mcp-scaffold` writes `structure/mcp_server.py`, a minimal resource scaffold that
can expose Structure Rule files to an MCP layer.

## Agent Ecosystem

`agent-export` writes external agent instruction files:

```bash
structure-rule agent-export --target codex
structure-rule agent-export --target claude
structure-rule agent-export --target cursor
structure-rule agent-export --target all
```

`skill-export` writes a richer `skills/<name>/SKILL.md` using the current
project summary, rules, toolbox commands, metrics, and agent brief.

`agent-sync` runs a complete integration pass:

```text
repo-map -> agent-ready -> context-prune -> agent-brief -> agent-export -> skill-export -> mcp-manifest
```

`mcp-server` provides a minimal JSON resource endpoint:

```bash
structure-rule mcp-server
structure-rule mcp-server --request '{"method":"resources/read","params":{"uri":"structure-rule://STRUCTURE_RULE.md"}}'
```

## Agent Network

The agent network layer stores local collaboration objects under:

```text
structure/network/
├── issues/
├── branches/
├── prs/
├── reviews/
├── projects/
├── comments/
├── milestones/
├── github_export/
└── network_log.jsonl
```

It is a local-first lightweight GitHub layer for agent work. Git still tracks
code. Structure Rule Kit tracks the agent collaboration structure.

```bash
structure-rule network-init
structure-rule issue-create --title "add parser" --label enhancement
structure-rule branch-create --name parser --issue issue-0001
structure-rule pr-create --title "implement parser" --issue issue-0001 --branch parser --check pytest
structure-rule review-create --pr pr-0001 --decision approve
structure-rule project-board
structure-rule network-sync --target codex
```

## Context Git Layer

0.6 adds a local semantic version-control layer for agent workflow state:

```text
.contextgit/
├── HEAD
├── config.json
├── log.jsonl
├── snapshots/
├── branches/
├── tags/
├── roots/
│   ├── rag/
│   ├── mcp/
│   ├── skills/
│   ├── notebooks/
│   └── structure/
├── github/
└── exports/
```

Git tracks file changes. Context Git tracks workflow state.

```bash
structure-rule context-init --project-name "Example"
structure-rule context-snapshot --message "initial workflow state"
structure-rule context-log
structure-rule context-latest
structure-rule context-branch experiment --purpose "try alternate route"
structure-rule context-checkout experiment
structure-rule context-tag v0.6-plan --snapshot 0001
structure-rule context-export --include-roots
```

`network-snapshot` connects the 0.5 network layer to Context Git:

```bash
structure-rule network-snapshot --message "parser issue ready for review"
```

It refreshes the local board and agent brief, creates a context snapshot, and
writes the snapshot id back to local issue, PR, and review records that do not
already have `linked_snapshot`.

## Network Lifecycle

0.7 turns local network records into a lightweight collaboration system:

```bash
structure-rule issue-assign issue-0001 --assignee codex
structure-rule issue-label issue-0001 --label enhancement
structure-rule issue-close issue-0001
structure-rule issue-reopen issue-0001
structure-rule pr-ready pr-0001
structure-rule pr-merge pr-0001
structure-rule comment-add --target issue-0001 --author reviewer --body "needs tests"
structure-rule comment-list --target issue-0001
structure-rule timeline --target issue-0001
structure-rule milestone-create --title "v0.7"
structure-rule milestone-list
structure-rule github-export --type issue --id issue-0001
```

`pr-merge` is semantic: it marks the local PR as merged, closes the linked issue
when present, updates the board, and records the merge in `network_log.jsonl`.

## GitHub Bridge

0.8 prepares the local network for future remote GitHub sync while staying
local-first and dry-run only.

```bash
structure-rule github-labels-export
structure-rule github-issues-export
structure-rule github-milestones-export
structure-rule github-dry-run
structure-rule github-sync --dry-run
structure-rule github-issue-create issue-0001 --repo owner/name
structure-rule github-issue-create issue-0001 --repo owner/name --apply
structure-rule github-issues-create --repo owner/name --apply
```

The bridge writes export files under `structure/network/github_export/` and
adds a `remote` metadata block to local issues, PRs, and milestones:

```json
{
  "provider": "github",
  "repo": null,
  "number": null,
  "url": null,
  "synced_at": null
}
```

`github-sync --dry-run` produces labels, issue markdown, milestone JSON, and a
sync plan. It does not create or modify any remote GitHub resources.

0.9 can create real GitHub issues when `gh` is installed and authenticated:

```bash
structure-rule github-issue-create issue-0001 --repo owner/name
structure-rule github-issue-create issue-0001 --repo owner/name --apply
structure-rule github-issues-create --repo owner/name --apply
structure-rule github-sync --repo owner/name --apply
```

The default mode is still safe: no `--apply`, no remote write. When an issue is
created, Structure Rule Kit stores the GitHub issue URL and number back into the
local issue's `remote` field. If the local issue has labels that do not exist on
the remote repository, creation is blocked with a missing-label report unless
`--skip-missing-labels` is passed.

## Agent GitHub Worknet

1.0 promotes the GitHub bridge into Agent GitHub Worknet: a local-first GitHub
work network for AI agents.

```bash
structure-rule github-config --repo owner/name
structure-rule github-doctor
structure-rule github-labels-create --apply
structure-rule github-milestones-create --apply
structure-rule github-issues-create --apply
structure-rule github-pull
structure-rule github-sync-report
```

The closure loop is:

```text
local issue -> GitHub issue -> remote state -> local status -> sync report
```

Local issue records can now carry `worknet_status` and `remote_state` fields
after pullback. The sync report is written to
`structure/network/github_export/sync_report.md`.

## Experimental Closure Layer

The 1.0 closure experiments live under `experimental/closure/`.

This folder is not part of the stable package API. It keeps real environment
traces, GitHub doctor scripts, sync-report experiments, and the proposed closure
roadmap in a public place before those pieces are promoted into stable commands.

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

0.3 workflow-runner flow:

```bash
structure-rule config
structure-rule session-start --task "add parser" --goal "create parser utility"
structure-rule run-task structure/tasks/20260616-add-parser.md --cmd "python3 -m pytest"
structure-rule session-end --done "added parser" --next "review implementation"
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
