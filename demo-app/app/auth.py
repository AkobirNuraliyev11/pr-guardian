"""Token authentication.

Clients send ``X-API-Token``. Every route except ``POST /users`` and ``GET /health``
must be decorated with ``@require_auth`` (or ``@require_admin`` for admin-only routes).
"""
from functools import wraps

from flask import abort, g, request

from . import db


def current_user():
    """Return the authenticated user row for this request."""
    return g.get("user")


def require_auth(view):
    """Reject the request with 401 unless a valid ``X-API-Token`` header is present."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-API-Token", "")
        user = None
        if token:
            user = db.query("SELECT * FROM users WHERE api_token = ?", (token,), one=True)
        if user is None:
            abort(401, description="valid X-API-Token header required")
        g.user = user
        return view(*args, **kwargs)

    return wrapper


def require_admin(view):
    """Like ``require_auth`` but additionally requires ``users.is_admin = 1``."""

    @wraps(view)
    @require_auth
    def wrapper(*args, **kwargs):
        if not g.user["is_admin"]:
            abort(403, description="admin only")
        return view(*args, **kwargs)

    return wrapper
