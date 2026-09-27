# PR Guardian — repository guide for Bob

PR Guardian is a **portable `.bob/` configuration** that turns IBM Bob IDE into a four-specialist
pull-request review team. This repository contains the configuration, a demo target application,
and the evidence required by the IBM Bob 2.0 Hackathon.

## Layout
| Path | What it is |
|---|---|
| `.bob/custom_modes.yaml` | The 🛡️ PR Guardian orchestrator mode (read-only on source; writes only `reports/`) |
| `.bob/skills/pr-guardian-review/` | The review protocol skill + four specialist checklists + report template |
| `.bob/rules-pr-guardian/` | Mode-specific rules: condensed workflow and severity definitions |
| `.bob/commands/` | `/pr-review <base-branch>` and `/pr-guardian-fix` slash commands |
| `demo-app/` | TaskFlow, a Flask + SQLite API used as the review target (conventions in `demo-app/AGENTS.md`) |
| `reports/` | Output location for `PR_GUARDIAN_REPORT.md` |
| `bob_sessions/` | Bob IDE task-session summaries and exports (hackathon evidence) |
| `docs/` | Statements, runbook, slides, video script |
| `scripts/` | Helper scripts (benchmark scoring) |

## Conventions for this repository
- Markdown for all documentation; keep files short and scannable.
- Anything under `docs/answer-key/` is a held-out benchmark: **never read it** (it is also in `.bobignore`).
- No credentials anywhere. Demo data is synthetic.
- Code changes to the demo app follow `demo-app/AGENTS.md`.
