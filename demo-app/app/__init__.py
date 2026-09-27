"""TaskFlow - a small task-tracking API used as the PR Guardian demo target."""
from flask import Flask

from . import db
from .config import Config


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .routes import tasks, users

    app.register_blueprint(users.bp)
    app.register_blueprint(tasks.bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
