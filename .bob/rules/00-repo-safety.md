# Repository safety rules (all modes)

- Never write credentials, tokens or API keys into any file. Configuration comes from environment variables.
- Never read or reference anything under `docs/answer-key/` — it is the held-out benchmark for PR Guardian.
- All data in this repository is synthetic and self-created. Do not introduce real personal or customer data.
- Do not run `git push`, `git commit --amend` or any destructive git command; the human commits.
- The demo target lives in `demo-app/`. Its conventions are in `demo-app/AGENTS.md` and are authoritative for that code.
