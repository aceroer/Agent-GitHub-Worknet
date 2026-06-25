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

The 1.3 model API loop adds a real provider boundary:

```text
provider config -> doctor -> request packet -> dry-run -> approval token -> live model call
```

The 1.4 runtime loop is stream-structured rather than tree-structured:

```text
issue -> stream -> CEO plan -> assignment -> stream events -> human takeover when needed
```

The 1.4.4 protocol layer fixes the operating contracts:

```text
object protocol -> authority protocol -> workflow protocol -> roundtable protocol -> handoff protocol
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

New projects include `structure/protocols.md`, the fixed contract file for
object IDs, authority, workflow, roundtable decisions, GitHub sync, metrics, and
handoffs.

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

Prepare a real model API provider:

```bash
structure-rule model-config
structure-rule model-provider-set --provider openai --model "$MODEL_NAME"
structure-rule model-doctor
structure-rule model-request --prompt "Plan the next step." --subagent subagent-0001
structure-rule model-call model-request-0001
```

Start a stream runtime with corporate P-level roles:

```bash
structure-rule runtime-init
structure-rule role-show --level P12
structure-rule agent-promote subagent-0001 --level P12
structure-rule stream-start --issue issue-0001 --ceo-agent subagent-0001
structure-rule ceo-plan --issue issue-0001 --stream stream-0001 --ceo-agent subagent-0001
structure-rule human-takeover stream-0001 --reason "Manual review"
```

Appoint executive agents under the CEO:

```bash
structure-rule executive-board
structure-rule executive-appoint --office CTO --subagent subagent-0002 --by subagent-0001
structure-rule executive-delegate --office CTO --stream stream-0001 --duty "Own the implementation route"
structure-rule executive-report --office CFO --stream stream-0001 --summary "Token budget is stable."
```

Record agent-native KPI/OKR signals:

```bash
structure-rule metrics-init
structure-rule metric-record --agent subagent-0001 --metric Reliability --score 5 --stream stream-0001
structure-rule scorecard-build --agent subagent-0001 --stream stream-0001
structure-rule okr-set --agent subagent-0001 --objective "Improve useful exploration" --metric Exploration --target 4
structure-rule okr-review okr-0001
```

Open a roundtable meeting for agents and human board members:

```bash
structure-rule roundtable-init
structure-rule meeting-start --topic "Route review" --stream stream-0001 --organizer subagent-0001
structure-rule meeting-post meeting-0001 --actor subagent-0002 --message "I propose a scoped route."
structure-rule vote-open --meeting meeting-0001 --motion "Adopt scoped route."
structure-rule vote-cast vote-0001 --voter subagent-0001 --choice yes
structure-rule vote-tally vote-0001 --close
structure-rule org-apply --applicant subagent-0002 --kind promotion --target P7 --meeting meeting-0001
structure-rule org-review application-0001 --decision approved --reviewer subagent-0001
structure-rule minutes-generate meeting-0001
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
structure-rule approval-grant approval-0001 --ttl-hours 24
structure-rule token-revoke token-0001 --reason "Scope changed."
```

Security checks are intentionally conservative:

```bash
structure-rule sandbox-check subagent-0001 --target structure/tasks/task.md
structure-rule command-check --subagent subagent-0001 --cmd "pytest; rm -rf build"
structure-rule secret-scan --target structure/tasks/draft.env
```

Sandbox checks resolve symlinks before deciding whether a path is allowed.
Command checks classify shell control operators as dangerous. Capability tokens
carry expiry timestamps and can be revoked.

This layer does not call a model API yet. It exists so later model agents have a
clear permission boundary before they can plan, draft, verify, or apply work.

## 1.3 Model API Commands

The 1.3 layer prepares real model API use while preserving the governance
boundary from 1.2. It stores provider config, request packets, response records,
and API audit events under:

```text
structure/worknet/model_api/
├── providers.json
├── model_api_log.jsonl
├── requests/
└── responses/
```

`model-config` initializes provider config:

```bash
structure-rule model-config
structure-rule model-config --json
```

`model-provider-set` records endpoint, API-key environment variable, provider
type, and model name:

```bash
structure-rule model-provider-set \
  --provider openai \
  --api-key-env OPENAI_API_KEY \
  --model "$MODEL_NAME"
