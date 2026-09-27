# Severity levels (used by every specialist and by the merge step)

| Level | Meaning | Examples |
|---|---|---|
| **Critical** | Must be fixed before merge. Exploitable or data-destroying right now. | SQL/command injection, missing authentication, IDOR / missing ownership check, secret in code, data loss, crash on a common path |
| **Warning** | Should be fixed before merge. Will hurt under realistic load or make the change unmaintainable. | N+1 queries, O(n²) on unbounded input, connection/memory leaks, new behaviour with zero tests, SQL outside the data layer, swallowed exceptions |
| **Suggestion** | Nice to have. | naming, docstrings, type hints, logging style, small refactors |

When two specialists flag the same file:line, keep the highest severity and list both categories.
When unsure between two levels, choose the higher one and set Confidence to Medium.

## Tie-breaker (added after run 1, proposed by Bob during the merge step)
A Style or Architecture finding that has **no runtime impact in isolation** is capped at **Warning**,
unless the same line is independently exploitable — in which case the Security finding carries the
Critical and the convention violation is listed under it. Run 1 over-escalated 4 of 12 findings;
this rule targets those cases without lowering any security severity.
