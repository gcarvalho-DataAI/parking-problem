# Parking Problem Framework

This repository provides a reproducible framework to model and solve the **Parking Problem** (2-partition / number partitioning) with multiple open-source solvers, generate datasets, validate solutions, and produce comparative reports.

## Quick Start

```bash
uv sync
uv run python main.py --instance figure_21 --solver ortools
```

## Project Structure

- `src/parking_problem/` – core implementation (model, solver selection, validation)
- `src/parking_problem/solvers/` – solver backends (`ortools`, `pulp`, `pyomo`, `highs`)
- `datasets/` – instances grouped by origin
- `tests/` – test suite and logs
- `reports/` – final report and plots

## Datasets

Instances are split by origin:

- `datasets/disponibilizada/` – provided in the statement (Figure 2.1)
- `datasets/adaptada/` – adapted from bin packing lists
- `datasets/gerada/` – generated heavy instances

See `datasets/README.md` for details.

## Solvers

Supported backends:

- OR-Tools (CBC)
- PuLP (CBC)
- Pyomo (HiGHS)
- HiGHS

Solver selection is done via `--solver`.

## Running

Example with a provided instance:

```bash
uv run python main.py --instance figure_21 --solver ortools
```

Example with a dataset file:

```bash
uv run python main.py --instance-file datasets/disponibilizada/figure_2_1.json --solver highs
```

## Tests

Run all tests (with logging and convergence plots):

```bash
uv run pytest --plot
```

Logs and plots:

- `tests/logs/output_*.log` – per run logs
- `tests/logs/solver_*.log` – raw solver traces
- `tests/plots/` – convergence plots

## Reports

Final report:

- `reports/parking_problem_report.pdf`

Support files:

- `reports/solver_comparison.csv`
- `reports/solver_comparison.md`
- `reports/plots/`

## Environment

All dependencies are managed via **UV**:

- `uv sync`
- `uv run <command>`

---

**Author:** Gabriel Carvalho Domingos da Conceição
**LinkedIn:** https://www.linkedin.com/in/gabriel-carvalho-conceicao/  
**Repository:** https://github.com/gcarvalho-DataAI/parking-problem
