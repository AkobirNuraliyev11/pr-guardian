---
name: pr-review
description: "\U0001F6E1️ PR Guardian — four parallel specialist subagents review the current branch against a base branch"
metadata:
  user-invocable: true
  disable-model-invocation: true
  argument-hint: <base-branch>
---

Run PR Guardian.

If the active mode is not "🛡️ PR Guardian" (slug `pr-guardian`), switch to it first.
Load the skill `pr-guardian-review` and follow its protocol exactly.

Base branch: $1 (if empty, use `main`).
Review everything that differs between the base branch and the current working tree (committed and uncommitted changes).

Spawn all four specialist subagents (Security, Performance, Test Coverage, Style & Architecture) in the same turn so they run in parallel, merge their findings, write `reports/PR_GUARDIAN_REPORT.md`, and reply with the verdict, the Critical/Warning/Suggestion counts and the Reviewer Brief.
