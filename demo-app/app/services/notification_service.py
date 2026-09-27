"""Webhook notifications for task events (used by the reporting endpoints)."""
import json
import urllib.request

from flask import current_app


def notify(event: str, payload: dict) -> None:
    """Send a webhook notification for a task event.

    If ``WEBHOOK_URL`` is not configured the call is a no-op.
    Failures are logged at WARNING level and never re-raised.
    """
    url = current_app.config.get("WEBHOOK_URL", "")
    if not url:
        return
    secret = current_app.config.get("WEBHOOK_SECRET", "")
    body = json.dumps({"event": event, "payload": payload, "secret": secret}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    timeout = current_app.config.get("HTTP_TIMEOUT_SECONDS", 3)
    try:
        urllib.request.urlopen(req, timeout=timeout)
    except Exception:
        current_app.logger.warning("webhook notify failed", exc_info=True)
