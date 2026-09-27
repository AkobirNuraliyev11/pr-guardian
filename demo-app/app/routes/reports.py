"""Reporting endpoints for the Q4 dashboard: search, CSV export, admin activity, tag summary."""
import csv
import io

from flask import Blueprint, Response, current_app, jsonify, request

from .. import db
from ..auth import current_user, require_admin, require_auth
from ..services import notification_service

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.get("/search")
@require_auth
def search():
    """Search the caller's tasks by title substring."""
    q = request.args.get("q", "")
    user_id = current_user()["id"]
    rows = db.query(
        "SELECT * FROM tasks WHERE user_id = ? AND title LIKE ? ORDER BY id",
        (user_id, f"%{q}%"),
    )
    return jsonify([dict(r) for r in rows])


@bp.get("/export/<int:task_id>")
@require_auth
def export_task_csv(task_id: int):
    """Export a task and its comments as a CSV file."""
    task = db.query(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user()["id"]),
        one=True,
    )
    if task is None:
        return jsonify({"error": "not found"}), 404
    comments = db.query("SELECT * FROM comments WHERE task_id = ?", (task_id,))

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "title", "status", "tags", "comment"])
    if comments:
        for c in comments:
            writer.writerow([task["id"], task["title"], task["status"], task["tags"], c["body"]])
    else:
        writer.writerow([task["id"], task["title"], task["status"], task["tags"], ""])

    data = buf.getvalue()
    current_app.logger.info("exported task %s (%d bytes)", task_id, len(data))
    notification_service.notify("task.exported", {"task_id": task_id, "user": current_user()["username"]})
    return Response(data, mimetype="text/csv")


@bp.get("/admin/activity")
@require_admin
def admin_activity():
    """Per-user activity report for the admin dashboard."""
    rows = db.query(
        """
        SELECT u.username, t.title, t.status, COUNT(c.id) AS comments
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        LEFT JOIN comments c ON t.id = c.task_id
        GROUP BY u.id, t.id
        ORDER BY u.id
        """
    )
    report = [
        {"user": r["username"], "task": r["title"], "status": r["status"], "comments": r["comments"]}
        for r in rows
    ]
    return jsonify(report)


@bp.get("/tags")
@require_auth
def tag_summary():
    """Distinct tags used by the caller."""
    rows = db.query("SELECT tags FROM tasks WHERE user_id = ?", (current_user()["id"],))
    all_tags = [
        tag.strip()
        for r in rows
        for tag in r["tags"].split(",")
        if tag.strip()
    ]
    unique = list(dict.fromkeys(all_tags))
    return jsonify({"tags": unique, "count": len(unique)})
