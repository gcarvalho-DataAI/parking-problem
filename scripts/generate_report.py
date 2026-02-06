#!/usr/bin/env python3
"""Generate comparative solver report from logs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Tuple, List

LOG_DIR = Path("tests/logs")
OUT_MD = Path("reports/solver_comparison.md")
OUT_CSV = Path("reports/solver_comparison.csv")

STATUS_RE = re.compile(r"^\[result\] status=(.+?) max_side=([0-9.eE+-]+)")
TIME_RE = re.compile(r"^\[convergence\] ([0-9.]+),")


def parse_log(path: Path) -> Dict[str, str]:
    data = {
        "log": path.name,
        "instance": path.name.split("_", 1)[1].rsplit("_", 1)[0],
        "solver": path.name.split("_")[-2],
        "status": "",
        "max_side": "",
        "time_sec": "",
        "conv_points": "0",
    }
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    conv_points = 0
    for line in lines:
        m = STATUS_RE.search(line)
        if m:
            data["status"] = m.group(1)
            data["max_side"] = m.group(2)
        if line.startswith("[convergence]") and "time_sec" not in line:
            conv_points += 1
            if data["time_sec"] == "":
                tm = TIME_RE.search(line)
                if tm:
                    data["time_sec"] = tm.group(1)
    data["conv_points"] = str(conv_points)
    return data


def main() -> None:
    logs = sorted(LOG_DIR.glob("output_*.log"))
    rows = [parse_log(p) for p in logs]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    # CSV
    with OUT_CSV.open("w", encoding="utf-8") as f:
        f.write("instance,solver,status,max_side,time_sec,conv_points,log\n")
        for r in rows:
            f.write(",".join(
                [
                    r["instance"],
                    r["solver"],
                    r["status"],
                    r["max_side"],
                    r["time_sec"],
                    r["conv_points"],
                    r["log"],
                ]
            ) + "\n")

    # Markdown
    lines: List[str] = []
    lines.append("# Solver Comparison Report\n")
    lines.append("This report summarizes solver performance based on existing logs.\n")
    lines.append("## Summary Table\n")
    lines.append("| Instance | Solver | Status | Max Side | Time (s) | Convergence Points | Log |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['instance']} | {r['solver']} | {r['status']} | {r['max_side']} | {r['time_sec']} | {r['conv_points']} | `{r['log']}` |"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD} and {OUT_CSV}")


if __name__ == "__main__":
    main()
