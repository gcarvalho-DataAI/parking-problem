"""OR-Tools CP-SAT backend."""

from __future__ import annotations

from typing import List

import os
import time

from ortools.sat.python import cp_model

from .base import Solution, scale_lengths


def solve(lengths: List[float]) -> Solution:
    n = len(lengths)
    scaled, factor = scale_lengths(lengths)

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

    sum_a = model.NewIntVar(0, sum(scaled), "sum_a")
    sum_b = model.NewIntVar(0, sum(scaled), "sum_b")
    L = model.NewIntVar(0, sum(scaled), "L")

    model.Add(sum_a == sum(scaled[i] * x[i] for i in range(n)))
    model.Add(sum_b == sum(scaled[i] * (1 - x[i]) for i in range(n)))
    model.Add(sum_a <= L)
    model.Add(sum_b <= L)
    model.Minimize(L)

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = 0
    try:
        solver.parameters.max_time_in_seconds = float(os.getenv("SOLVER_TIME_LIMIT", "0"))
    except ValueError:
        pass
    log_only = os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true"
    per_run_log = os.getenv("PER_RUN_LOG", "").lower() == "true"
    log_enabled = os.getenv("SOLVER_LOG", "").lower() == "true" and (
        not log_only or per_run_log
    )
    if log_enabled:
        solver.parameters.log_search_progress = True
        log_path = os.getenv("SOLVER_LOG_PATH", "")
        if per_run_log and log_path:
            log_file = open(log_path, "a", encoding="utf-8")

            def _cb(text: str) -> None:
                log_file.write(text + "\n")
                log_file.flush()

            solver.log_callback = _cb

    conv_path = os.getenv("CONVERGENCE_LOG_PATH", "")
    if conv_path:
        start_time = time.perf_counter()

        class _ConvCB(cp_model.CpSolverSolutionCallback):
            def __init__(self) -> None:
                super().__init__()
                self._file = open(conv_path, "a", encoding="utf-8")

            def on_solution_callback(self) -> None:
                t = time.perf_counter() - start_time
                obj = self.ObjectiveValue() / factor
                self._file.write(f"[convergence] {t:.6f},{obj},FEASIBLE\n")
                self._file.flush()

        conv_cb = _ConvCB()
    else:
        conv_cb = None
    if conv_cb is not None and hasattr(solver, "SolveWithSolutionCallback"):
        status = solver.SolveWithSolutionCallback(model, conv_cb)
    else:
        status = solver.Solve(model)

    status_name = solver.StatusName(status)

    # Append solver statistics to log when enabled
    log_path = os.getenv("SOLVER_LOG_PATH", "")
    if log_enabled and per_run_log and log_path:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("[ortools_stats]\n")
            log_file.write(solver.ResponseStats())
            if not solver.ResponseStats().endswith("\n"):
                log_file.write("\n")
    side_a = [i for i in range(n) if solver.Value(x[i]) == 1]
    side_b = [i for i in range(n) if i not in side_a]

    sum_a_val = sum(lengths[i] for i in side_a)
    sum_b_val = sum(lengths[i] for i in side_b)

    return Solution(
        status=status_name,
        max_side=solver.Value(L) / factor,
        side_a=side_a,
        side_b=side_b,
        sum_a=sum_a_val,
        sum_b=sum_b_val,
    )
