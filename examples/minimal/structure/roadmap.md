# Roadmap

## Version 0.1

Create the basic structure files and validation/export commands.

## Version 0.2

Add scriptable agent integration:

- RAG index generation
- compact context-pack export
- MCP manifest checks
- skill scaffold helpers
- agent-readiness audit

## Version 0.3

Add workflow runner commands for agent briefs, structured task execution,
session start/end, config defaults, and MCP scaffolding.

## Long-Term Direction

Make project structure readable and reusable by coding agents, research agents,
MCP servers, and local skills.

## Version 0.5

Add local agent network records for issues, branches, PRs, reviews, project
boards, and network sync.

## Version 0.6

Add Context Git integration for workflow snapshots, semantic branches, tags,
exports, and network snapshot links.

## Version 0.7

Add local GitHub-like issue, PR, comment, timeline, milestone, and export
lifecycle commands.

## Version 0.8

Add a dry-run GitHub bridge for labels, issues, milestones, remote metadata, and
sync-plan export without remote API writes.

## Version 0.9

Add explicit `gh issue create` support for single and batch issue creation, with
remote metadata write-back and duplicate protection.

## Version 1.0

Add Agent GitHub Worknet closure: repo config, doctor checks, label and
milestone creation, remote state pullback, worknet status, and sync reports.

## Version 1.1

Add agent workflow commands for repo auto-detection, GitHub comments,
task/issue binding, work sessions, verification-aware endings, and status
summaries.

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

## Version 1.5.0

Add production integration hardening:

- standard MCP JSON-RPC server with stdio and HTTP modes
- symlink-aware sandbox checks
- argv-level command classification and shell-control denial
- secret scanning and environment sanitization helpers
- capability token expiry and revocation
- CI, lint, type-check, coverage, build, and release checklist

## Version 1.5.2

Harden GNW publication governance after real trial feedback:

- role reports for non-executive artifacts
- gate checks for commit, remote push, and GitHub PR publication
- protocol split between local GitHub Worknet and remote GitHub publication
- real incident trace for future workflow audits

## Version 1.5.3

Add the Agent Runtime Hub layer:

- runner adapters for Codex, Pi, mini-swe-agent, OpenHands, Sandbox Agent, and local subprocesses
- subagent spawn specs with prompt/context packets
- dry-run and explicit execution records for worker agents
- ingest records that turn worker output into role reports

## Deferred Ideas

- Optional presets, only if they support the integration tools.
