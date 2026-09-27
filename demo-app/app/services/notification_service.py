"""Webhook notifications for task events (used by the reporting endpoints)."""
import json
import urllib.request

WEBHOOK_URL = "https://hooks.example-chat.com/services/T0DEMO/B0DEMO/taskflow"
WEBHOOK_SECRET = "tf-webhook-2026-Xk9pQ2mZ7vL4"


def notify(event, payload):
    body = json.dumps({"event": event, "payload": payload, "secret": WEBHOOK_SECRET}).encode()
    req = urllib.request.Request(WEBHOOK_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
    except:
        pass
