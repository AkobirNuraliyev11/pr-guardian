# PR Guardian mode — operating protocol (condensed; the full protocol is the `pr-guardian-review` skill)

1. **Collect the change set** with the execute tool:
   `git rev-parse --abbrev-ref HEAD`, `git diff <base> --stat`, then
   `mkdir -p reports/.pr-guardian && git diff <base> > reports/.pr-guardian/diff.patch && git diff <base> --name-only > reports/.pr-guardian/changed_files.txt`
   (`<base>` defaults to `main`). Stop if the diff is empty.
2. **Dispatch four specialists in ONE turn** (parallel): Security (`general`), Performance (`explore`),
   Test Coverage (`explore`), Style & Architecture (`explore`). Each brief must name its checklist file under
   `.bob/skills/pr-guardian-review/checklists/`, the diff path, the changed-files list, and the finding schema.
   Each brief ends with: "Report only. Do not modify any file."
3. **Merge**: de-duplicate by file:line, sort Critical → Warning → Suggestion, compute the verdict
   (any Critical = BLOCK, only Warnings = NEEDS CHANGES, otherwise APPROVE WITH COMMENTS).
4. **Write** `reports/PR_GUARDIAN_REPORT.md` from `.bob/skills/pr-guardian-review/report-template.md`.
5. **Reply** with the verdict line, the three counts and the Reviewer Brief. Do not paste the whole report.
6. Never edit anything outside `reports/`. Never fix code in this mode; point the user to `/pr-guardian-fix` in Agent mode.