```

`model-doctor` checks whether the provider is ready for a live call:

```bash
structure-rule model-doctor
structure-rule model-doctor --json
```

`model-request` builds a request packet from a prompt, issue, and subagent:

```bash
structure-rule model-request \
  --issue issue-0001 \
  --subagent subagent-0001 \
  --prompt "Draft a task split."
```

`model-call` defaults to dry-run:

```bash
structure-rule model-call model-request-0001
```

A live call requires both `--apply` and a matching capability token:

```bash
structure-rule approval-request subagent-0001 --action model-call --target openai
structure-rule approval-grant approval-0001
structure-rule model-capability-check --subagent subagent-0001 --provider openai
structure-rule model-call model-request-0001 --apply
```

This version supports OpenAI-compatible chat-completions style providers through
standard HTTPS calls and keeps the default model unset until the project owner
chooses one.

## 1.4 Stream Runtime Commands

The 1.4 layer adds a backend runtime without adding a dashboard. Its philosophy
is stream-based, not tree-based: work advances through append-only event flows
that can be frozen, resumed, assigned, and taken over.

It stores runtime state under:

```text
structure/worknet/runtime/
├── streams/
│   └── stream-0001.jsonl
├── roles/
│   └── corporate_levels.json
├── assignments/
│   └── assignment-0001.json
├── ceo_plans/
│   └── ceo-plan-0001-stream-0001.json
├── current_stream.json
└── runtime_log.jsonl
```

`runtime-init` creates the stream runtime and P1-P13 corporate role model:

```bash
structure-rule runtime-init
structure-rule role-show
structure-rule role-show --level P12
```

The default supervision model has two layers:

- `P12` CEO Agent: global orchestration, delegation, stream routing, escalation
- `P13` Human Supervisor: final owner, approval, revocation, takeover

`agent-promote` assigns a corporate level to a governed subagent:

```bash
structure-rule agent-promote subagent-0001 --level P6
structure-rule agent-promote subagent-0002 --level P12
```

`level-check` verifies whether a level has a capability:

```bash
structure-rule level-check --level P6 --capability verify_commands
structure-rule level-check --level P2 --capability verify_commands
```

`stream-start` opens an append-only runtime stream:

```bash
structure-rule stream-start --issue issue-0001 --ceo-agent subagent-0002
```

`stream-event` appends observations, tool results, approvals, or other runtime
events:

```bash
structure-rule stream-event stream-0001 --type observation --message "Loaded context."
```

`assignment-create` binds a subagent to a stream or issue:

```bash
structure-rule assignment-create \
  --subagent subagent-0001 \
  --stream stream-0001 \
  --duty "Verify the implementation route."
```

`ceo-plan` creates the P12 global coordination plan while preserving P13 gates:

```bash
structure-rule ceo-plan --issue issue-0001 --stream stream-0001 --ceo-agent subagent-0002
```

`human-takeover` lets the P13 supervisor pause or redirect the stream:

```bash
structure-rule human-takeover stream-0001 --reason "Manual review before remote write."
```

This is the backend runtime layer that sits above Git, Context Git, worknet
objects, governance, and model API packets.

### 1.4.1 Executive Layer

The 1.4.1 patch adds an executive board below the CEO agent. The CEO can appoint
specialized executive offices while P13 remains the final supervisor.

Default offices:

- `COO`: operations, stream progress, issue/project flow, delivery cadence
- `CTO`: architecture, implementation routes, verification, technical risk
- `CFO`: token budget, model/API cost, resource usage, budget reporting
- `CSO`: governance, sandbox, secrets, permission risk
- `CRO`: research routes, evidence quality, knowledge capture

Executive state is stored under:

```text
structure/worknet/runtime/executives/
├── executive_board.json
├── appointments/
│   └── appointment-0001-cto.json
└── reports/
    └── cfo-report-0001.json
