from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import os
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
import re
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import contextlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from parking_problem.validator import validate_solution  # noqa: E402
from parking_problem.solver_main import solve  # noqa: E402



def load_instance(path: Path) -> List[float]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["lengths"]


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _debug_enabled() -> bool:
    _load_dotenv()
    return os.getenv("DEBUG", "").lower() == "true"


def _max_threads() -> int:
    _load_dotenv()
    try:
        return max(1, int(os.getenv("MAX_THREADS", "1")))
    except ValueError:
        return 1


def _per_run_log() -> bool:
    _load_dotenv()
    return os.getenv("PER_RUN_LOG", "").lower() == "true"


def _plot_enabled() -> bool:
    _load_dotenv()
    return os.getenv("PLOT_CONVERGENCE", "").lower() == "true"


def _parse_cbc_convergence(log_text: str) -> list[tuple[float, float]]:
    # Example:
    # Cbc0010I After 2265000 nodes, ..., 138.6 best solution, best possible 138.55 (2145.67 seconds)
    pattern = re.compile(
        r",\s*([0-9.]+)\s*best solution,\s*best possible\s*([0-9.]+)\s*\((\d+\.?\d*) seconds\)",
        re.IGNORECASE,
    )
    points = []
    for line in log_text.splitlines():
        m = pattern.search(line)
        if m:
            best_solution = float(m.group(1))
            t = float(m.group(3))
            obj = best_solution
            points.append((t, obj))
    return points


def _parse_highs_convergence(log_text: str) -> list[tuple[float, float]]:
    # Heuristic: capture lines like "Objective value:  28.6" with nearby "Time"
    # or "Time (Wallclock seconds): 0.21"
    obj_pattern = re.compile(r"Objective value:\\s*([0-9.+-eE]+)")
    time_pattern = re.compile(r"Time \\(Wallclock seconds\\):\\s*([0-9.]+)")
    points = []
    last_time = None
    for line in log_text.splitlines():
        tm = time_pattern.search(line)
        if tm:
            last_time = float(tm.group(1))
        om = obj_pattern.search(line)
        if om and last_time is not None:
            obj = float(om.group(1))
            points.append((last_time, obj))
    return points


def _parse_ortools_convergence(log_text: str) -> list[tuple[float, float]]:
    # Example: "#3       0.01s best:286   next:[]"
    pattern = re.compile(r"^#\\d+\\s+(\\d+\\.?\\d*)s\\s+best:([0-9.]+)", re.MULTILINE)
    points = []
    for m in pattern.finditer(log_text):
        t = float(m.group(1))
        obj = float(m.group(2))
        points.append((t, obj))
    return points


def _parse_convergence_lines(log_text: str) -> list[tuple[float, float]]:
    points = []
    for line in log_text.splitlines():
        if line.startswith("[convergence]") and "," in line:
            parts = line.replace("[convergence]", "").strip().split(",")
            if len(parts) >= 2 and parts[0] != "time_sec":
                try:
                    t = float(parts[0])
                    obj = float(parts[1])
                    points.append((t, obj))
                except ValueError:
                    continue
    return points


def _plot_convergence(log_path: Path, title: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # noqa: E402
    except Exception:
        return

    log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    points = _parse_convergence_lines(log_text)
    if not points:
        return

    times = [p[0] for p in points]
    objs = [p[1] for p in points]

    plots_dir = ROOT / "tests" / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plots_dir / (log_path.stem + ".png")

    plt.figure(figsize=(6, 4))
    plt.plot(times, objs, marker="o", linewidth=1)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Objective (max side)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()


def _log(msg: str) -> None:
    if _debug_enabled():
        print(msg, flush=True)


@contextlib.contextmanager
def _redirect_fds(target_path: Path):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "a", encoding="utf-8") as f:
        fd_out = os.dup(1)
        fd_err = os.dup(2)
        os.dup2(f.fileno(), 1)
        os.dup2(f.fileno(), 2)
        try:
            yield
        finally:
            os.dup2(fd_out, 1)
            os.dup2(fd_err, 2)
            os.close(fd_out)
            os.close(fd_err)


