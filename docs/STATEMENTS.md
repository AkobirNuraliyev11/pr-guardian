# Submission statements

## 1. Problem & Solution (≈430 words)

**The problem.** In most teams a pull request waits longer for review than it took to write. When the
review finally happens it is done by one person who is context-switching, tired, and expected to be a
security engineer, a performance engineer, a test engineer and the keeper of the team's conventions —
all at once, at 6 p.m. Review fatigue is how SQL injections, missing auth checks and N+1 queries reach
production. Teams respond either by slowing down (everything blocks on review) or by accepting the risk.

**The solution.** PR Guardian turns IBM Bob into a review *team*. It is a portable `.bob/` configuration —
a custom mode, a skill, four specialist checklists and two slash commands — that works in any repository
you open in Bob IDE. You check out the branch and type `/pr-review main`:

1. Bob captures the change set (`git diff` against the base branch).
2. It spawns **four specialist subagents in the same turn**, so they run in parallel, each in an isolated
   context with a focused checklist: **Security**, **Performance**, **Test Coverage**, and
   **Style & Architecture**. The last one reads the repository's `AGENTS.md`, so it enforces *this team's*
   conventions — "all SQL goes through `db.query`", "every route uses `@require_auth`" — rather than generic taste.
3. The orchestrator merges the four summaries, de-duplicates by file and line, ranks every finding
   **Critical / Warning / Suggestion**, computes a verdict (🔴 BLOCK · 🟡 NEEDS CHANGES · 🟢 APPROVE WITH
   COMMENTS) and writes `reports/PR_GUARDIAN_REPORT.md`, opening with a **Reviewer Brief**: the three
   places a human should look first.

The mode is deliberately **read-only on source code** — its edit permission is restricted to `reports/`,
so it is safe to run on any branch. Fixing is a separate, explicit step: `/pr-guardian-fix` in Agent mode
applies the Critical fixes and writes the missing tests.

**Results.** We built TaskFlow, a small Flask + SQLite API with written conventions, and opened a realistic
PR that plants 12 defects (4 security, 4 performance, 1 test gap, 3 style/architecture). The answer key is
hidden from Bob via `.bobignore`. PR Guardian caught **12 of 12**, including all four Criticals — SQL
injection, hard-coded secret, unauthenticated admin endpoint, IDOR — with 8 exact severity matches and 4
over-escalations (the safe direction), for about **one Bobcoin per review**, with the four specialists finishing in 42 seconds of wall-clock time (141 seconds of specialist work, run in parallel).

**Business value.** The human reviewer starts from a ranked brief instead of a cold diff; Critical issues
surface in minutes instead of days; and the cost of a review is a fraction of the cost of one missed
injection. Adoption is copying a folder — no CI changes, no infrastructure, no new tool to learn. Because
the conventions live in `AGENTS.md`, the review gets better every time the team writes a rule down.

**Why not just `/review`?** Bob's built-in review is one generalist pass. PR Guardian is a team of
specialists with isolated attention, a severity policy you can edit as a file, repo-convention awareness,
a sandboxed orchestrator, and a reproducible benchmark to prove it works.

## 2. IBM Bob Usage (≈420 words)

**Bob IDE is the runtime, not a helper.** PR Guardian has no server and no code of its own: the entire
product is Bob configuration that Bob IDE loads and executes. Every review, every finding and every fix in
this project was performed by Bob.

**Bob 2.0 features we built on**

- **Custom modes** (`.bob/custom_modes.yaml`). The 🛡️ PR Guardian mode defines the orchestrator's role and
  `whenToUse`, grants `read`, `execute`, `skill`, `subagent`, `todo`, and an `edit` group restricted with
  `fileRegex` to `reports/` — a least-privilege reviewer that can never touch source.
- **Subagents.** The mode allows both presets: the Security specialist runs on `general` (default model),
  the other three on `explore` (lighter, cheaper, read-only). The skill instructs Bob to spawn all four in
  one turn; Bob's parallel-subagents panel shows them running concurrently with isolated contexts.
- **Skills** (`.bob/skills/pr-guardian-review/`). `SKILL.md` holds the protocol; supporting files hold the
  finding schema, the report template and the four checklists that each subagent is told to read.
- **Mode-specific rules** (`.bob/rules-pr-guardian/`): a condensed workflow and the severity policy.
  **Workspace rules** (`.bob/rules/`) forbid secrets and reading the benchmark answer key.
- **Slash commands** (`.bob/commands/`): `/pr-review $1` and `/pr-guardian-fix`.
- **AGENTS.md hierarchy**: a root file describing the repo for Bob and `demo-app/AGENTS.md` with the
  conventions the Style & Architecture specialist enforces. **`.bobignore`** hides `docs/answer-key/`.
- **Agent mode** for the remediation step, and **task History export** for the evidence in `bob_sessions/`.

**Sessions (see `bob_sessions/`)**

- *task01 — full PR review.* `/pr-review main` on `feature/search-export-report`: four subagents in
  parallel, 12/12 seeded defects found, verdict BLOCK, report written, benchmark scored inside the same
  task (~0.96 Bobcoin, 32.5k context tokens).
- *task02 — fix Criticals + tests.* `/pr-guardian-fix` in Agent mode: Bob applied the fixes following
  `AGENTS.md` and generated the tests for the four new endpoints; the suite passes.

**Iterating with Bob.** In run 1 Bob rated four findings Critical where the key expected Warning or
Suggestion. Unprompted, Bob proposed a tie-breaker — cap style/architecture findings without runtime impact
at Warning unless the line is independently exploitable. We encoded it in
`.bob/rules-pr-guardian/10-severity.md`, so the severity policy is now a reviewable file that the team,
and Bob, can improve together.

**What we learned.** Bob spawns subagents sparingly by default, so parallelism must be demanded explicitly
in the skill; `explore` subagents are good enough for checklist-driven review, keeping a full four-agent
review near one Bobcoin; and a `fileRegex`-restricted mode is the simplest way to make an autonomous
reviewer safe to run anywhere.
