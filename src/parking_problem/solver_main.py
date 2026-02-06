"""Facade to select solver backends."""

from __future__ import annotations

from typing import List

from .solvers.base import Solution
from .solvers import solver_ortools, solver_pulp, solver_pyomo


def solve(lengths: List[float], backend: str, pyomo_solver: str) -> Solution:
    if backend == "ortools":
        return solver_ortools.solve(lengths)
    if backend == "pulp":
        return solver_pulp.solve(lengths)
    if backend == "highs":
        return solver_pyomo.solve(lengths, "highs")
    if backend == "pyomo":
        return solver_pyomo.solve(lengths, pyomo_solver)
    raise SystemExit(f"Unknown solver backend: {backend}")
