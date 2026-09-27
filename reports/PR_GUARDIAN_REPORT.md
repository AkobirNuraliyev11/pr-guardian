# 🛡️ PR Guardian Report

**Branch:** `feature/search-export-report` → **Base:** `main` · **Files changed:** 3 · **Generated:** 2026-09-27 17:24

## Verdict: 🔴 BLOCK

| 🔴 Critical | 🟡 Warning | 🔵 Suggestion |
|:---:|:---:|:---:|
| 6 | 6 | 2 |

## Reviewer Brief — read these first
1. `demo-app/app/routes/reports.py:23` — SQL injection via f-string: unsanitised `q` parameter interpolated directly into SQL; full read access to any table. **(Critical)**
2. `demo-app/app/routes/reports.py:53` — Admin route gated only on `?admin=1` query param — no token check at all; any anonymous user can read every user's data. **(Critical)**
3. `demo-app/app/routes/reports.py:30` — IDOR: export endpoint fetches any task without verifying ownership; `raw sqlite3.connect()` also leaks the connection. **(Critical)**

## Specialist runs (parallel subagents)
| Specialist | Subagent | Findings |
|---|---|:---:|
| Security | general | 8 |
| Performance | explore | 5 |
| Test Coverage | explore | 8 |
| Style & Architecture | explore | 13 |

## Findings

### 🔴 Critical

---

### [Critical] SQL injection via f-string in `search()` query
- File: `demo-app/app/routes/reports.py:23`
- Category: Security, Architecture
- Evidence: `rows = db.query(f"SELECT * FROM tasks WHERE user_id = {user_id} AND title LIKE '%{q}%' ORDER BY id")`
- Why it matters: The `q` parameter is taken directly from the query string and interpolated into the SQL string without any escaping. An attacker can send `?q=' UNION SELECT * FROM users--` to exfiltrate any table. Also violates `demo-app/AGENTS.md` §1: "Never build SQL with f-strings, `%`, `.format()` or concatenation."
- Fix:
  ```python
  rows = db.query(
      "SELECT * FROM tasks WHERE user_id = ? AND title LIKE ? ORDER BY id",
      (user_id, f"%{q}%"),
  )
  ```
- Confidence: High

---

### [Critical] Admin route gated on `?admin=1` query param — no real authentication
- File: `demo-app/app/routes/reports.py:53`
- Category: Security, Architecture
- Evidence:
  ```python
  def admin_activity():
      if request.args.get("admin") != "1":
          return jsonify({"error": "forbidden"}), 403
  ```
- Why it matters: Any unauthenticated user who appends `?admin=1` receives a full dump of every user's username, task titles, statuses, and comment counts. The `@require_admin` decorator documented in `auth.py` and required by `demo-app/AGENTS.md` §3 is never applied. This is also an unauthenticated route because `@require_auth` is missing.
- Fix:
  ```python
  @bp.get("/admin/activity")
  @require_admin
  def admin_activity():
      """Per-user activity report for the admin dashboard."""
      # Remove the request.args.get("admin") guard entirely.
  ```
- Confidence: High

---

### [Critical] IDOR — `exportTaskCsv` fetches any task without scoping to the authenticated user
- File: `demo-app/app/routes/reports.py:30`
- Category: Security
- Evidence: `task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()`
- Why it matters: Any authenticated user can request `/reports/export/<any_task_id>` and download another user's task data and all its comments. The route never checks `task["user_id"] == current_user()["id"]`.
- Fix:
  ```python
  task = db.query(
      "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
      (task_id, current_user()["id"]),
      one=True,
  )
  ```
- Confidence: High

---

### [Critical] Raw `sqlite3.connect()` outside `db.py` — connection leak
- File: `demo-app/app/routes/reports.py:30`
- Category: Security, Architecture
- Evidence:
  ```python
  conn = sqlite3.connect(current_app.config["DATABASE"])
  conn.row_factory = sqlite3.Row
  task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
  ```
- Why it matters: This opens a second, unmanaged connection that is never explicitly closed, leaking a file descriptor on every request, bypassing `PRAGMA foreign_keys = ON`, and defeating teardown hooks. Violates `demo-app/AGENTS.md` §1: "Never call `sqlite3.connect` outside `app/db.py`."
- Fix: Replace with the project's `db.query()` helper (same fix as the IDOR finding above; both are resolved by switching to `db.query` with ownership filter).
- Confidence: High

