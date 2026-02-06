#!/usr/bin/env python3
"""Append exact results table to the report markdown."""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path("reports/solver_comparison.csv")
MD_PATH = Path("reports/parking_problem_report.md")


def main() -> None:
    rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    lines = MD_PATH.read_text(encoding="utf-8").splitlines()

    # Remove previous appended table if present
    start_marker = "## Appendix B: Full Results Table"
    if start_marker in lines:
        idx = lines.index(start_marker)
        lines = lines[:idx]

    lines.append("")
    lines.append(start_marker)
    lines.append("")
    lines.append("| Instance | Solver | Status | Max Side | Time (s) | Convergence Points | Log |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['instance']} | {r['solver']} | {r['status']} | {r['max_side']} | {r['time_sec']} | {r['conv_points']} | `{r['log']}` |"
        )

    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Updated report with full results table")


if __name__ == "__main__":
    main()
