#!/usr/bin/env python3
"""Generate heavy instances for benchmarking as separate JSON files."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def gen_uniform(n: int, lo: float, hi: float, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [round(rng.uniform(lo, hi), 2) for _ in range(n)]


def gen_bimodal(n: int, lo1: float, hi1: float, lo2: float, hi2: float, seed: int) -> list[float]:
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(n):
        if rng.random() < 0.5:
            out.append(round(rng.uniform(lo1, hi1), 2))
        else:
            out.append(round(rng.uniform(lo2, hi2), 2))
    return out


def gen_narrow(n: int, center: float, spread: float, seed: int) -> list[float]:
    rng = random.Random(seed)
    return [round(center + rng.uniform(-spread, spread), 2) for _ in range(n)]


def write_instance(out_dir: Path, name: str, lengths: list[float]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"name": name, "source": "gerada", "lengths": lengths}
    with (out_dir / f"{name}.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="datasets/gerada")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    write_instance(out_dir, "heavy_uniform_50", gen_uniform(50, 1.0, 10.0, seed=123))
    write_instance(out_dir, "heavy_bimodal_100", gen_bimodal(100, 0.1, 2.0, 8.0, 10.0, seed=456))
    write_instance(out_dir, "heavy_narrow_200", gen_narrow(200, 5.0, 0.6, seed=789))


if __name__ == "__main__":
    main()
