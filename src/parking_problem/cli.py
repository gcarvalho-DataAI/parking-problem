"""CLI for the Parking Problem solver."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .solver_main import solve
from .validator import validate_lengths, validate_solution


BP20_FIRST_15 = [
    1.1, 4.3, 3.9, 1.6, 2.7,
    2.5, 3.4, 4.0, 0.9, 0.6,
    4.3, 2.4, 3.9, 0.5, 2.5,
]

DEFAULT_FIGURE_21_PATH = Path("datasets/disponibilizada/figure_2_1.json")


def _load_instance_file(path: Path) -> List[float]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict) or "lengths" not in payload:
        raise SystemExit(f"Invalid instance file format: {path}")
    return payload["lengths"]


def _get_instance(name: str, instance_file: str | None) -> List[float]:
    if instance_file:
        return _load_instance_file(Path(instance_file))
    if name == "bp20_first_15":
        return BP20_FIRST_15
    if name == "figure_21":
        if not DEFAULT_FIGURE_21_PATH.exists():
            raise SystemExit(
                "Figure 2.1 instance file not found. "
                "Expected datasets/disponibilizada/figure_2_1.json"
            )
        return _load_instance_file(DEFAULT_FIGURE_21_PATH)
    raise SystemExit(f"Unknown instance: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instance",
        choices=["bp20_first_15", "figure_21"],
        default="bp20_first_15",
    )
    parser.add_argument(
        "--instance-file",
        help="Path to a JSON instance file (overrides --instance)",
    )
    parser.add_argument(
        "--solver",
        choices=["ortools", "pulp", "highs", "pyomo"],
        default="ortools",
        help="Choose open-source solver backend",
    )
    parser.add_argument(
        "--pyomo-solver",
        choices=["highs"],
        default="highs",
        help="Pyomo backend solver (used with --solver pyomo)",
    )
    args = parser.parse_args()

    lengths = _get_instance(args.instance, args.instance_file)
    validate_lengths(lengths, expected_count=15)
    result = solve(lengths, args.solver, args.pyomo_solver)
    validate_solution(lengths, result)

    print("status:", result.status)
    print("L (max side length):", result.max_side)
    print("side A indices:", result.side_a, "sum:", result.sum_a)
    print("side B indices:", result.side_b, "sum:", result.sum_b)


if __name__ == "__main__":
    main()
