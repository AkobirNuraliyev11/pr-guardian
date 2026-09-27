"""Development entrypoint: ``python run.py`` (never used with debug=True in production)."""
from app import create_app, db

app = create_app()
with app.app_context():
    db.init_db()

if __name__ == "__main__":
    app.run(port=5000)
