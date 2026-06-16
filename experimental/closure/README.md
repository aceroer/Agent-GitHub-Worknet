# Closure Experimental Layer

This folder is an experimental sublibrary for the Structure Rule Kit 1.0
closure path.

It is intentionally kept outside the stable Python package. The goal is to keep
real integration traces, rough scripts, and environment-facing experiments in
one public place before deciding which parts should become stable commands.

## Purpose

The closure layer asks whether the local agent network can become a complete
real-world workflow:

```text
local issue -> GitHub issue -> remote state -> local reconciliation -> report
```

Version 0.9 proved the first remote write path with `gh issue create`. The 1.0
closure experiment explores the remaining environment pieces:

- default GitHub repository config
- GitHub environment doctor
- label and milestone readiness
- idempotent issue sync
- remote state pullback
- conflict and missing-remote reports
- sync report artifacts

## Folder Contents

```text
experimental/closure/
├── README.md
├── ROADMAP.md
├── REAL_TRACE_2026-06-16.md
├── github_config.example.json
└── scripts/
    ├── github_doctor.py
    └── sync_report_from_network.py
```

## Stability

Everything in this folder is experimental. Scripts may change, move into the
stable CLI, or be replaced by a cleaner implementation in a later release.

The main rule is simple: keep real traces visible and reproducible, but do not
let experimental assumptions leak into the stable package API too early.

## Quick Checks

Check a GitHub environment:

```bash
python3 experimental/closure/scripts/github_doctor.py --repo owner/name
```

Build a local sync report from a project that has `structure/network/`:

```bash
python3 experimental/closure/scripts/sync_report_from_network.py \
  --path /path/to/project \
  --repo owner/name
```
