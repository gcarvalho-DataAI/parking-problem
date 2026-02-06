from __future__ import annotations

from pathlib import Path

from tests.utils import ROOT, load_instance, run_matrix


def test_instance1_all_solvers() -> None:
    instance_path = ROOT / "datasets" / "disponibilizada" / "figure_2_1.json"
    lengths = load_instance(Path(instance_path))
    label = instance_path.name

    solvers = ["ortools", "pulp", "highs", "pyomo"]
    tasks = []
    for solver in solvers:
        tasks.append((lengths, solver, "highs", label))
    run_matrix(tasks)
