# Agent GitHub Worknet

A local-first GitHub work network for AI agents.

Agent GitHub Worknet lets coding and research agents create, track, sync, and
reconcile GitHub-like work objects without losing local project structure.

It is built on the `structure-rule-kit` package and the `structure-rule` CLI.
The package name remains stable for installation and compatibility; the 1.0
project identity is Agent GitHub Worknet.

## What It Does

Agent work usually falls apart at the boundary between local context and remote
collaboration state.

Agents can edit files, but they also need to know:

- what issue is being solved
- which branch or route is active
- what review or milestone the work belongs to
- whether a GitHub issue already exists
- what the remote issue state is now
- what should be synced, skipped, or reported

Agent GitHub Worknet gives agents a local work network under `structure/network/`
and connects it to GitHub through the GitHub CLI.

The 1.0 closure loop is:

```text
local issue -> GitHub issue -> remote state -> local status -> sync report
```

## Install

```bash
pip install structure-rule-kit
```

For local development:

```bash
pip install -e ".[dev]"
```

Requirements for GitHub sync:

- GitHub CLI: `gh`
- authenticated `gh auth login`
- a repository with issue access

## Quick Start

Create a structured project:

```bash
structure-rule init
structure-rule validate
```

Create local work objects:

```bash
structure-rule network-init
structure-rule issue-create --title "Add parser" --label enhancement
structure-rule branch-create --name parser --issue issue-0001
structure-rule pr-create --title "Implement parser" --issue issue-0001 --branch parser
structure-rule project-board
```

Configure GitHub:

```bash
structure-rule github-config --repo owner/name
structure-rule github-doctor
```

Prepare remote objects:

```bash
structure-rule github-labels-create --apply
structure-rule github-milestones-create --apply
```

Create GitHub issues from local issues:

```bash
structure-rule github-issue-create issue-0001
structure-rule github-issue-create issue-0001 --apply
structure-rule github-issues-create --apply
```

Pull remote state and write a closure report:

```bash
structure-rule github-pull
structure-rule github-sync-report
```

Run the full issue sync path:

```bash
structure-rule github-sync --apply
```

The sync report is written to:

```text
structure/network/github_export/sync_report.md
```

## 1.0 Closure Commands

`github-config` writes the default GitHub repository config:

```bash
structure-rule github-config --repo owner/name
```

`github-doctor` checks the real environment:

```bash
structure-rule github-doctor
structure-rule github-doctor --json
```

It checks:

- `gh` is installed
- `gh auth status` works
- the repository is readable
- issues are accessible
- labels are readable
- milestones are readable

`github-labels-create` creates missing labels explicitly:

```bash
structure-rule github-labels-create
structure-rule github-labels-create --apply
```

`github-milestones-create` creates missing milestones explicitly:

```bash
structure-rule github-milestones-create
structure-rule github-milestones-create --apply
```

`github-pull` pulls linked GitHub issue state back into local records:

```bash
structure-rule github-pull
```

Local issue records may then contain:

```json
{
  "worknet_status": "synced",
  "remote_state": {
    "number": 1,
    "state": "OPEN",
    "title": "Add parser",
    "url": "https://github.com/owner/name/issues/1"
  }
}
```

`github-sync-report` writes a local closure report:

```bash
structure-rule github-sync-report
```

Report statuses include:

- `synced`
- `remote-changed`
- `missing-remote`
- `local-only`

## Local Network Model

Agent GitHub Worknet stores local collaboration objects under:

```text
structure/network/
├── issues/
├── branches/
├── prs/
├── reviews/
├── comments/
├── milestones/
├── projects/
├── github_export/
├── github_config.json
└── network_log.jsonl
```

Git still tracks files. GitHub tracks public collaboration. Agent GitHub Worknet
tracks the agent work structure between them.

## Safety Model

Remote writes require `--apply`.

Without `--apply`, commands stay in dry-run or reporting mode. This makes the
tool safe for agents to inspect and plan before touching GitHub.

Duplicate protection is built in:

- if a local issue already has `remote.url` or `remote.number`, issue creation
  skips it
- missing labels block issue creation unless `--skip-missing-labels` is used
- sync reports expose local-only, missing-remote, and changed records instead
  of hiding them

## Agent Structure Tools

The package still includes the broader Structure Rule toolchain:

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
structure-rule verify-log --cmd "python3 -m py_compile structure_rule_kit/*.py" --run
structure-rule decision-log --decision "use GitHub Worknet for issue sync"
structure-rule context-prune --budget 8000
structure-rule repo-map
structure-rule agent-brief --task "implement parser"
structure-rule session-start --task "implement parser"
structure-rule session-end --done "added parser" --next "review tests"
structure-rule agent-export --target codex
structure-rule skill-export --name project-structure
structure-rule agent-sync --target codex
structure-rule mcp-server
```

These commands make project structure readable and reusable by coding agents,
research agents, MCP servers, and local skills.

## Experimental Closure Layer

The public experiment folder remains available at:

```text
experimental/closure/
```

It keeps real traces, doctor prototypes, sync-report experiments, and notes from
the path toward the 1.0 closure release.

## Version

Current stable version:

```text
1.0.0
```

The first real closure smoke test created GitHub issue `#2`, pulled it back into
local state as `synced`, generated an Agent GitHub Worknet sync report, and then
closed the temporary issue.

## Philosophy

Do not only give an agent context. Give it a work network.

Context tells the agent what has happened.

Structure tells it how to continue.

Agent GitHub Worknet connects that structure to GitHub without giving up local
control.
