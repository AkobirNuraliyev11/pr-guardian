# Video script — one continuous take, ≤ 3:00 (demo ≥ 90 s), no editing needed

Setup: Bob IDE full-screen, zoom 150 % (⌘ + twice), chat panel wide, run-1 chat open and scrolled to the top
(History → "/pr-review main"). Chrome behind it on PR #1 → Files changed. Record with ⌘⇧5 → Record Entire
Screen → Options → Microphone on. Normal pace; pauses are fine. Stop at 2:55.

| Time | Screen | Say |
|---|---|---|
| 0:00–0:20 | Chrome: PR #1 "Files changed" | This is a normal pull request: four new endpoints, about a hundred lines. It's been waiting since morning, and the reviewer will look at it at 6 p.m., tired, between two meetings. Hidden in it: a SQL injection, a hard-coded secret, a missing auth check and an IDOR. I'm Akobir, and this is PR Guardian. |
| 0:20–0:40 | Bob IDE: expand `.bob/` in the explorer | PR Guardian is IBM Bob turned into a review team. It's only this `.bob` folder — a custom mode, a skill with four specialist checklists, and one slash command. Copy it into any repo and Bob gets a new mode. |
| 0:40–1:30 | Run-1 chat, scroll slowly: command → "Dispatch four specialist subagents in parallel" panel | I switched to the PR Guardian mode and typed slash pr-review main. Bob captured the diff and dispatched four subagents in the same turn — here they are, running in parallel: performance, style and architecture, security, test coverage. Each has its own isolated context and its own checklist; the architecture agent reads our AGENTS.md, so it enforces *our* conventions. A hundred and forty seconds of specialist work finished in forty-two seconds, for a third of a Bobcoin. |
| 1:30–2:00 | Scroll to the verdict + Reviewer Brief; open `reports/PR_GUARDIAN_REPORT.md` | The orchestrator merged and de-duplicated the findings, ranked them Critical, Warning, Suggestion, and gave a verdict: BLOCK — with a Reviewer Brief, the three lines a human should read first. Every finding has file and line, evidence, why it matters, and a fix. |
| 2:00–2:15 | Scroll to the score output in the chat (or run `python3 scripts/score_report.py reports/PR_GUARDIAN_REPORT.md` in the terminal) | This branch had twelve planted defects; the answer key is hidden from Bob by .bobignore. Score: twelve of twelve, all four Criticals, for about one Bobcoin. |
| 2:15–2:45 | Mode → Agent, type `/pr-guardian-fix`, Enter, approve, show Bob start editing | The mode can't touch source — its edit permission is locked to the reports folder. Fixing is an explicit step: Agent mode, slash pr-guardian-fix, and Bob applies the Critical fixes and writes the missing tests. |
| 2:45–2:55 | Stay on the chat | A human still approves — but now they start with a ranked brief instead of a cold diff. PR Guardian: four Bob specialists, one report, before a tired reviewer opens the PR. |

After stopping the recording, let `/pr-guardian-fix` finish (approve its prompts), then `cd demo-app && python -m pytest -q`.

Upload: YouTube → Unlisted → title "PR Guardian — IBM Bob 2.0 Hackathon demo". Paste the link in the lablab form and in README.
