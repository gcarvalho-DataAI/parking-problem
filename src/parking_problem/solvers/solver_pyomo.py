"""Pyomo-based backend for external solvers (HiGHS/GLPK/SCIP/CBC)."""

from __future__ import annotations

import os
from typing import List
from contextlib import redirect_stderr, redirect_stdout

from .base import Solution


def solve(lengths: List[float], solver_name: str) -> Solution:
    try:
        import pyomo.environ as pyo
    except Exception as exc:  # pragma: no cover - optional dependency
        raise SystemExit(f"Pyomo is not available: {exc}") from exc

    n = len(lengths)
    model = pyo.ConcreteModel()
    model.I = pyo.RangeSet(0, n - 1)
    model.x = pyo.Var(model.I, domain=pyo.Binary)
    model.L = pyo.Var(domain=pyo.NonNegativeReals)

    model.sum_a = pyo.Expression(expr=sum(lengths[i] * model.x[i] for i in model.I))
    model.sum_b = pyo.Expression(expr=sum(lengths[i] * (1 - model.x[i]) for i in model.I))

    model.c1 = pyo.Constraint(expr=model.sum_a <= model.L)
    model.c2 = pyo.Constraint(expr=model.sum_b <= model.L)
    model.obj = pyo.Objective(expr=model.L, sense=pyo.minimize)

    solver = pyo.SolverFactory(solver_name)
    if solver is None or not solver.available(exception_flag=False):
        raise SystemExit(
            f"Solver '{solver_name}' not available via Pyomo. "
            "Make sure it is installed and on PATH (or python package for HiGHS)."
        )

    try:
        time_limit = float(os.getenv("SOLVER_TIME_LIMIT", "0"))
    except ValueError:
        time_limit = 0
    if time_limit > 0:
        # Solver-specific time limit options
        if solver_name == "highs":
            solver.options["time_limit"] = time_limit
        else:
            solver.options["timelimit"] = time_limit
            solver.options["seconds"] = time_limit

    log_only = os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true"
    per_run_log = os.getenv("PER_RUN_LOG", "").lower() == "true"
    log_enabled = os.getenv("SOLVER_LOG", "").lower() == "true"
    log_path = os.getenv("SOLVER_LOG_PATH", "")
    if log_enabled and per_run_log and log_path:
        # Enable more verbose output if supported
        solver.options["output_flag"] = True
        solver.options["log_to_console"] = False
        try:
            result = solver.solve(model, tee=False, logfile=log_path)
        except NotImplementedError:
            with open(log_path, "w", encoding="utf-8") as f, redirect_stdout(f), redirect_stderr(f):
                result = solver.solve(model, tee=True)
    else:
        tee = log_enabled and (not log_only or per_run_log)
        result = solver.solve(model, tee=tee)

    if log_enabled and per_run_log and log_path:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("[pyomo_stats]\n")
            log_file.write(str(result.solver))
            log_file.write("\n")
    status = str(result.solver.status)

    side_a = [i for i in range(n) if pyo.value(model.x[i]) >= 0.5]
    side_b = [i for i in range(n) if i not in side_a]

    return Solution(
        status=status,
        max_side=float(pyo.value(model.L)),
        side_a=side_a,
        side_b=side_b,
        sum_a=sum(lengths[i] for i in side_a),
        sum_b=sum(lengths[i] for i in side_b),
    )
