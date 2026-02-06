from __future__ import annotations

from pathlib import Path

from tests.utils import ROOT, load_instance, run_matrix


def _instance_paths() -> list[Path]:
    return [
        ROOT / "datasets" / "disponibilizada" / "figure_2_1.json",
        ROOT / "datasets" / "adaptada" / "bp20_first_15.json",
        ROOT / "datasets" / "gerada" / "heavy_uniform_50.json",
        ROOT / "datasets" / "gerada" / "heavy_bimodal_100.json",
        ROOT / "datasets" / "gerada" / "heavy_narrow_200.json",
    ]


def test_all_instances_all_solvers() -> None:
    solvers = ["ortools", "pulp", "highs", "pyomo"]

    tasks = []
    for path in _instance_paths():
        lengths = load_instance(path)
        for solver in solvers:
            tasks.append((lengths, solver, "highs", path.name))
    run_matrix(tasks)
