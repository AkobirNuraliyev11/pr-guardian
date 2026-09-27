"""User endpoints."""
import secrets

from flask import Blueprint, abort, jsonify, request

from .. import db
from ..auth import current_user, require_auth

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.post("")
def register():
    """Create a user and return its API token (the only unauthenticated write endpoint)."""
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    if not username:
        abort(400, description="username is required")
    if db.query("SELECT id FROM users WHERE username = ?", (username,), one=True):
        abort(409, description="username taken")
    token = secrets.token_urlsafe(32)
    user_id = db.execute(
        "INSERT INTO users (username, api_token) VALUES (?, ?)", (username, token)
    )
    return jsonify({"id": user_id, "username": username, "api_token": token}), 201


@bp.get("/me")
@require_auth
def me():
    """Return the caller's profile (never the token)."""
    user = current_user()
    return jsonify(
        {"id": user["id"], "username": user["username"], "is_admin": bool(user["is_admin"])}
    )