---

### [Critical] Webhook secret and URL hardcoded as source-code literals
- File: `demo-app/app/services/notification_service.py:5`
- Category: Security
- Evidence:
  ```python
  WEBHOOK_URL = "https://hooks.example-chat.com/services/T0DEMO/B0DEMO/taskflow"
  WEBHOOK_SECRET = "tf-webhook-2026-Xk9pQ2mZ7vL4"
  ```
- Why it matters: Committing a secret into source control exposes it in every clone, fork, and CI log forever. `config.py` already provides `Config.WEBHOOK_URL` and `Config.WEBHOOK_SECRET` sourced from environment variables. `demo-app/AGENTS.md` §4 states: "No credential, token, webhook secret or private URL literal anywhere in the code."
- Fix: Delete both module-level literals. Read from config:
  ```python
  from flask import current_app
  url = current_app.config["WEBHOOK_URL"]
  secret = current_app.config["WEBHOOK_SECRET"]
  ```
- Confidence: High

---

### [Critical] Unbounded module-level export cache — memory leak + data retention
- File: `demo-app/app/routes/reports.py:14`
- Category: Performance, Security
- Evidence:
  ```python
  _EXPORT_CACHE = []
  ...
  _EXPORT_CACHE.append(data)   # line 47
  ```
- Why it matters: Every CSV export appends task content to a process-global list that is never pruned. This is an unbounded memory leak, and also retains sensitive user data in server memory indefinitely. `demo-app/AGENTS.md` §6: "No module-level mutable state used as a cache (unbounded growth = memory leak)."
- Fix: Remove `_EXPORT_CACHE` entirely (lines 14 and 47). If caching is intentional, use a bounded, TTL-scoped store (e.g. `functools.lru_cache` keyed by user+task, or Redis).
- Confidence: High

---

### 🟡 Warning

---

### [Warning] Webhook secret embedded in outbound JSON body
- File: `demo-app/app/services/notification_service.py:10`
- Category: Security
- Evidence: `body = json.dumps({"event": event, "payload": payload, "secret": WEBHOOK_SECRET}).encode()`
- Why it matters: Embedding the shared secret in the JSON body means any TLS terminator, logging proxy, or server that receives the request logs the secret. Standard practice is an HMAC header.
- Fix:
  ```python
  import hashlib, hmac as _hmac
  body = json.dumps({"event": event, "payload": payload}).encode()
  sig = _hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
  req = urllib.request.Request(
      url, data=body,
      headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
  )
  ```
- Confidence: High

---

### [Warning] Outbound HTTP call with no timeout and bare `except: pass`
- File: `demo-app/app/services/notification_service.py:13`
- Category: Security, Performance, Style
- Evidence:
  ```python
  try:
      urllib.request.urlopen(req)
  except:
      pass
  ```
- Why it matters: Without a timeout the worker thread hangs indefinitely on a slow endpoint, exhausting Flask worker pool under load. The bare `except: pass` swallows all exceptions (including `SystemExit`, `KeyboardInterrupt`) and hides all failures silently. `demo-app/AGENTS.md` §5: "Outbound HTTP calls set a timeout (`Config.HTTP_TIMEOUT_SECONDS`). No bare `except:`."
- Fix:
  ```python
  try:
      urllib.request.urlopen(req, timeout=current_app.config.get("HTTP_TIMEOUT_SECONDS", 3))
  except Exception:
      current_app.logger.warning("webhook notify failed", exc_info=True)
  ```
- Confidence: High

---

### [Warning] N+1 queries in `admin_activity()` endpoint
- File: `demo-app/app/routes/reports.py:59`
- Category: Performance
- Evidence:
  ```python
  for u in db.query("SELECT * FROM users ..."):
      for t in db.query("SELECT * FROM tasks WHERE user_id = ?", (u["id"],)):
          count = db.query("SELECT COUNT(*) AS c FROM comments WHERE task_id = ?", (t["id"],), ...)
  ```
