"""SQLite helpers.

Every SQL statement in this codebase MUST go through ``query()`` or ``execute()``
with ``?`` placeholders. Never build SQL strings with f-strings, ``format`` or ``+``.
"""
import sqlite3
from pathlib import Path

from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    """Return the per-request connection, opening it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc: BaseException | None = None) -> None:
    """Close the per-request connection (registered as a teardown hook)."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    """Create tables from schema.sql (idempotent)."""
    schema = Path(__file__).resolve().parent.parent / "schema.sql"
    get_db().executescript(schema.read_text())
    get_db().commit()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)


def query(sql: str, params: tuple = (), one: bool = False):
    """Run a parameterised SELECT and return rows (or a single row when ``one=True``)."""
    rows = get_db().execute(sql, params).fetchall()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql: str, params: tuple = ()) -> int:
    """Run a parameterised INSERT/UPDATE/DELETE, commit, and return ``lastrowid``."""
    cur = get_db().execute(sql, params)
    get_db().commit()
    return cur.lastrowid
