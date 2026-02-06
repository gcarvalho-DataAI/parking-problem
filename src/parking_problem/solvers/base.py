"""Shared types and utilities for solver backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Solution:
    status: str
    max_side: float
    side_a: List[int]
    side_b: List[int]
    sum_a: float
    sum_b: float


def scale_lengths(lengths: List[float]) -> Tuple[List[int], int]:
    """Scale floats to ints for CP-SAT. Returns (scaled, factor)."""
    max_decimals = 0
    for v in lengths:
        s = f"{v:.10f}".rstrip("0").rstrip(".")
        if "." in s:
            max_decimals = max(max_decimals, len(s.split(".")[1]))
    factor = 10 ** max_decimals
    scaled = [int(round(v * factor)) for v in lengths]
    return scaled, factor
