# TaskFlow — engineering conventions

TaskFlow is a small Flask + SQLite task-tracking API. It exists as the review target for
PR Guardian, but it is written and maintained like production code. **Every change must
follow these conventions.** PR Guardian's Style & Architecture specialist checks them.

## 1. Data access
- **All SQL goes through `app/db.py`** (`db.query`, `db.execute`) with `?` placeholders.
- Never build SQL with f-strings, `%`, `.format()` or concatenation.
- Never call `sqlite3.connect` outside `app/db.py`; connections are per-request and closed by the teardown hook.

## 2. Layers
- `app/routes/*.py` are **thin controllers**: parse the request, call a service, return JSON.
- Business logic and SQL live in `app/services/*.py`.
- Blueprints are registered only in `create_app()`.

## 3. Authentication & authorisation
- Every route except `POST /users` and `GET /health` is decorated with `@require_auth`.
- Admin-only routes use `@require_admin`. Never gate admin behaviour on query params, headers or client-supplied flags.
- **Ownership scoping:** every task/comment query includes `user_id = ?` for the current user (no IDOR).

## 4. Configuration & secrets
- Secrets and environment-specific values come **only** from `app/config.py` → environment variables.
- No credential, token, webhook secret or private URL literal anywhere in the code.

## 5. Errors, logging, external calls
- No bare `except:`; catch specific exceptions. Use `abort(code, description=...)` for client errors.
- Log with `current_app.logger`, never `print`.
- Outbound HTTP calls set a timeout (`Config.HTTP_TIMEOUT_SECONDS`) and log failures.

## 6. Performance
- No database queries inside loops — use `JOIN`, `IN (...)` or aggregate queries.
- Use sets/dicts for membership and de-duplication, not nested loops.
- No module-level mutable state used as a cache (unbounded growth = memory leak).

## 7. Style
- `snake_case` for functions/variables, `PascalCase` for classes.
- Module docstring, function docstrings and type hints on all public functions.
- Functions stay under ~40 lines; split otherwise.

## 8. Tests
- Every new route or service function ships with tests in `tests/test_<module>.py`
  using the `client` / `auth_headers` fixtures from `tests/conftest.py`.
- Run: `cd demo-app && python -m pytest -q`. Coverage must not drop.
