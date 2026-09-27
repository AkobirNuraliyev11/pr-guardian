---
name: pr-guardian-review
description: Run the PR Guardian protocol - diff a branch against its base, spawn four parallel specialist subagents (security, performance, test coverage, style/architecture), and merge their findings into one severity-ranked report with a Reviewer Brief.
---
# PR Guardian review protocol

You are the orchestrator. Specialists do the reading; you do the dispatching and the merging.

## Step 1 - Collect the change set (deterministic, execute tool)

1. Base branch = the argument the user gave; default `main`.
2. Run:
   ```
   git rev-parse --abbrev-ref HEAD
   git diff <base> --stat
   mkdir -p reports/.pr-guardian
   git diff <base> > reports/.pr-guardian/diff.patch
   git diff <base> --name-only > reports/.pr-guardian/changed_files.txt
   ```
   This captures committed branch changes **and** uncommitted edits relative to the base.
3. If `changed_files.txt` is empty, tell the user there is nothing to review and stop.

## Step 2 - Dispatch four specialists IN PARALLEL

Spawn **all four subagents in this same turn**. Do not wait for one before spawning the next.
Do not perform any specialist analysis yourself.

| Specialist | Subagent type | Checklist file |
|---|---|---|
| Security | `general` | `.bob/skills/pr-guardian-review/checklists/security.md` |
| Performance | `explore` | `.bob/skills/pr-guardian-review/checklists/performance.md` |
| Test Coverage | `explore` | `.bob/skills/pr-guardian-review/checklists/tests.md` |
| Style & Architecture | `explore` | `.bob/skills/pr-guardian-review/checklists/style-architecture.md` |

Every brief must be self-contained (subagents cannot see this conversation) and contain:

1. "You are the **<Specialist>** specialist of PR Guardian."
2. "Read your checklist at `<checklist file>` and follow it exactly."
3. "The change set is in `reports/.pr-guardian/diff.patch`; the changed files are listed in
   `reports/.pr-guardian/changed_files.txt`. Read the diff first, then open every changed file in full
   for context. Open callees/decorators/helpers when needed to confirm a finding."
4. For Style & Architecture only: "The project conventions are in `AGENTS.md` and `demo-app/AGENTS.md`
   (or the nearest `AGENTS.md` to the changed files). They are authoritative."
5. "Return your findings using exactly this schema, one block per finding:" followed by the finding schema
   from `finding-schema.md` (copy it verbatim into the brief).
6. "Report only. Do not modify any file. End with `Files reviewed:` and the list."

## Step 3 - Merge (you)

1. Collect the four summaries. Normalise severities to Critical / Warning / Suggestion using
   `.bob/rules-pr-guardian/10-severity.md`.
2. De-duplicate findings that point at the same file:line - keep the highest severity, mention both categories.
3. Sort Critical → Warning → Suggestion; inside a level, High confidence first.
4. Verdict: any Critical → **🔴 BLOCK**; only Warnings → **🟡 NEEDS CHANGES**; otherwise → **🟢 APPROVE WITH COMMENTS**.
5. Reviewer Brief = the three findings a tired human reviewer must look at first (file:line + one line why).
6. Write `reports/PR_GUARDIAN_REPORT.md` using `report-template.md`. Fill the specialist-run table
   (subagent type, number of findings).
7. Reply in chat with: the verdict line, the counts, the Reviewer Brief, and the report path. Nothing else.

## Guardrails

- Read-only on the codebase. The only writable location is `reports/`.
- Never fix code here. Point the user to Agent mode and `/pr-guardian-fix`.
- Do not run the application. Do not install packages.
- If a subagent fails, re-spawn that one specialist once; if it fails again, note it in the report and continue.
