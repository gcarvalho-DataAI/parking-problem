#!/usr/bin/env python3
"""Generate convergence plots from existing log files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_convergence_lines(log_text: str) -> list[tuple[float, float]]:
    points = []
    for line in log_text.splitlines():
        if line.startswith("[convergence]") and "," in line:
            parts = line.replace("[convergence]", "").strip().split(",")
            if len(parts) >= 2 and parts[0] != "time_sec":
                try:
                    t = float(parts[0])
                    obj = float(parts[1])
                    points.append((t, obj))
                except ValueError:
                    continue
    return points


def parse_ortools(log_text: str) -> list[tuple[float, float]]:
    pattern = re.compile(r"^#\\d+\\s+(\\d+\\.?\\d*)s\\s+best:([0-9.]+)", re.MULTILINE)
    return [(float(m.group(1)), float(m.group(2))) for m in pattern.finditer(log_text)]


def parse_cbc(log_text: str) -> list[tuple[float, float]]:
    pattern = re.compile(
        r",\\s*([0-9.]+)\\s*best solution,\\s*best possible\\s*([0-9.]+)\\s*\\((\\d+\\.?\\d*) seconds\\)",
        re.IGNORECASE,
    )
    points = []
    for line in log_text.splitlines():
        m = pattern.search(line)
        if m:
            best_solution = float(m.group(1))
            t = float(m.group(3))
            points.append((t, best_solution))
    return points


def parse_highs_convergence(log_text: str) -> list[tuple[float, float]]:
    # Heuristic: capture lines like "Objective value:  28.6" with nearby "Time"
    obj_pattern = re.compile(r"Objective value:\\s*([0-9.+-eE]+)")
    time_pattern = re.compile(r"Time \\(Wallclock seconds\\):\\s*([0-9.]+)")
    points = []
    last_time = None
    for line in log_text.splitlines():
        tm = time_pattern.search(line)
        if tm:
            last_time = float(tm.group(1))
        om = obj_pattern.search(line)
        if om and last_time is not None:
            obj = float(om.group(1))
            points.append((last_time, obj))
    return points


def plot(points: list[tuple[float, float]], out_path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402

    if not points:
        return
    points = sorted(points, key=lambda x: x[0])
    times = [p[0] for p in points]
    objs = [p[1] for p in points]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.plot(times, objs, marker="o", linewidth=1)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Objective (max side)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs-dir", default="tests/logs")
    parser.add_argument("--out-dir", default="tests/plots")
    parser.add_argument("--pattern", default="output_*.log")
    args = parser.parse_args()

    logs_dir = Path(args.logs_dir)
    out_dir = Path(args.out_dir)

    for log_path in sorted(logs_dir.glob(args.pattern)):
        text = log_path.read_text(encoding="utf-8", errors="ignore")
        points = parse_convergence_lines(text)
        solver_log_path = logs_dir / log_path.name.replace("output_", "solver_")
        solver_text = ""
        if solver_log_path.exists():
            solver_text = solver_log_path.read_text(encoding="utf-8", errors="ignore")

        if len(points) <= 1:
            # try fallback parsers (prefer solver log if available)
            target_text = solver_text or text
            if "ortools" in log_path.name:
                points = parse_ortools(target_text)
            elif "pulp" in log_path.name:
                points = parse_cbc(target_text)
            elif "highs" in log_path.name or "pyomo" in log_path.name:
                points = parse_highs_convergence(target_text)

        title = log_path.stem
        out_path = out_dir / f"{log_path.stem}.png"
        plot(points, out_path, title)


if __name__ == "__main__":
    main()
