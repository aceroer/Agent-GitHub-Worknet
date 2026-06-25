# Real Trace: Serfbound Good First Issue GNW Trial

Date: 2026-06-25

Trial workspace:

```text
/Users/aceroe/Documents/Code/gnw-trials/serfbound-good-first-issue
```

External repository:

```text
https://github.com/karolswdev/serfbound
```

External issue:

```text
https://github.com/karolswdev/serfbound/issues/5
```

## Purpose

This trace records the first live Agent GitHub Worknet trial where a company-style
agent organization was allowed to choose the execution route for an external
open-source issue.

The human board selected the issue and then stepped back. The observer only
monitored GNW state, repository status, and final artifacts.

## Scope

The trial issue was a low-risk documentation task:

```text
docs: add good-first-issue walkthrough
```

The issue acceptance criteria required a short path from issue selection to
branch, edit, `npm run test:docs`, `.tmp/CONTRACT.md`, and PR template, plus an
explanation for when a tiny docs-only change does not need a roadmap story
status flip.

## GNW Startup Events

Observed network log:

```json
{"timestamp": "2026-06-25T20:37:43", "event": "network_init"}
{"timestamp": "2026-06-25T20:38:34", "event": "issue_create", "id": "issue-0001", "title": "docs: add good-first-issue walkthrough"}
{"timestamp": "2026-06-25T20:39:40", "event": "github_config", "repo": "karolswdev/serfbound", "created": true}
{"timestamp": "2026-06-25T20:39:40", "event": "branch_create", "id": "docs-good-first-issue-walkthrough", "name": "docs/good-first-issue-walkthrough"}
{"timestamp": "2026-06-25T20:39:40", "event": "task_from_issue", "id": "issue-0001"}
{"timestamp": "2026-06-25T20:45:10", "event": "work_start", "id": "issue-0001"}
```

## Company Organization

The CEO agent created a company structure:

- CEO: global route, delegation, acceptance, escalation.
- CTO: file target, patch shape, verification strategy.
- COO: worknet hygiene and issue-to-PR route.
- CSO: PMO contract, asset boundary, and remote-write boundary.
- CRO: newcomer clarity and source-backed docs.
- CFO: scope and effort control.
- Docs Lead: walkthrough draft and focused docs verification.

The company files were written under:

```text
structure/company/
```

with `CEO_MEMO.md`, `ORG_CHART.md`, `SOLUTION_ROUTE.md`,
`EMPLOYEE_TASKS.md`, `ISSUE_CONTEXT.md`, and later `BOARD_REPORT.md`.

## Local Patch Result

The CEO-directed run produced a local patch in:

```text
repositories/serfbound
```

Final branch:

```text
docs/good-first-issue-walkthrough
```

Changed files:

```text
CONTRIBUTING.md
scripts/check-docs.mjs
```

Observed diff stat:

```text
CONTRIBUTING.md        | 26 ++++++++++++++++++++++++++
scripts/check-docs.mjs |  3 +++
2 files changed, 29 insertions(+)
```

No remote write was performed before the human board reviewed the local result.
After review, the board explicitly approved fork-branch draft PR publication.

## Verification

The GNW verification log recorded:

```text
Command: npm run test:docs
Result: passed in repositories/serfbound: serfbound-docs-ok
Notes: Ran after editing CONTRIBUTING.md and scripts/check-docs.mjs for karolswdev/serfbound#5.
```

The board report also recorded the focused docs gate result:

```text
serfbound-docs-ok: player, developer, static hosting, contributor, and GitHub templates cover required topics.
```

## Work End Event

The worknet closed the local task with:

```json
{"timestamp": "2026-06-25T20:48:24", "event": "work_end", "id": "issue-0001", "done": "Implemented local Serfbound docs patch for issue #5; added board report and executive reviews.", "verification": true}
```

Final local status:

```text
No blocker for local completion. PR publication requires human approval before remote writes.
Next Step: Human board decides whether to publish PR.
```

## Publication Event

After the board approved publication, the CEO followed the upstream hook and
fork workflow:

- Created `.tmp/CONTRACT.md` with 8/8 required checkboxes.
- Configured `core.hooksPath` to `.githooks`.
- Committed normally; the PMO pre-commit hook accepted the contract and deleted
  `.tmp/CONTRACT.md`.
- Created the fork `aceroer/serfbound`.
- Pushed branch `docs/good-first-issue-walkthrough` to the fork.
- Opened draft PR #6 into `karolswdev/serfbound:main`.

Published draft PR:

```text
https://github.com/karolswdev/serfbound/pull/6
```

Commit:

```text
752a876 docs: add good-first-issue walkthrough
```

## Boundary Observations

The run preserved the intended governance boundary:

- Human board selected the external issue.
- CEO agent owned route and delegation.
- Observer did not decide patch shape.
- External repository changes stayed local until the board approved publication.
- Remote PR publication was performed only after explicit human approval.
- Upstream read-only permissions were respected by using a fork branch and draft
  PR.

## Engineering Finding

The run exposed one concrete GNW reliability gap:

```text
Parallel executive-delegate calls collided on assignment-0004 and corrupted JSON;
the local template package currently has no object ID lock.
```

The company recorded a local decision:

```text
Serialize worknet object writes in this company.
```

This should become a product-level fix: worknet object allocation needs atomic ID
generation or a file lock before parallel agent writes are safe.

## CEO Retrospective

The biggest operating lesson was that a CEO agent should not flatten the whole
job into a single script. Its real work is to split uncertainty into accountable
offices:

- CTO owned the patch target and verification route.
- CSO owned hook, permission, data-boundary, and remote-write risk.
- CFO kept the small issue from expanding into a larger project.
- CRO checked whether the result was readable for a newcomer.
- COO kept the worknet state and delivery flow coherent.

The CEO's strongest move was not writing the document. It was making sure every
important judgment had an owner, then deciding when the route was ready to
converge.

The second lesson was operational: organization state must be serialized or
locked. Parallel delegation collided on `assignment-0004` and damaged JSON. That
is not a cosmetic bug. Once multiple agent roles act at the same time, the
worknet needs atomic ID allocation, lock files, or transaction-style writes.
Otherwise the organization can look busy while its ledger breaks first.

The third lesson was that safety boundaries should appear before action, not at
the end as paperwork. In this run, `.tmp/CONTRACT.md`,
`.githooks/pre-commit`, and the fork-PR path were treated as release gates from
the start. That kept publication clean: normal hook flow, full contract checks,
fork branch, and draft PR.

The resulting CEO pattern is:

```text
do not replace employees;
make tasks finish naturally inside the right institution.
```

This model is viable, but the next product focus should be:

- concurrency governance for worknet writes
- automatic executive report aggregation
- task-scale routing so small issues do not pay company-level overhead
- risk-aware routing so a high-risk small task can add a specialist gate without
  paying full company overhead

## Closure Implication

This trace proves a larger section of the closure loop:

```text
external GitHub issue
-> local GNW issue
-> CEO-led organization
-> local branch
-> local patch
-> verification record
-> board report
-> human-gated remote publication
-> fork branch draft PR
```

Publication is not automatic. Remote write actions remain explicit board
decisions, and the chosen route depends on repository permissions.
