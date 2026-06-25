# Protocols

## Protocol Hierarchy

Follow human instruction first, then `structure/rules.md`, then this file, then
local notes.


## Role Protocol

- P1-P5 agents gather context, summarize, draft, and inspect.
- P6-P8 agents verify, implement scoped changes, and operate local worknet records.
- P9-P11 agents coordinate, manage low-risk local work, and prepare remote actions.
- P12 CEO agents coordinate globally but cannot override P13.
- P13 human supervisors own final approval, revocation, and takeover.
- COO/CTO/CFO/CSO/CRO offices are delegated responsibilities, not final ownership.

## Work Protocol

- Represent meaningful work as an issue, task, stream, meeting, or handoff.
- Keep object IDs stable.
- Prefer append-only records for decisions and events.
- Verify work before marking it complete.
- Record limitations when checks cannot run.

## Task Scale Routing Protocol

- Small tasks should stay single-threaded unless traceability needs more.
- Medium tasks should use GitHub worknet flow when issue, branch, PR, and sync records matter.
- Large tasks can use CEO/company architecture when parallel roles, route uncertainty, or human board governance are useful.
- Do not wrap every task in a company structure; use the lightest mode that preserves quality and traceability.
- Risk can selectively raise governance without creating a full company: add CSO, P13, or another specialist gate for secrets, legal boundaries, broad writes, live model calls, or remote publication.
- Worknet object writes must be serialized until atomic ID allocation or file locking exists; parallel reads are fine, but numbered object creation and stream/event writes should be sequenced.

## Authority Protocol

- Human owners have final authority.
- Remote writes and broad changes require explicit approval.
- Organization changes should be reviewed by a supervisor role.

## Handoff Protocol

A useful handoff names the active object, changed files, checks run, decisions,
risks, and next step.
