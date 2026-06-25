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
