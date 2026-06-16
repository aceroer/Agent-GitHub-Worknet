# Real Trace: GitHub Issue Create Smoke

Date: 2026-06-16

Repository:

```text
https://github.com/aceroer/structure-rule-kit
```

## Purpose

This trace records the first real environment proof that Structure Rule Kit can
create a GitHub issue from a local network issue and write the remote URL back
into local metadata.

## Commands

A temporary local project was created outside the repository:

```bash
tmpdir=$(mktemp -d)
PYTHONPATH=. python3 -m structure_rule_kit.cli init --path "$tmpdir" --minimal
PYTHONPATH=. python3 -m structure_rule_kit.cli issue-create \
  --path "$tmpdir" \
  --title "Structure Rule Kit 0.9 smoke test" \
  --body "Temporary smoke test for v0.9 GitHub issue creation. This issue will be closed after verification."
PYTHONPATH=. python3 -m structure_rule_kit.cli github-issue-create \
  issue-0001 \
  --path "$tmpdir" \
  --repo aceroer/structure-rule-kit \
  --apply \
  --skip-missing-labels
```

Observed remote URL:

```text
https://github.com/aceroer/structure-rule-kit/issues/1
```

The smoke issue was then closed:

```bash
gh issue close 1 \
  --repo aceroer/structure-rule-kit \
  --comment "v0.9 smoke test completed; closing temporary verification issue."
```

Verification:

```bash
gh issue view 1 --repo aceroer/structure-rule-kit --json number,state,title,url
```

Observed result:

```json
{
  "number": 1,
  "state": "CLOSED",
  "title": "Structure Rule Kit 0.9 smoke test",
  "url": "https://github.com/aceroer/structure-rule-kit/issues/1"
}
```

## Local Write-Back Contract

After successful issue creation, the local issue record stores:

```json
{
  "remote": {
    "provider": "github",
    "repo": "aceroer/structure-rule-kit",
    "number": 1,
    "url": "https://github.com/aceroer/structure-rule-kit/issues/1",
    "synced_at": "<local timestamp>"
  }
}
```

## Closure Implication

This trace proves the first half of the closure loop:

```text
local issue -> GitHub issue -> local remote metadata
```

The remaining experimental work is:

- remote state pullback
- missing-label and missing-milestone repair
- sync report generation
- idempotent repeated sync