```

Useful commands:

```bash
structure-rule executive-board
structure-rule executive-board --office CTO
structure-rule executive-appoint --office CTO --subagent subagent-0002 --by subagent-0001
structure-rule executive-delegate --office CTO --stream stream-0001 --duty "Own implementation route."
structure-rule executive-report --office CFO --stream stream-0001 --summary "Budget stable."
```

`executive-appoint` requires a `P12` CEO agent or a `P13` human supervisor.
Executives can own delegated stream duties, but they do not override P13 gates.

### 1.4.2 Agent Metrics And OKR Layer

The 1.4.2 patch adds an agent-native KPI/OKR layer. It does not copy generic
business KPI. It measures behavior that matters for coding and research agents:

- `Reliability`: proportion and quality of outputs that are accepted or adopted
- `Delegation`: ability to split work into suitable agents, offices, or P-levels
- `Coordination`: net benefit after collaboration with other agents
- `Correction`: speed and quality of fixing mistakes after feedback
- `Exploration`: useful new routes, hypotheses, or implementation options

Metric state is stored under:

```text
structure/worknet/runtime/metrics/
├── agent_metrics.json
├── events/
│   └── metric-event-0001-reliability.json
├── scorecards/
│   └── scorecard-0001.json
├── okrs/
│   └── okr-0001.json
└── metrics_log.jsonl
```

Useful commands:

```bash
structure-rule metrics-init
structure-rule metric-show
structure-rule metric-show --metric Reliability
structure-rule metric-record \
  --agent subagent-0001 \
  --metric Reliability \
  --score 5 \
  --stream stream-0001 \
  --evidence "Output accepted with minor edits."
structure-rule scorecard-build --agent subagent-0001 --stream stream-0001
structure-rule okr-set \
  --agent subagent-0001 \
  --objective "Improve useful exploration." \
  --metric Exploration \
  --target 4
structure-rule okr-review okr-0001
structure-rule metrics-status
```

Scores use a 0-5 scale and are evidence-backed. OKRs target the agent behavior
metrics directly rather than external business numbers.

### 1.4.3 Roundtable Layer

The 1.4.3 patch adds a roundtable meeting mechanism for agents and human board
members. It is still backend-first: every meeting is an append-only terminal,
not a dashboard.

It provides three special mechanisms:

- meeting minutes generation
- weighted voting
- organization application and review

Roundtable state is stored under:

```text
structure/worknet/runtime/roundtable/
├── roundtable_rules.json
├── meetings/
│   └── meeting-0001.jsonl
├── minutes/
│   └── minutes-0001-meeting-0001.json
├── votes/
│   └── vote-0001.json
├── applications/
│   └── application-0001.json
└── roundtable_log.jsonl
```

Meeting terminal commands:

```bash
structure-rule roundtable-init
structure-rule meeting-start --topic "Architecture review" --stream stream-0001
structure-rule meeting-post meeting-0001 --actor subagent-0001 --role CTO --message "Use the scoped route."
structure-rule meeting-show meeting-0001
structure-rule minutes-generate meeting-0001
```

Weighted voting commands:

```bash
structure-rule vote-open --meeting meeting-0001 --motion "Adopt scoped route."
structure-rule vote-cast vote-0001 --voter subagent-0001 --choice yes
structure-rule vote-cast vote-0001 --voter subagent-0002 --choice no --weight 3
structure-rule vote-tally vote-0001 --close
```

When no explicit weight is supplied, voting uses actor authority:

- `P13` / human: 13
- `P12` CEO: 12
- lower P-level agents: their P number

Organization application commands:

```bash
structure-rule org-apply \
  --applicant subagent-0002 \
  --kind promotion \
  --target P7 \
  --justification "Needs scoped source edit responsibility." \
  --meeting meeting-0001
