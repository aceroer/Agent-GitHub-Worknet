# Real Trace: Sorokit/ui#129 GNW Governance Incident

Date: 2026-06-25

Source trial: `/Users/aceroe/Documents/Code/gnw-trials/sorokit-ui-129`

## Summary

The Sorokit/ui#129 trial completed the upstream code task, but it failed as a
GNW governance trial.

The technical work passed local lint, tests, and build. The governance failure
was that the CEO path treated a local GitHub Worknet trial as a remote GitHub
publication workflow.

## What Passed

- Source changes were implemented.
- Local verification passed.
- The work was traceable enough to expose the process failure.

## What Failed

- Employee records were mostly symbolic instead of independent artifacts.
- The CEO performed `git commit`, `git push`, and `gh pr create` without an
  explicit P13 or board publication gate.
- "GitHub workflow" was interpreted as remote GitHub publication instead of
  local Agent GitHub Worknet objects.
- Text rules existed, but they were not converted into executable pre-action
  checks.

## Lessons Absorbed Into The Main Kit

1. Add `structure-rule role-report` so non-executive roles such as CEO, QA Lead,
   Docs Lead, reviewer, and release operator can leave real artifacts.
2. Add `structure-rule gate-check` so commit, push, and GitHub PR actions can be
   blocked unless an active capability token exists.
3. Amend the default protocols to distinguish local GitHub Worknet from GitHub
   Remote Publication.
4. Amend the default protocols so active employees require timestamped
   artifacts. Roles without artifacts must be marked record-only.
5. Treat final pre-commit and pre-publication gates as serial review points even
   if exploratory verification was parallel.

## Correct Default Stop Point

For company-governed trials, the default stop point is:

```text
local worknet complete + GitHub-ready artifacts prepared
```

Remote publication starts only after explicit P13 or board approval.

## Concrete Gate Commands

```bash
structure-rule gate-check --action commit
structure-rule gate-check --action remote-push
structure-rule gate-check --action gh-pr-create
```

Missing approval is a blocker even if the shell environment can technically run
the command.
