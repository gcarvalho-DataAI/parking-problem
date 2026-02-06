#!/usr/bin/env python3
"""Entry point for running the Parking Problem solver."""

from __future__ import annotations

import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from parking_problem.cli import main  # noqa: E402


if __name__ == "__main__":
    main()
