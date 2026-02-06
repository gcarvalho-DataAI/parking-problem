"""Solution validator for the Parking Problem."""

from __future__ import annotations

import math
from typing import List

from .solvers.base import Solution


def validate_lengths(lengths: List[float], expected_count: int | None = None) -> None:
    if expected_count is not None and len(lengths) != expected_count:
        raise ValueError(
            f"Invalid number of cars: expected {expected_count}, got {len(lengths)}"
        )

    if len(lengths) == 0:
        raise ValueError("Lengths list is empty")

    for i, v in enumerate(lengths):
        if not isinstance(v, (int, float)):
            raise ValueError(f"Length at index {i} is not numeric: {v!r}")
        if not math.isfinite(float(v)):
            raise ValueError(f"Length at index {i} is not finite: {v!r}")
        if float(v) <= 0:
            raise ValueError(f"Length at index {i} must be > 0: {v!r}")


def validate_solution(lengths: List[float], solution: Solution, tol: float = 1e-6) -> None:
    n = len(lengths)
    all_idx = set(solution.side_a) | set(solution.side_b)

    if len(all_idx) != n:
        missing = set(range(n)) - all_idx
        extra = all_idx - set(range(n))
        raise ValueError(f"Invalid indices: missing={sorted(missing)}, extra={sorted(extra)}")

    if set(solution.side_a) & set(solution.side_b):
        raise ValueError("Overlap between side_a and side_b")

    sum_a = sum(lengths[i] for i in solution.side_a)
    sum_b = sum(lengths[i] for i in solution.side_b)
    max_side = max(sum_a, sum_b)

    if abs(sum_a - solution.sum_a) > tol:
        raise ValueError(f"sum_a mismatch: expected {sum_a}, got {solution.sum_a}")
    if abs(sum_b - solution.sum_b) > tol:
        raise ValueError(f"sum_b mismatch: expected {sum_b}, got {solution.sum_b}")
    if abs(max_side - solution.max_side) > tol:
        raise ValueError(f"max_side mismatch: expected {max_side}, got {solution.max_side}")
