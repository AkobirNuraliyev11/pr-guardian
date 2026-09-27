"""Application configuration.

Every secret and environment-specific value is read from environment variables here.
No other module may contain configuration literals.
"""
import os


class Config:
    DATABASE = os.environ.get("TASKFLOW_DATABASE", "taskflow.sqlite3")
    WEBHOOK_URL = os.environ.get("TASKFLOW_WEBHOOK_URL", "")
    WEBHOOK_SECRET = os.environ.get("TASKFLOW_WEBHOOK_SECRET", "")
    HTTP_TIMEOUT_SECONDS = float(os.environ.get("TASKFLOW_HTTP_TIMEOUT", "3"))
