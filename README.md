# Agent GitHub Worknet

A local-first GitHub work network for AI agents.

Agent GitHub Worknet lets coding and research agents create, track, sync, and
reconcile GitHub-like work objects without losing local project structure.

It is built on the `structure-rule-kit` package and the `structure-rule` CLI.
The package name remains stable for installation and compatibility; the project
identity is Agent GitHub Worknet.

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

The 1.1 workflow loop is:

```text
GitHub repo -> local issue -> agent task -> work session -> verification -> GitHub comment -> sync report
```

The 1.2 governance loop adds a safe shell around future model agents:

```text
issue -> subagent plan -> governed subagent -> sandbox check -> command check -> approval -> capability token
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
structure-rule github-config --auto
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

Start and finish an agent work session:

```bash
structure-rule task-from-issue issue-0001
structure-rule work-start issue-0001
structure-rule work-end --done "Implemented parser" --cmd "python3 -m pytest" --run
structure-rule worknet-status
```

Initialize the governance layer before introducing model-backed subagents:

```bash
structure-rule governance-init
structure-rule subagent-plan issue-0001
structure-rule subagent-create --permission draft --issue issue-0001
structure-rule sandbox-check subagent-0001 --target structure/tasks/task.md
structure-rule command-check --subagent subagent-0001 --cmd "rg TODO"
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

## 1.1 Agent Workflow Commands

`github-config --auto` detects the GitHub repo from `git remote get-url origin`:

```bash
structure-rule github-config --auto
```

`task-from-issue` turns a local issue into an executable agent task:

```bash
structure-rule task-from-issue issue-0001
```

`issue-from-task` turns an agent task back into a local issue:

```bash
structure-rule issue-from-task structure/tasks/20260625-add-parser.md
```

`work-start` opens a local work session:

```bash
structure-rule work-start issue-0001
```

It writes `structure/worknet/current.json` and updates `structure/status.md`.

`work-end` closes the session, records optional verification, refreshes the sync
report, and can prepare or apply a GitHub comment:

```bash
structure-rule work-end \
  --done "Implemented parser" \
  --next "Review changes" \
  --cmd "python3 -m pytest" \
  --run

structure-rule work-end \
  --done "Implemented parser" \
  --github-comment "Implemented parser and tests pass." \
  --apply-comment
```

`github-comment` comments on a linked GitHub issue:

```bash
structure-rule github-comment issue-0001 --body "Tests pass."
structure-rule github-comment issue-0001 --body "Tests pass." --apply
```

`worknet-status` gives an agent-friendly status summary:

```bash
structure-rule worknet-status
structure-rule worknet-status --json
```

## 1.2 Governance Commands

The 1.2 layer prepares Agent GitHub Worknet for model-backed subagents without
turning on autonomous execution. It records policy, sandboxes, approval
requests, capability tokens, and audit events under:

```text
structure/worknet/governance/
├── policy.json
├── audit_log.jsonl
├── approvals/
├── sandboxes/
└── capability_tokens/
```

`governance-init` creates the governance files:

```bash
structure-rule governance-init
structure-rule policy-show
structure-rule policy-show --json
```

The default permission levels are intentionally conservative:

- `plan`: read context and generate plans only
- `draft`: write local worknet, task, and draft artifacts
- `apply`: apply broader project changes only after explicit approval

`subagent-plan` creates a deterministic role plan for a local issue:

```bash
structure-rule subagent-plan issue-0001
```

`subagent-create` creates a governed subagent record and a matching sandbox:

```bash
structure-rule subagent-create --permission plan --issue issue-0001
structure-rule subagent-create --permission draft --issue issue-0001
structure-rule subagent-create --permission apply --issue issue-0001
```

`sandbox-check` tests whether a subagent may write a path:

```bash
structure-rule sandbox-check subagent-0001 --target structure/tasks/task.md
structure-rule sandbox-check subagent-0001 --target src/model.py
```

`command-check` classifies commands as `read`, `verify`, `write`, `danger`, or
`unknown`, then checks the subagent permission:

```bash
structure-rule command-check --subagent subagent-0001 --cmd "rg TODO"
structure-rule command-check --permission apply --cmd "python3 -m pytest"
```

`approval-request` and `approval-grant` create the human approval trail:

```bash
structure-rule approval-request subagent-0001 --action apply-patch --target src/model.py
structure-rule approval-grant approval-0001
```

This layer does not call a model API yet. It exists so later model agents have a
clear permission boundary before they can plan, draft, verify, or apply work.

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

Model-agent actions also pass through governance checks:

- path writes go through `sandbox-check`
- shell commands go through `command-check`
- apply-level work requires an approval record and capability token
- dangerous commands are denied by default

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
1.2.0
```

The 1.2 release adds the governance and sandbox foundation for future
model-backed subagents: policy files, subagent records, path sandboxes, command
classification, approvals, capability tokens, audit logs, and CLI checks.

## Philosophy

Do not only give an agent context. Give it a work network.

Context tells the agent what has happened.

Structure tells it how to continue.

Agent GitHub Worknet connects that structure to GitHub without giving up local
control.
