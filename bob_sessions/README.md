# Bob IDE task sessions (hackathon evidence)

Naming: `prguardian_taskNN_<description>_summary.png` (consumption summary) + `prguardian_taskNN_<description>.md` (exported task history).

| # | What | Mode | Bobcoins | Files |
|---|---|---|---|---|
| 01 | `/pr-review main` on `feature/search-export-report`: 4 parallel subagents, 12/12 seeded defects found, verdict BLOCK, report written and scored | 🛡️ PR Guardian | 0.962 | `prguardian_task01_full_pr_review_summary.png`, `prguardian_task01_full_pr_review.md` |
| 02 | Same conversation continued with `/pr-guardian-fix`: 6 Critical fixes, 4 warning one-liners, 19 new tests in `tests/test_reports.py`, 28 passed | Agent | 3.15 cumulative (review + fix) | `prguardian_task02_fix_criticals_and_tests_summary.png`, `prguardian_task02_fix_criticals_and_tests.md` |

Produced in Bob IDE: task header → consumption summary → screenshot; **↑ Export** → Markdown. Workspace: `pr-guardian`. Solo participant: Akobir Nuraliyev.
