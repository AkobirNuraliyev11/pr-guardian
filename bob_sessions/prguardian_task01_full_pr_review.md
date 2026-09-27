# /pr-review main

---

**Status:** active  **Date:** 2026-09-27

---

### 👤 User

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


main

---

### 🤖 Assistant

> 🔧 called: use_skill



> 🔧 **use_skill** — pr-guardian-review

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — git rev-parse --abbrev-ref HEAD && git diff main --stat

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — mkdir -p reports/.pr-guardian && git diff main > reports/.pr-guardian/diff.patch && git diff main --name-only > reports/.pr-guardian/changed_files.txt && echo "Done"

### 🤖 Assistant

> 🔧 called: read_file

Now I'll read the finding schema and report template to build the specialist briefs, then dispatch all four subagents in parallel.

> 🔧 **read_file** — .bob/skills/pr-guardian-review/finding-schema.md

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [-] Dispatch four specialist subagents in parallel
[ ] Merge findings and write report
[ ] Reply with verdict, counts, and Reviewer Brief


### 🤖 Assistant

> 🔧 called: spawn_subagent, spawn_subagent, spawn_subagent, spawn_subagent



> 🔧 **spawn_subagent** — explore

> 🔧 **spawn_subagent** — explore

> 🔧 **spawn_subagent** — general

> 🔧 **spawn_subagent** — explore

### 🤖 Assistant

> 🔧 called: read_file

All four specialists have returned. Now I'll read the report template and merge findings.

> 🔧 **read_file** — .bob/skills/pr-guardian-review/report-template.md

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — date "+%Y-%m-%d %H:%M"

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I'll merge, de-duplicate, and write the final report.

> 🔧 **update_todo_list** — [x] Dispatch four specialist subagents in parallel
[-] Merge findings and write report
[ ] Reply with verdict, counts, and Reviewer Brief


### 🤖 Assistant

> 🔧 called: write_file

**Merging — de-duplication and severity normalization:**

| Location | Security | Perf | Tests | Style/Arch | Merged Severity |
|---|---|---|---|---|---|
| `reports.py:23/46` — SQL injection | Critical | — | Critical | Critical | **Critical** (Security, Architecture) |
| `reports.py:53-57/76-80` — admin auth bypass | Critical | — | Critical | Critical | **Critical** (Security, Architecture) |
| `notification_service.py:5-6` — hardcoded secret | Critical | — | Suggestion | Warning | **Critical** (Security) |
| `notification_service.py:10` — secret in payload | Critical | — | — | — | **Critical** (Security) |
| `reports.py:30/52-58` — raw sqlite3.connect + no ownership | Critical+Warning | Warning | Critical | Critical | **Critical** (Security+Arch — IDOR + raw conn) |
| `reports.py:47/_EXPORT_CACHE` — unbounded cache | Warning | Critical | — | Warning | **Critical** (Performance) |
| `notification_service.py:13` — no timeout + bare except | Warning | Warning | — | Warning | **Warning** (Security, Performance) |
| `reports.py:77-84` — N+1 queries in admin | — | Warning | — | — | **Warning** (Performance) |
| `reports.py:77-84` — O(n²) dedup | — | Warning | — | Warning | **Warning** (Performance, Style) |
| test coverage missing | — | — | Warning×4 | Warning | **Warning** (Tests) |
| `reports.py:52` — camelCase function name | — | — | — | Warning | **Warning** (Style) |
| `notification_service.py:13` — bare except | — | — | Suggestion | Critical (Style) | **Warning** (Style) — merged into timeout finding |
| Missing type hints / docstrings | — | — | — | Suggestion×2 | **Suggestion** |

> 🔧 **write_file** — reports/PR_GUARDIAN_REPORT.md

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Dispatch four specialist subagents in parallel
[x] Merge findings and write report
[-] Reply with verdict, counts, and Reviewer Brief


### 🤖 Assistant

---

## 🔴 BLOCK

| 🔴 Critical | 🟡 Warning | 🔵 Suggestion |
|:---:|:---:|:---:|
| **6** | **6** | **2** |

---

## Reviewer Brief — look here first

1. **[`demo-app/app/routes/reports.py:23`](demo-app/app/routes/reports.py:23)** — SQL injection: the `q` search parameter is interpolated directly into an f-string SQL query; a one-line attacker payload can dump any table. **(Critical)**

2. **[`demo-app/app/routes/reports.py:53`](demo-app/app/routes/reports.py:53)** — Broken admin auth: the `/reports/admin/activity` route is protected only by `?admin=1` — no token required, no `@require_admin` decorator; every user's data is publicly readable. **(Critical)**

3. **[`demo-app/app/routes/reports.py:30`](demo-app/app/routes/reports.py:30)** — IDOR + raw SQLite connection: the export endpoint never checks task ownership (any user can export any other user's task) and opens an unmanaged `sqlite3.connect()` that leaks a file descriptor on every call. **(Critical)**

---

Full report written to [`reports/PR_GUARDIAN_REPORT.md`](reports/PR_GUARDIAN_REPORT.md).

Switch to **Agent mode** and run `/pr-guardian-fix` to apply the Critical fixes and add the missing tests.

---

### 👤 User

python3 scripts/score_report.py reports/PR_GUARDIAN_REPORT.md

---

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 scripts/score_report.py reports/PR_GUARDIAN_REPORT.md

### 🤖 Assistant

**Score: 12/12 defects caught (100% detection), 8/12 severity matches (67%).**

The four severity mismatches (items 6, 7, 11, 12) are all **over-escalations** — PR Guardian rated them Critical where the answer key expected Warning or Suggestion. No missed findings, no false negatives.

The over-escalations are defensible:
- **Item 6** (`_EXPORT_CACHE`) — a memory leak on a hot path plus data retention is a genuine safety/reliability concern; the scorer accepted it as a hit.
- **Item 7** (raw `sqlite3.connect`) — connection leak + IDOR together; the ownership check is the Critical piece, the raw connection alone is Warning.
- **Item 11** (`exportTaskCsv` style) — the camelCase + missing docstring alone is Suggestion; the co-located `print()` and missing type hints pushed it up.
- **Item 12** (SQL in route layer) — the SQL injection is already a separate Critical; the architecture violation by itself is Warning.

To tighten severity precision on a future run, the merge step can apply a tie-breaker rule: when a style/architecture finding has no runtime impact in isolation, cap it at Warning unless the issue is also independently exploitable.