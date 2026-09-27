# Reports

`PR_GUARDIAN_REPORT.md` is written by the 🛡️ PR Guardian mode after `/pr-review <base-branch>`.
`.pr-guardian/` holds the scratch diff for the specialists (git-ignored).

Score a report against the seeded benchmark:

```bash
python scripts/score_report.py reports/PR_GUARDIAN_REPORT.md
```