structure-rule org-review application-0001 --decision approved --reviewer subagent-0001
structure-rule roundtable-status
```

`org-review` requires a P12 CEO agent or P13 human supervisor.

### 1.4.4 Protocol Stabilization Layer

The 1.4.4 patch fixes the protocols that were implicit across earlier versions.
The main project-level contract now lives in:

```text
structure/protocols.md
```

The protocol file covers:

- object protocol for issues, tasks, branches, PRs, streams, meetings, votes,
  applications, and metrics
- authority protocol for human owners, P13 supervisors, P12 CEO agents,
  executive offices, and lower P-level agents
- workflow protocol from intake to route, delegation, execution, verification,
  review, and closure
- task scale routing: small tasks stay single-threaded, medium tasks use
  GitHub worknet traceability, and large tasks justify CEO/company structure
- risk-aware routing: high-risk small tasks can add specialist gates without
  creating a full company
- worknet concurrency protocol: numbered object writes are serialized until
  atomic ID allocation or file locking is available
- roundtable protocol for minutes, weighted votes, and organization review
- model API protocol for dry-runs, request packets, capability tokens, and
  response records
- GitHub protocol for local-first records, explicit `--apply`, remote pullback,
  and sync reports
- metrics protocol for evidence-backed agent behavior signals
- handoff protocol for resumable agent continuity

`STRUCTURE_RULE.md` now lists `structure/protocols.md` as a required read before
metrics and toolbox files. `action_protocol.md` also requires protocol updates
when a workflow, authority rule, or data contract changes.

### 1.5.0 MCP, Security, And CI Layer

The 1.5.0 release turns the MCP endpoint into a real JSON-RPC MCP server and
hardens the governance boundary.

MCP stdio mode:

```bash
structure-rule-mcp-server --path . --stdio
```

MCP HTTP mode:

```bash
structure-rule-mcp-server --path . --http --host 127.0.0.1 --port 8765
```

The server supports:

- `initialize`
- `resources/list`
- `resources/read`
- `tools/list`
- `tools/call`

The CLI keeps the old single-request mode for smoke tests:

```bash
structure-rule mcp-server --request '{"jsonrpc":"2.0","id":1,"method":"resources/list"}'
```

Security additions:

- symlink-aware sandbox checks
- argv-level command classification with shell control operators denied
- capability token expiry
- capability token revocation
- one-file secret scanning for common secret patterns
- environment sanitization helpers for secret-like variable names

Packaging additions:

- `structure-rule-mcp-server` console script
- Ruff, mypy, coverage, and build dev dependencies
- GitHub Actions CI for lint, type check, tests, coverage report, and package build
- `RELEASE_CHECKLIST.md`

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
- symlink escapes are denied by sandbox checks
- shell control operators are classified as dangerous commands
- capability tokens expire and can be revoked
- secret scans can be run before adopting generated files
- live model API calls require `model-call --apply` and a matching token
- stream runtime authority is expressed through P1-P13 corporate levels
- P12 CEO agents still cannot override P13 human gates
- executive appointments require a P12 CEO agent or P13 human supervisor
- agent metrics are evidence-backed stream records, not hidden model judgments
- roundtable organization reviews require a P12 CEO agent or P13 human supervisor
- weighted votes use explicit weights or actor P-level authority
- project protocols are fixed in `structure/protocols.md` and must be updated
  when workflow, authority, or data contracts change

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
structure-rule-mcp-server --stdio
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
1.5.1
```

The 1.5.1 release fixes role rules into `structure/protocols.md`: P1-P13
responsibilities, boundaries, executive office duties, and required outputs.

## Philosophy

Do not only give an agent context. Give it a work network.

Context tells the agent what has happened.

Structure tells it how to continue.

Agent GitHub Worknet connects that structure to GitHub without giving up local
control.
