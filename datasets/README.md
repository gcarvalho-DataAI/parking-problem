# Datasets

Instances are split by origin:

- `disponibilizada/`: instance from the original problem statement (Figure 2.1).
- `adaptada/`: instances adapted from other sources (e.g., 1D bin packing lists).
- `gerada/`: synthetic instances for stress-testing solvers.

Each instance file is a JSON object with:
- `name`
- `source`
- `lengths`

Notes
- `figure_2_1.json` is a placeholder until the figure values are provided.
- The CLI currently validates for 15 cars only. Larger instances are for custom scripts or after making the expected count configurable.
