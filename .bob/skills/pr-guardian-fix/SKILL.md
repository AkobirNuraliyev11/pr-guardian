---
name: pr-guardian-fix
description: >-
  Fix the Critical findings from the latest PR Guardian report and add the
  missing tests (Agent mode)
metadata:
  user-invocable: true
  disable-model-invocation: true
---

Use Agent mode for this task.

1. Read `reports/PR_GUARDIAN_REPORT.md`.
2. For every **Critical** finding apply the minimal fix that follows the project conventions in the nearest `AGENTS.md`
   (parameterised queries through the db helper, `@require_auth` / `@require_admin`, ownership scoping by `user_id`,
   secrets via `Config` / environment variables).
3. Add the tests proposed by the Test Coverage specialist under the project's `tests/` directory, using the existing fixtures.
4. Run the test suite (`cd demo-app && python -m pytest -q`) and make it pass.
5. Do not touch Warnings or Suggestions unless the fix is a one-liner in a file you already edited.
6. Finish with a checklist: finding → file → what changed, plus the test command output summary.
