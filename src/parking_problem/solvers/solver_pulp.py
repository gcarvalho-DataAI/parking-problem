"""PuLP + CBC backend."""

from __future__ import annotations

from typing import List

import os
import pulp

from .base import Solution


def solve(lengths: List[float]) -> Solution:
    n = len(lengths)
    model = pulp.LpProblem("parking_partition", pulp.LpMinimize)

    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(n)]
    L = pulp.LpVariable("L", lowBound=0)

    sum_a = pulp.lpSum(lengths[i] * x[i] for i in range(n))
    sum_b = pulp.lpSum(lengths[i] * (1 - x[i]) for i in range(n))

    model += L
    model += sum_a <= L
    model += sum_b <= L

    log_only = os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true"
    per_run_log = os.getenv("PER_RUN_LOG", "").lower() == "true"
    log_enabled = os.getenv("SOLVER_LOG", "").lower() == "true"
    log_path = os.getenv("SOLVER_LOG_PATH", "")
    try:
        time_limit = float(os.getenv("SOLVER_TIME_LIMIT", "0"))
    except ValueError:
        time_limit = 0
    if log_enabled and per_run_log and log_path:
        model.solve(pulp.PULP_CBC_CMD(msg=True, logPath=log_path, timeLimit=time_limit))
    else:
        msg = log_enabled and (not log_only or per_run_log)
        model.solve(pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit))

    side_a = [i for i in range(n) if pulp.value(x[i]) > 0.5]
    side_b = [i for i in range(n) if i not in side_a]

    return Solution(
        status=pulp.LpStatus[model.status],
        max_side=float(pulp.value(L)),
        side_a=side_a,
        side_b=side_b,
        sum_a=sum(lengths[i] for i in side_a),
        sum_b=sum(lengths[i] for i in side_b),
    )
