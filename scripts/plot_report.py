#!/usr/bin/env python3
"""Plot comparative charts from reports/solver_comparison.csv."""

from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

CSV_PATH = Path("reports/solver_comparison.csv")
OUT_DIR = Path("reports/plots")


def main() -> None:
    rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Plot time by solver (average over instances)
    times_by_solver = defaultdict(list)
    for r in rows:
        if r["time_sec"]:
            times_by_solver[r["solver"]].append(float(r["time_sec"]))

    solvers = sorted(times_by_solver.keys())
    avg_times = [sum(times_by_solver[s]) / len(times_by_solver[s]) for s in solvers]

    plt.figure(figsize=(6, 4))
    plt.bar(solvers, avg_times)
    plt.ylabel("Avg Time (s)")
    plt.title("Average Time by Solver")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "avg_time_by_solver.png", dpi=150)
    plt.close()

    # Plot convergence points by solver
    conv_by_solver = defaultdict(list)
    for r in rows:
        if r["conv_points"]:
            conv_by_solver[r["solver"]].append(int(r["conv_points"]))

    solvers = sorted(conv_by_solver.keys())
    avg_conv = [sum(conv_by_solver[s]) / len(conv_by_solver[s]) for s in solvers]

    plt.figure(figsize=(6, 4))
    plt.bar(solvers, avg_conv)
    plt.ylabel("Avg Convergence Points")
    plt.title("Average Convergence Points by Solver")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "avg_convergence_by_solver.png", dpi=150)
    plt.close()

    # Plot max_side by solver (average)
    ms_by_solver = defaultdict(list)
    for r in rows:
        if r["max_side"]:
            ms_by_solver[r["solver"]].append(float(r["max_side"]))

    solvers = sorted(ms_by_solver.keys())
    avg_ms = [sum(ms_by_solver[s]) / len(ms_by_solver[s]) for s in solvers]

    plt.figure(figsize=(6, 4))
    plt.bar(solvers, avg_ms)
    plt.ylabel("Avg Max Side")
    plt.title("Average Objective by Solver")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "avg_max_side_by_solver.png", dpi=150)
    plt.close()

    # Per-instance grouped bars (time, max_side, convergence)
    instances = sorted({r["instance"] for r in rows})
    solvers = sorted({r["solver"] for r in rows})

    def plot_grouped(metric_key: str, title: str, ylabel: str, filename: str) -> None:
        data = defaultdict(dict)
        for r in rows:
            v = r.get(metric_key, "")
            if v != "":
                data[r["instance"]][r["solver"]] = float(v)

        x = np.arange(len(instances))
        width = 0.8 / max(1, len(solvers))

        plt.figure(figsize=(8, 4))
        for i, solver in enumerate(solvers):
            vals = [data.get(inst, {}).get(solver, 0.0) for inst in instances]
            plt.bar(x + i * width, vals, width=width, label=solver)

        plt.xticks(x + width * (len(solvers) - 1) / 2, instances, rotation=30, ha="right")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(OUT_DIR / filename, dpi=150)
        plt.close()

    plot_grouped("time_sec", "Time by Instance and Solver", "Time (s)", "time_by_instance.png")
    plot_grouped("max_side", "Objective by Instance and Solver", "Max Side", "max_side_by_instance.png")
    plot_grouped("conv_points", "Convergence Points by Instance and Solver", "Convergence Points", "conv_by_instance.png")

    print(f"Plots written to {OUT_DIR}")


if __name__ == "__main__":
    main()
