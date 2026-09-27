"""Business logic for tasks.

Routes stay thin; all task SQL lives here and goes through ``db.query``/``db.execute``.
Every query is scoped by ``user_id`` so users can only ever touch their own tasks.
"""
from .. import db

VALID_STATUSES = ("open", "in_progress", "done")


def list_tasks(user_id: int, status: str | None = None) -> list[dict]:
    """Return the user's tasks, optionally filtered by status."""
    if status:
        rows = db.query(
            "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id",
            (user_id, status),
        )
    else:
        rows = db.query("SELECT * FROM tasks WHERE user_id = ? ORDER BY id", (user_id,))
    return [dict(r) for r in rows]


def get_task(user_id: int, task_id: int) -> dict | None:
    """Return one task owned by the user, or ``None``."""
    row = db.query(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id), one=True
    )
    return dict(row) if row else None


def create_task(user_id: int, title: str, tags: list[str] | None = None) -> dict:
    """Create a task. Tags are normalised to a sorted, de-duplicated, lower-case list."""
    title = title.strip()
    if not title:
        raise ValueError("title is required")
    normalised = {t.strip().lower() for t in (tags or []) if t.strip()}
    task_id = db.execute(
        "INSERT INTO tasks (user_id, title, tags) VALUES (?, ?, ?)",
        (user_id, title, ",".join(sorted(normalised))),
    )
    return get_task(user_id, task_id)


def update_status(user_id: int, task_id: int, status: str) -> dict | None:
    """Change a task's status. Raises ``ValueError`` for unknown statuses."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}")
    db.execute(
        "UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", (status, task_id, user_id)
    )
    return get_task(user_id, task_id)


def delete_task(user_id: int, task_id: int) -> bool:
    """Delete a task (and its comments). Returns ``False`` if it does not exist."""
    if get_task(user_id, task_id) is None:
        return False
    db.execute("DELETE FROM comments WHERE task_id = ?", (task_id,))
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    return True
