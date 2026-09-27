#!/usr/bin/env python3
"""Score a PR Guardian report against the seeded-defect answer key.

Usage: python scripts/score_report.py reports/PR_GUARDIAN_REPORT.md

A seeded defect counts as *caught* when the report mentions its file (basename is enough)
and at least one of its keywords. Severity is compared against the expected level.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = ROOT / "docs" / "answer-key" / "seeded_issues.json"
LEVELS = ("Critical", "Warning", "Suggestion")


def main(path: str) -> int:
    report = Path(path).read_text(encoding="utf-8")
    low = report.lower()
    issues = json.loads(KEY.read_text(encoding="utf-8"))

    # Split the report into finding blocks so we can read the severity next to each match.
    blocks = re.split(r"\n(?=### )", report)

    caught, sev_ok = 0, 0
    rows = []
    for issue in issues:
        fname = Path(issue["file"]).name.lower()
        hit_blocks = [
            b for b in blocks
            if fname in b.lower() and any(k.lower() in b.lower() for k in issue["keywords"])
        ]
        found = bool(hit_blocks) or (
            fname in low and any(k.lower() in low for k in issue["keywords"])
        )
        severity = "-"
        if hit_blocks:
            m = re.search(r"\[(Critical|Warning|Suggestion)\]|(Critical|Warning|Suggestion)", hit_blocks[0])
            severity = next((g for g in (m.groups() if m else ()) if g), "-")
        caught += found
        sev_match = found and severity == issue["expected"]
        sev_ok += sev_match
        rows.append((issue["id"], issue["agent"], issue["expected"], severity if found else "-", "✓" if found else "✗", issue["title"]))

    print(f"{'#':>2} {'Specialist':<13}{'Expected':<11}{'Reported':<11}{'Hit':<4}Defect")
    for r in rows:
        print(f"{r[0]:>2} {r[1]:<13}{r[2]:<11}{r[3]:<11}{r[4]:<4}{r[5]}")
    print()
    print(f"Caught {caught}/{len(issues)} seeded defects; severity matched on {sev_ok}/{caught}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "reports/PR_GUARDIAN_REPORT.md"))
