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

## Deferred Ideas

- Optional presets, only if they support the integration tools.
