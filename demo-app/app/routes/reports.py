"""Reporting endpoints for the Q4 dashboard: search, CSV export, admin activity, tag summary."""
import csv
import io
import sqlite3

from flask import Blueprint, Response, current_app, jsonify, request

from .. import db
from ..auth import current_user, require_auth
from ..services import notification_service

bp = Blueprint("reports", __name__, url_prefix="/reports")

_EXPORT_CACHE = []


@bp.get("/search")
@require_auth
def search():
    """Search the caller's tasks by title substring."""
    q = request.args.get("q", "")
    user_id = current_user()["id"]
    rows = db.query(f"SELECT * FROM tasks WHERE user_id = {user_id} AND title LIKE '%{q}%' ORDER BY id")
    return jsonify([dict(r) for r in rows])


@bp.get("/export/<int:task_id>")
@require_auth
def exportTaskCsv(task_id):
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        return jsonify({"error": "not found"}), 404
    comments = conn.execute("SELECT * FROM comments WHERE task_id = ?", (task_id,)).fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "title", "status", "tags", "comment"])
    if comments:
        for c in comments:
            writer.writerow([task["id"], task["title"], task["status"], task["tags"], c["body"]])
    else:
        writer.writerow([task["id"], task["title"], task["status"], task["tags"], ""])

    data = buf.getvalue()
    _EXPORT_CACHE.append(data)
    print(f"exported task {task_id} ({len(data)} bytes)")
    notification_service.notify("task.exported", {"task_id": task_id, "user": current_user()["username"]})
    return Response(data, mimetype="text/csv")


@bp.get("/admin/activity")
def admin_activity():
    """Per-user activity report for the admin dashboard."""
    if request.args.get("admin") != "1":
        return jsonify({"error": "forbidden"}), 403
    report = []
    for u in db.query("SELECT * FROM users ORDER BY id"):
        tasks = db.query("SELECT * FROM tasks WHERE user_id = ?", (u["id"],))
        for t in tasks:
            n = db.query("SELECT COUNT(*) AS c FROM comments WHERE task_id = ?", (t["id"],), one=True)["c"]
            report.append({"user": u["username"], "task": t["title"], "status": t["status"], "comments": n})
    return jsonify(report)


@bp.get("/tags")
@require_auth
def tag_summary():
    """Distinct tags used by the caller."""
    rows = db.query("SELECT tags FROM tasks WHERE user_id = ?", (current_user()["id"],))
    all_tags = []
    for r in rows:
        for tag in r["tags"].split(","):
            if tag:
                all_tags.append(tag)
    unique = []
    for i in range(len(all_tags)):
        dup = False
        for j in range(len(unique)):
            if all_tags[i] == unique[j]:
                dup = True
        if not dup:
            unique.append(all_tags[i])
    return jsonify({"tags": unique, "count": len(unique)})
