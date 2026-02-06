#!/usr/bin/env python3
"""Generate a LaTeX report with equations, tables, and plots."""

from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime

CSV_PATH = Path("reports/solver_comparison.csv")
OUT_TEX = Path("reports/parking_problem_report.tex")
PLOTS_DIR = Path("reports/plots")


def load_table():
    rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def esc_tex(s: str) -> str:
    return (
        s.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("~", "\\textasciitilde{}")
        .replace("^", "\\textasciicircum{}")
    )


def main() -> None:
    rows = load_table()
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)

    tex = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{margin=2.5cm}

\title{Parking Problem: Methodology and Solver Comparison}
\author{}
\date{Generated: %s}

\begin{document}
\maketitle

\section*{Abstract}
This report addresses a parking allocation problem in which a fixed number of cars must be arranged along both sides of a street while minimizing the maximum occupied length. The problem is formulated as a Number Partitioning problem (equivalent to $P2\parallel C_{\max}$) and solved with exact optimization. A comparative analysis of open-source solvers (OR-Tools, PuLP/CBC, and Pyomo/HiGHS) is presented, including timing, objective value, and convergence behavior.

\section{Problem and Theoretical Background}
The Parking Problem is a 2-partition (2-bin packing) instance, known to be NP-hard. The goal is to split car lengths into two groups so that the maximum total length is minimized.

\section{Mathematical Formulation}
Let $\lambda_i$ be the length of car $i$, for $i=1,\dots,n$.
Define a binary variable $x_i$ such that:
\begin{align*}
  x_i &= 1 \quad \text{if car } i \text{ is assigned to Side A}\\
  x_i &= 0 \quad \text{if car } i \text{ is assigned to Side B}
\end{align*}
Let $L$ be the maximum occupied length between the two sides.

\textbf{Objective:}
\[
\min L
\]

\textbf{Constraints:}
\[
\sum_{i=1}^{n} \lambda_i x_i \le L
\]
\[
\sum_{i=1}^{n} \lambda_i (1 - x_i) \le L
\]
\[
x_i \in \{0,1\}, \quad \forall i
\]
\[
L \ge 0
\]

\section{Framework Methodology}
The framework was built with a modular, multi-backend structure:
\begin{itemize}
\item Separate solver backends per file (OR-Tools, PuLP/CBC, Pyomo/HiGHS).
\item Central solver facade to select backend and normalize outputs.
\item Validation layer to verify solution correctness.
\item Logging and convergence extraction from solver logs.
\end{itemize}

\section{Datasets}
Instances are grouped by origin:
\begin{itemize}
\item Provided: Figure 2.1 (15 cars).
\item Adapted: 15 items from a bin packing list (bp20\_first\_15).
\item Generated: synthetic heavy instances (uniform, bimodal, and narrow).
\end{itemize}

\section{Results}
The following plots summarize objective values, runtime, and convergence behavior.

\subsection*{Objective Value}
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Average objective value by solver}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Objective value by instance and solver}
\end{figure}

\subsection*{Runtime}
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Average runtime by solver}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Runtime by instance and solver}
\end{figure}

\subsection*{Convergence}
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Average convergence points by solver}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{%s}
\caption{Convergence points by instance and solver}
\end{figure}

\section{Testing Results}
The test suite runs three groups:
\begin{itemize}
\item Instance 1 $\times$ all solvers
\item All instances $\times$ one solver
\item All instances $\times$ all solvers
\end{itemize}

Each run validates solution feasibility and logs convergence traces.
Outputs are stored in:
\begin{itemize}
\item \texttt{tests/logs/output\_*.log} (per run log)
\item \texttt{tests/logs/solver\_*.log} (raw solver output)
\item \texttt{tests/plots/*.png} (convergence plots)
\end{itemize}

The aggregated results table is extracted from \texttt{reports/solver\_comparison.csv}.

\section{Environment Management with UV}
The project uses \textbf{UV} for dependency management and reproducible execution.
Typical workflow:
\begin{verbatim}
uv sync
uv run python main.py --instance figure_21 --solver ortools
uv run pytest --plot
\end{verbatim}

\section{Full Results Table}
\begin{center}
\scriptsize
\begin{tabular}{llllll}
\hline
Instance & Solver & Status & Max Side & Time (s) & Conv. Points\\
\hline
""" % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        (PLOTS_DIR / "avg_max_side_by_solver.png").as_posix(),
        (PLOTS_DIR / "max_side_by_instance.png").as_posix(),
        (PLOTS_DIR / "avg_time_by_solver.png").as_posix(),
        (PLOTS_DIR / "time_by_instance.png").as_posix(),
        (PLOTS_DIR / "avg_convergence_by_solver.png").as_posix(),
        (PLOTS_DIR / "conv_by_instance.png").as_posix(),
    )

    for r in rows:
        tex += (
            f"{esc_tex(r['instance'])} & {esc_tex(r['solver'])} & {esc_tex(r['status'])} & {esc_tex(r['max_side'])} & {esc_tex(r['time_sec'])} & {esc_tex(r['conv_points'])}\\\\\n"
        )

    tex += r"""\hline
\end{tabular}
\end{center}

\section*{Log Files}
Full log filenames are listed below:
\begin{itemize}
""" 
    for r in rows:
        tex += f"\\item {esc_tex(r['log'])}\n"
    tex += r"""\end{itemize}

\end{document}
"""

    OUT_TEX.write_text(tex, encoding="utf-8")
    print(f"Wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
