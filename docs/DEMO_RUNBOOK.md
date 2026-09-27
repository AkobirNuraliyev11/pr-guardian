# Demo runbook — reproduce the PR Guardian sessions in IBM Bob IDE

## 0. Prerequisites
- IBM Bob IDE installed and signed in (hackathon account).
- Python 3.10+ with `pip install -r demo-app/requirements.txt`.
- This repository cloned with both branches: `main` and `feature/search-export-report`.
- Open the **repository root** (`pr-guardian/`) as the workspace, otherwise `.bob/` is not discovered.

## 1. Verify the configuration loaded
- Mode picker shows **🛡️ PR Guardian** (Settings → Modes → project modes if you want to inspect the YAML).
- Typing `/` in the chat lists `/pr-review <base-branch>` and `/pr-guardian-fix`.

## 2. Task 01 — smoke test (cheap, 1-line diff)
```bash
git checkout main
echo "# smoke" >> demo-app/README.md
```
Select 🛡️ PR Guardian → `/pr-review main` → approve subagent spawning when asked.
Expected: four subagents in the parallel-subagents panel, a near-empty report, and a verdict line.
Then `git checkout -- demo-app/README.md`.

## 3. Task 02 — the full review (record the screen)
```bash
git checkout feature/search-export-report
```
Select 🛡️ PR Guardian → `/pr-review main` → approve → wait for the panel to show 4/4 complete.
Open `reports/PR_GUARDIAN_REPORT.md`. In the terminal:
```bash
python scripts/score_report.py reports/PR_GUARDIAN_REPORT.md
```
Commit the report: `git add reports/PR_GUARDIAN_REPORT.md && git commit -m "PR Guardian report"`.

## 4. Task 03 — fix Criticals + generate tests (Agent mode)
Switch to **Agent** → `/pr-guardian-fix` → approve edits → confirm `python -m pytest -q` passes in `demo-app/`.
Commit: `git commit -am "Address PR Guardian Critical findings; add reports tests"`.

## 5. Export the evidence after EVERY task
Chat panel → **Views and More Actions (…)** → **History** → select the task →
screenshot the consumption summary → **Export** the task history (Markdown) → save both to `bob_sessions/`
as `prguardian_taskNN_<description>_summary.png` and `prguardian_taskNN_<description>.md`.

## 6. Publish
```bash
git checkout main
git checkout feature/search-export-report -- bob_sessions reports README.md docs
git commit -m "Add Bob session evidence, report and submission docs"
git push origin main feature/search-export-report
```
Open a pull request `feature/search-export-report → main` on GitHub so judges can see the PR under review.
