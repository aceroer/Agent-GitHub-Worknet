# Closure Roadmap

This is the experimental plan for turning the 0.9 GitHub bridge into a 1.0
closure workflow.

## Closure Definition

The workflow is closed when the same local network can safely complete this
cycle:

1. Create local issues, labels, milestones, and PR records.
2. Push supported objects to GitHub.
3. Store remote identifiers back into local records.
4. Pull remote state back into local records.
5. Report divergence, missing remotes, skipped records, and successful syncs.
6. Repeat without creating duplicates.

## 1.0 Candidate Scope

### GitHub Config

- Add a default repo config file.
- Let commands resolve `--repo` from config when omitted.
- Keep explicit CLI flags higher priority than config.

### GitHub Doctor

- Check whether `gh` is installed.
- Check whether `gh auth status` works.
- Check whether the target repo is readable.
- Check whether issues are enabled and accessible.
- Report label and milestone counts.

### Labels

- Detect missing remote labels before issue creation.
- Create missing labels only when explicitly requested.
- Store label creation in a sync report.

### Milestones

- Create missing milestones explicitly.
- Store milestone remote URL/number if GitHub exposes them.
- Allow issue creation to attach a synced milestone.

### Remote Pullback

- Read linked remote issues.
- Pull state, title, labels, assignees, milestone, and URL.
- Mark local records as `synced`, `remote-changed`, `missing-remote`, or
  `divergent`.

### Sync Report

- Generate `structure/network/github_export/sync_report.md`.
- Include created, skipped, failed, missing-label, missing-remote, and divergent
  records.
- Include enough command evidence for another agent to reproduce the state.

## Not In 1.0 Unless Trivial

- Real PR creation.
- Automatic conflict resolution.
- Rewriting remote issue bodies after creation.
- Bidirectional milestone policy beyond simple pullback.

## Promotion Rule

An experimental script can move into `structure_rule_kit/` only after it has:

- a stable command name
- tests with mocked `gh`
- at least one real trace
- documentation in the main README
- clear idempotency behavior
