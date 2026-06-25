# Protocols

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


## Role Protocol

P-levels define what an agent is expected to do and what it must not do without a higher gate:

| Level | Role | Primary Work | Boundary |
| --- | --- | --- | --- |
| P1 | Observer Intern | Read local context and report what exists. | No writes, no commands beyond passive reading. |
| P2 | Summarizer | Summarize structure files, issues, streams, meetings, and handoffs. | No planning authority beyond summaries. |
| P3 | Draft Assistant | Create local plans, task drafts, notes, and proposed routes. | Draft only; no source edits. |
| P4 | Sandbox Worker | Edit approved sandbox, worknet, task, and draft files. | No source tree changes outside allowed paths. |
| P5 | Read Command Worker | Run read-only inspection commands and gather evidence. | No verification, write, remote, or model-live actions. |
| P6 | Verification Worker | Run approved verification commands and record results. | No source edits unless separately authorized. |
| P7 | Scoped Implementer | Prepare scoped source edits after approval. | No broad refactors, remote writes, or policy changes. |
| P8 | Worknet Operator | Create and update local issues, PRs, milestones, boards, and worknet records. | Local worknet only unless remote action is approved. |
| P9 | Lead Agent | Coordinate multiple subagents and merge local evidence. | Cannot bypass approval gates or human takeover. |
| P10 | Manager Agent | Approve low-risk local execution inside policy and review agent output. | Cannot grant external or high-risk capability alone. |
| P11 | Remote Action Preparer | Prepare GitHub, publication, or external actions for approval. | Preparation only; remote writes still require explicit gates. |
| P12 | CEO Agent | Global planning, delegation, stream routing, executive appointment, and escalation. | Cannot override P13 human gates. |
| P13 | Human Supervisor | Final ownership, approval, revocation, takeover, and redirection. | Human policy is the top local authority. |

A lower level may assist a higher level only inside its own boundary. Promotion changes must be recorded through organization application, executive appointment, or explicit human action.

## Executive Office Protocol

Executive offices are specialized P-level roles below P13. They describe responsibility, not ownership:

| Office | Default Level | Responsibility | Required Output |
| --- | --- | --- | --- |
| COO | P11 | Operations, stream progress, issue/project flow, delivery cadence. | Delegation records, progress reports, blocker summaries. |
| CTO | P11 | Architecture, implementation route, verification strategy, technical risk. | Technical route, review notes, verification plan. |
| CFO | P10 | Token budget, model/API cost, resource usage, budget reporting. | Cost notes, budget warnings, resource reports. |
| CSO | P11 | Governance, sandbox, secrets, permissions, remote-write risk. | Security review, sandbox decision, secret-risk report. |
| CRO | P10 | Research route, evidence quality, knowledge capture, open questions. | Research memo, evidence map, unresolved question list. |

Executives can be delegated work on streams or issues. They can recommend decisions, but appointments, organization changes, high-risk actions, and remote writes remain gated by P12/P13 rules.

## Employee Artifact Protocol

An employee or office is active only when it produces a timestamped artifact
that affects a later decision. Acceptable artifacts include route notes, review
notes, verification verdicts, security gate verdicts, votes, meeting minutes,
or role reports.

Use `structure-rule role-report` for non-executive roles such as CEO, QA Lead,
Docs Lead, reviewer, or release operator. If a named role has no independent
artifact, mark it as `record-only` and do not claim it as a working contributor.

The CEO should decide from employee artifacts, not replace employee work with
after-the-fact role labels.

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

## Task Scale Routing Protocol

Choose the lightest operating mode that can preserve quality and traceability:

| Task Scale | Recommended Mode | Use When | Avoid |
| --- | --- | --- | --- |
| Small | Single-thread agent session | One narrow edit, one obvious owner, low coordination risk. | CEO/executive boards, roundtables, or heavy worknet ceremony. |
| Medium | GitHub worknet flow | Issue-to-branch-to-PR traceability matters, but the route is still mostly linear. | Full company architecture unless there are real cross-role tradeoffs. |
| Large | Company architecture | Multi-part delivery, unclear route, competing risks, parallel agents, or human board governance are useful. | Treating the CEO layer as a replacement for verification or human gates. |

The company architecture is a coordination instrument, not a default wrapper
around every task. If the organization overhead is larger than the task, keep the
task single-threaded and record only the minimal worknet evidence needed.

Task size is not the only routing input. Risk can selectively raise the
governance mode without requiring a full company:

- Small task with high permission, secret, legal, or remote-publication risk: add
  the relevant specialist gate, usually CSO or P13, while keeping execution
  single-threaded.
- Medium task with low risk: keep the worknet flow lean and avoid executive
  ceremony.
- Large task with multi-party decisions: use CEO/company architecture and
  record executive reports.
- Any task with remote writes, live model calls, broad file writes, or
  publication: require explicit approval and keep the gate visible in the
  worknet.

## Worknet Concurrency Protocol

Until the runtime provides atomic ID allocation or file locking, worknet object
writes must be serialized. Do not run concurrent commands that create or update
issues, assignments, executive reports, stream events, meetings, votes, PR
records, or other numbered worknet objects.

Read-only inspection may be parallel. Writes that allocate IDs or append runtime
events should be sequenced, then checked with JSON validation or the relevant
status command before further delegation.

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

## Agent Runtime Hub Protocol

GNW is the work hub, governance hub, and trace hub. External coding agents are
runner backends.

Supported runner adapters can include Codex, Pi, mini-swe-agent, OpenHands,
Sandbox Agent, and local subprocess runners. GNW should not depend on one
worker runtime when a spawn spec, prompt packet, event stream, and ingest record
can express the common workflow.

Use the hub flow:

```text
subagent-spawn -> subagent-run -> subagent-ingest -> role-report
```

`subagent-spawn` creates the bounded task packet and prompt. `subagent-run`
records a dry-run or explicit execution attempt. `subagent-ingest` turns worker
output into a role artifact. A CEO decision should cite ingested artifacts, not
only the existence of named employees.

Remote publication remains governed by the Publication Gate Protocol. A runner
adapter may do work, but it does not receive implicit authority to commit, push,
open PRs, or write remote comments.

## GitHub Protocol

GitHub sync is explicit:

- Local objects are the source of agent work structure.
- GitHub issues are remote collaboration records.
- Remote writes require `--apply`.
- Pull remote state before claiming remote closure when practical.
- Preserve remote URLs and issue numbers once linked.
- Write a sync report when local and remote state diverge.

## Publication Gate Protocol

GitHub Worknet means local records only: local issues, branches, tasks,
sessions, verification records, PR records, sync reports, and GitHub-ready
markdown artifacts.

GitHub Remote Publication means any real mutation to GitHub or a fork,
including `git push`, `gh pr create`, `gh issue comment`, `gh pr ready`,
`gh pr merge`, and `gh pr close`.

Remote publication is never implied by a GitHub Worknet task. Default stop
point for a company-governed trial is:

```text
local worknet complete + GitHub-ready artifacts prepared
```

Before gated actions, run the matching preflight:

```bash
structure-rule gate-check --action commit
structure-rule gate-check --action remote-push
structure-rule gate-check --action gh-pr-create
```

Missing approval is a blocker even when the shell can technically execute the
command. The CEO may coordinate, request, and prepare gated actions, but cannot
self-certify P13 or board approval.

Final pre-commit and pre-publication gates should be serial. Exploratory checks
may be parallel, but final gate evidence should be reviewed in order.

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
