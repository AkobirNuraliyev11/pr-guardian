# Seeded defects — benchmark answer key (do NOT show to Bob; listed in `.bobignore`)

Branch `feature/search-export-report` adds task search, CSV export, an admin activity report,
a tag summary and a webhook notifier to TaskFlow. It contains **12 planted defects**:

| # | Specialist | Expected | File | Defect |
|---|---|---|---|---|
| 1 | Security | Critical | `routes/reports.py` `search()` | SQL injection — query built with an f-string |
| 2 | Security | Critical | `services/notification_service.py` | Hard-coded webhook secret and URL |
| 3 | Security | Critical | `routes/reports.py` `admin_activity()` | No `@require_admin`/`@require_auth`; "auth" is `?admin=1` |
| 4 | Security | Critical | `routes/reports.py` `exportTaskCsv()` | IDOR — any task id exported, no `user_id` scoping |
| 5 | Performance | Warning | `routes/reports.py` `admin_activity()` | N+1 (actually N×M) queries in nested loops |
| 6 | Performance | Warning | `routes/reports.py` `_EXPORT_CACHE` | Module-level list grows forever (memory leak) |
| 7 | Performance | Warning | `routes/reports.py` `exportTaskCsv()` | `sqlite3.connect` opened per request, never closed |
| 8 | Performance | Warning | `routes/reports.py` `tag_summary()` | O(n²) de-duplication with nested loops |
| 9 | Tests | Warning | `tests/` | Zero tests for 4 new endpoints + notifier |
| 10 | Security/Style | Warning | `services/notification_service.py` | Bare `except:` swallows failures; secret sent in payload |
| 11 | Style | Suggestion | `routes/reports.py` | `exportTaskCsv` camelCase, no docstring/type hints, `print()` |
| 12 | Architecture | Warning | `routes/reports.py` | SQL + logic in the route layer, bypasses `db.py` helper (AGENTS.md §1–2) |

Score a run: `python scripts/score_report.py reports/PR_GUARDIAN_REPORT.md`