- Why it matters: Issues 1 + N + (N×M) queries for N users with M tasks each. With 100 users × 10 tasks each, that's 1,101 queries per request. Will degrade significantly under realistic load.
- Fix: Replace with a single JOIN query:
  ```sql
  SELECT u.username, t.title, t.status, COUNT(c.id) AS comments
  FROM users u
  LEFT JOIN tasks t ON u.id = t.user_id
  LEFT JOIN comments c ON t.id = c.task_id
  GROUP BY u.id, t.id
  ORDER BY u.id
  ```
- Confidence: High

---

### [Warning] O(n²) tag deduplication in `tag_summary()`
- File: `demo-app/app/routes/reports.py:77`
- Category: Performance, Style
- Evidence:
  ```python
  for i in range(len(all_tags)):
      dup = False
      for j in range(len(unique)):
          if all_tags[i] == unique[j]:
  ```
- Why it matters: Nested-loop deduplication is O(n²). For a user with 1,000 tags: 500,000 comparisons. `demo-app/AGENTS.md` §6: "Use sets/dicts for membership and de-duplication, not nested loops."
- Fix:
  ```python
  unique = list(dict.fromkeys(all_tags))  # O(n), preserves insertion order
  ```
- Confidence: High

---

### [Warning] Zero test coverage for all new routes and `notification_service`
- File: `demo-app/app/routes/reports.py` (all endpoints), `demo-app/app/services/notification_service.py`
- Category: Tests
- Evidence: No `demo-app/tests/test_reports.py` exists; none of the four new endpoints (`/search`, `/export/<id>`, `/admin/activity`, `/tags`) have any tests.
- Why it matters: Three Critical security vulnerabilities (SQL injection, broken auth, IDOR) exist in untested code. `demo-app/AGENTS.md` §8: "Every new route or service function ships with tests in `tests/test_<module>.py`."
- Fix: Create `demo-app/tests/test_reports.py` covering:
  - `GET /reports/search` — requires auth, scoped to user, SQL-safe inputs
  - `GET /reports/export/<id>` — requires auth, 404 on missing, **403 when task owned by different user**
  - `GET /reports/admin/activity` — 401 without token, 403 for non-admin
  - `GET /reports/tags` — requires auth, returns unique tags only
- Confidence: High

---

### [Warning] Function name `exportTaskCsv` violates `snake_case` convention
- File: `demo-app/app/routes/reports.py:52`
- Category: Style
- Evidence: `def exportTaskCsv(task_id):`
- Why it matters: `demo-app/AGENTS.md` §7 requires `snake_case` for all functions. Inconsistent naming impairs grep/tooling and code review.
- Fix: Rename to `export_task_csv`.
- Confidence: High

---

### 🔵 Suggestion

---

### [Suggestion] Missing type hints on `notify()` in `notification_service.py`
- File: `demo-app/app/services/notification_service.py:8`
- Category: Style
- Evidence: `def notify(event, payload):`
- Why it matters: `demo-app/AGENTS.md` §7 requires type hints on all public functions. Missing hints reduce IDE assistance and documentation quality.
- Fix: `def notify(event: str, payload: dict) -> None:`
- Confidence: Medium

---

### [Suggestion] Missing docstring on `exportTaskCsv` (or `export_task_csv` after rename)
- File: `demo-app/app/routes/reports.py:52`
- Category: Style
- Evidence: `def exportTaskCsv(task_id):` — no docstring
- Why it matters: `demo-app/AGENTS.md` §7 requires docstrings on all public functions.
- Fix:
  ```python
  def export_task_csv(task_id: int):
      """Export a task and its comments as a CSV file."""
  ```
- Confidence: Medium

---

## Change-set coverage

| File | Security | Performance | Tests | Style/Arch |
|---|:---:|:---:|:---:|:---:|
| `demo-app/app/__init__.py` | ✓ | ✓ | ✓ | ✓ |
| `demo-app/app/routes/reports.py` | ✓ | ✓ | ✓ | ✓ |
| `demo-app/app/services/notification_service.py` | ✓ | ✓ | ✓ | ✓ |

## Next step
Switch to **Agent** mode and run `/pr-guardian-fix` to apply the Critical fixes and add the missing tests.