def run_and_validate(
    lengths: List[float],
    solver: str,
    pyomo_solver: str = "highs",
    label: Optional[str] = None,
) -> None:
    instance_name = label or "instance"
    safe_instance = instance_name.replace(" ", "_")
    safe_solver = solver.replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log_dir = ROOT / "tests" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"output_{safe_instance}_{safe_solver}_{ts}.log"
    solver_log_path = log_dir / f"solver_{safe_instance}_{safe_solver}_{ts}.log"

    os.environ["SOLVER_LOG_PATH"] = str(solver_log_path)
    os.environ["CONVERGENCE_LOG_PATH"] = str(log_path)
    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"[run] instance={instance_name} solver={solver}\n")
        start = time.perf_counter()
        # Redirect native solver stdout/stderr to solver_log_path
        with _redirect_fds(solver_log_path):
            result = solve(lengths, solver, pyomo_solver)
        elapsed = time.perf_counter() - start
        f.write(f"[done] instance={instance_name} solver={solver} elapsed={elapsed:.3f}s\n")
        f.write(f"[result] status={result.status} max_side={result.max_side}\n")
        f.write(f"[result] sum_a={result.sum_a} sum_b={result.sum_b}\n")
        f.write(f"[result] side_a={result.side_a}\n")
        f.write(f"[result] side_b={result.side_b}\n")
        validate_solution(lengths, result)
        # Always write at least the final convergence point
        f.write("[convergence] time_sec,objective,status\n")
        f.write(f"[convergence] {elapsed:.6f},{result.max_side},{result.status}\n")

    if solver_log_path.exists() and solver_log_path.stat().st_size > 0:
        solver_log_text = solver_log_path.read_text(encoding="utf-8", errors="ignore")
        with log_path.open("a", encoding="utf-8") as f:
            f.write("[solver_log_begin]\n")
            f.write(solver_log_text)
            if not solver_log_text.endswith("\n"):
                f.write("\n")
            f.write("[solver_log_end]\n")

    # Append parsed convergence for solvers that log progress to file
    if solver in {"pulp", "highs", "pyomo", "ortools"}:
        log_text = (
            solver_log_path.read_text(encoding="utf-8", errors="ignore")
            if solver_log_path.exists()
            else log_path.read_text(encoding="utf-8", errors="ignore")
        )
        if solver == "pulp":
            points = _parse_cbc_convergence(log_text)
        elif solver == "ortools":
            points = _parse_ortools_convergence(log_text)
        else:
            points = _parse_highs_convergence(log_text)
        if points:
            with log_path.open("a", encoding="utf-8") as f:
                f.write("[convergence] time_sec,objective,status\n")
                for t, obj in points:
                    f.write(f"[convergence] {t:.6f},{obj},FEASIBLE\n")

    if _plot_enabled():
        _plot_convergence(
            log_path,
            title=f"{instance_name} | {solver}",
        )


def run_matrix(tasks: List[tuple[List[float], str, str, Optional[str]]]) -> None:
    max_threads = _max_threads()
    if len(tasks) <= 1:
        for lengths, solver, pyomo_solver, label in tasks:
            run_and_validate(lengths, solver, pyomo_solver, label)
        return

    if _per_run_log():
        _log(f"[run] parallel tasks={len(tasks)} max_processes={max_threads}")
        with ProcessPoolExecutor(max_workers=max_threads) as pool:
            futures = [
                pool.submit(run_and_validate, lengths, solver, pyomo_solver, label)
                for lengths, solver, pyomo_solver, label in tasks
            ]
            for future in as_completed(futures):
                future.result()
        return

    _log(f"[run] parallel tasks={len(tasks)} max_threads={max_threads}")
    with ThreadPoolExecutor(max_workers=max_threads) as pool:
        futures = [
            pool.submit(run_and_validate, lengths, solver, pyomo_solver, label)
            for lengths, solver, pyomo_solver, label in tasks
        ]
        for future in as_completed(futures):
            future.result()
