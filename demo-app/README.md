# TaskFlow (demo target)

A deliberately small Flask + SQLite API that PR Guardian reviews in the demo.

```bash
cd demo-app
pip install -r requirements.txt
python -m pytest -q          # test suite
python run.py                # http://127.0.0.1:5000/health
```

Endpoints: `POST /users`, `GET /users/me`, `GET|POST /tasks`, `GET|PATCH|DELETE /tasks/<id>`, `GET /health`.
Conventions live in [`AGENTS.md`](AGENTS.md) — PR Guardian's Style & Architecture specialist enforces them.
