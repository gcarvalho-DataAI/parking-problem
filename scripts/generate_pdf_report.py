#!/usr/bin/env python3
"""Generate PDF report with solver comparison and plots."""

from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

CSV_PATH = Path("reports/solver_comparison.csv")
PLOTS_DIR = Path("reports/plots")
OUT_PDF = Path("reports/solver_report.pdf")


def read_csv():
    rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


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


def main() -> None:
    rows = read_csv()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(OUT_PDF), pagesize=A4)
    width, height = A4

    # Title page
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, height - 2 * cm, "Parking Problem – Solver Comparison Report")
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 2.8 * cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 4 * cm
    c.setFont("Helvetica", 11)
    intro = (
        "This report compares open-source solvers for the 2-partition (bin packing with 2 bins) "
        "model of the Parking Problem. Metrics include total solve time, objective value (max side), "
        "and convergence points extracted from solver logs."
    )
    y = draw_wrapped_text(c, intro, 2 * cm, y, width - 4 * cm)

    c.showPage()

    # Solver explanations
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Solvers and Observations")
    c.setFont("Helvetica", 11)
    y = height - 3 * cm

    sections = [
        (
            "OR-Tools (CP-SAT)",
            "Constraint programming with SAT + LP relaxations. Typically very fast on small/medium instances. "
            "Can return different optimal partitions if multiple optima exist. Logs show internal search progress."
        ),
        (
            "PuLP (CBC)",
            "Mixed-integer linear programming using CBC. Produces detailed branch-and-bound logs with many convergence points, "
            "but can be much slower on large instances."
        ),
        (
            "Pyomo + HiGHS",
            "Modeling layer using HiGHS as backend. Usually fast and stable, but logs are less detailed; convergence points "
            "are often just final results."
        ),
    ]

    for title, body in sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, title)
        y -= 14
        c.setFont("Helvetica", 11)
        y = draw_wrapped_text(c, body, 2 * cm, y, width - 4 * cm)
        y -= 6

    c.showPage()

    # Summary plots
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Aggregate Results")
    y = height - 3 * cm
    y = add_image(c, PLOTS_DIR / "avg_time_by_solver.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "avg_convergence_by_solver.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "avg_max_side_by_solver.png", 2 * cm, y, width - 4 * cm)

    c.showPage()

    # Per-instance plots
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Per-Instance Comparison")
    y = height - 3 * cm
    y = add_image(c, PLOTS_DIR / "time_by_instance.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "max_side_by_instance.png", 2 * cm, y, width - 4 * cm)
    y = add_image(c, PLOTS_DIR / "conv_by_instance.png", 2 * cm, y, width - 4 * cm)

    c.showPage()

    # Data table (first N rows)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Raw Results (excerpt)")
    c.setFont("Helvetica", 9)
    y = height - 3 * cm
    header = ["instance", "solver", "status", "max_side", "time_sec", "conv_points"]
    c.drawString(2 * cm, y, " | ".join(header))
    y -= 12
    for r in rows[:30]:
        line = " | ".join(r[k] for k in header)
        c.drawString(2 * cm, y, line[:120])
        y -= 11
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 9)

    c.save()
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
