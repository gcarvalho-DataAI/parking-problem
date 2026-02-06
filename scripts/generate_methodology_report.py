#!/usr/bin/env python3
"""Generate full methodology PDF report for the framework."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PLOTS_DIR = Path("reports/plots")
OUT_PDF = Path("reports/methodology_report.pdf")


def draw_wrapped_text(c, text, x, y, width, leading=14):
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test) <= width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def add_image(c, img_path: Path, x, y, w):
    if not img_path.exists():
        return y
    img = ImageReader(str(img_path))
    iw, ih = img.getSize()
    h = w * (ih / iw)
    c.drawImage(img, x, y - h, w, h, preserveAspectRatio=True, mask="auto")
    return y - h - 10


def section(c, title, y):
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, title)
    return y - 16


def main() -> None:
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PDF), pagesize=A4)
    width, height = A4

    # Cover
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, height - 2 * cm, "Parking Problem Framework – Methodology Report")
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 2.8 * cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = height - 4 * cm
    c.setFont("Helvetica", 11)
    intro = (
        "This report documents the methodology used to design, implement, and validate a solver framework "
        "for the Parking Problem (2-partition / 2-bin packing). It covers theoretical background, dataset "
        "selection and generation, mathematical modeling, solver integration, and testing protocol."
    )
    y = draw_wrapped_text(c, intro, 2 * cm, y, width - 4 * cm)
    c.showPage()

    # Theoretical background
    y = height - 2 * cm
    y = section(c, "Theoretical Background", y)
    c.setFont("Helvetica", 11)
    text = (
        "The Parking Problem can be formulated as a 2-partition (or 2-bin packing) problem: divide item lengths "
        "into two sets to minimize the maximum subset sum. This is a classic NP-complete problem; exact methods "
        "are typically modeled as mixed-integer programming or constraint programming."
    )
    y = draw_wrapped_text(c, text, 2 * cm, y, width - 4 * cm)

    # Methodology
    y -= 8
    y = section(c, "Framework Methodology", y)
    c.setFont("Helvetica", 11)
    bullets = [
        "Define a common data model (length list + solution structure).",
        "Implement separate solver backends (OR-Tools CP-SAT, PuLP/CBC, Pyomo/HiGHS).",
        "Normalize output: objective value, partition assignment, and basic validation.",
        "Centralize solver selection via a facade (solver_main).",
        "Add validation for data integrity and solution correctness.",
    ]
    for b in bullets:
        y = draw_wrapped_text(c, f"- {b}", 2 * cm, y, width - 4 * cm)

    # Datasets
    y -= 8
    y = section(c, "Datasets: Selection and Generation", y)
    c.setFont("Helvetica", 11)
    text = (
        "Three dataset classes were used: (1) provided instance (Figure 2.1), (2) adapted instances from 1D bin packing lists, "
        "and (3) synthetic heavy instances to stress solvers. Synthetic instances were generated with different distributions: "
        "uniform, bimodal, and narrow-range (near-equal) to test sensitivity to variance and instance difficulty."
    )
    y = draw_wrapped_text(c, text, 2 * cm, y, width - 4 * cm)

    # Modeling
    y -= 8
    y = section(c, "Mathematical Model", y)
    c.setFont("Helvetica", 11)
    model_text = (
        "Decision variable x_i in {0,1} assigns car i to side A. Objective minimizes L such that sum_A <= L and sum_B <= L. "
        "This captures the minimization of the maximum occupied street length between two sides."
    )
    y = draw_wrapped_text(c, model_text, 2 * cm, y, width - 4 * cm)

    # Solvers
    y -= 8
    y = section(c, "Solvers and Rationale", y)
    c.setFont("Helvetica", 11)
    solvers = [
        "OR-Tools CP-SAT: fast for small/medium instances, strong presolve and search heuristics.",
        "PuLP/CBC: open-source MILP with detailed B&B logs; slower on large instances but rich convergence data.",
        "Pyomo + HiGHS: efficient LP/MIP backend with good performance and stable results; logs less granular.",
    ]
    for s in solvers:
        y = draw_wrapped_text(c, f"- {s}", 2 * cm, y, width - 4 * cm)

    c.showPage()

    # Testing
    y = height - 2 * cm
    y = section(c, "Testing Protocol", y)
    c.setFont("Helvetica", 11)
    test_text = (
        "Tests are organized in three groups: (i) one instance across all solvers, (ii) all instances with a single solver, "
        "and (iii) all instances across all solvers. Each run validates solution feasibility and logs execution metadata."
    )
    y = draw_wrapped_text(c, test_text, 2 * cm, y, width - 4 * cm)

    # Convergence & logging
    y -= 8
    y = section(c, "Convergence Logging", y)
    c.setFont("Helvetica", 11)
    conv_text = (
        "Each run writes a log with solution, timing, and convergence points. For CBC, convergence is parsed from branch-and-bound logs. "
        "For OR-Tools, convergence is inferred from solver search logs. For HiGHS, convergence is typically only the final point."
    )
    y = draw_wrapped_text(c, conv_text, 2 * cm, y, width - 4 * cm)

    # Plots
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Plots")
    y = height - 3 * cm
    y = add_image(c, PLOTS_DIR / "time_by_instance.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "max_side_by_instance.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "conv_by_instance.png", 2 * cm, y, width - 4 * cm)

    c.save()
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
