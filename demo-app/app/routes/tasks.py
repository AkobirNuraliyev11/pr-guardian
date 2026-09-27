"""Task endpoints - thin controllers: validate input, call the service, return JSON."""
from flask import Blueprint, abort, jsonify, request

from ..auth import current_user, require_auth
from ..services import task_service

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("")
@require_auth
def list_tasks():
    """List the caller's tasks (optional ``?status=`` filter)."""
    return jsonify(task_service.list_tasks(current_user()["id"], request.args.get("status")))


@bp.post("")
@require_auth
def create_task():
    """Create a task from ``{"title": str, "tags": [str]}``."""
    payload = request.get_json(silent=True) or {}
    try:
        task = task_service.create_task(
            current_user()["id"], payload.get("title", ""), payload.get("tags")
        )
    except ValueError as exc:
        abort(400, description=str(exc))
    return jsonify(task), 201


@bp.get("/<int:task_id>")
@require_auth
def get_task(task_id: int):
    """Fetch one of the caller's tasks."""
    task = task_service.get_task(current_user()["id"], task_id)
    if task is None:
        abort(404)
    return jsonify(task)


@bp.patch("/<int:task_id>")
@require_auth
def update_task(task_id: int):
    """Update a task's status from ``{"status": str}``."""
    payload = request.get_json(silent=True) or {}
    try:
        task = task_service.update_status(
            current_user()["id"], task_id, payload.get("status", "")
        )
    except ValueError as exc:
        abort(400, description=str(exc))
    if task is None:
        abort(404)
    return jsonify(task)


@bp.delete("/<int:task_id>")
@require_auth
def delete_task(task_id: int):
    """Delete one of the caller's tasks."""
    if not task_service.delete_task(current_user()["id"], task_id):
        abort(404)
    return "", 204
