#!/usr/bin/env python3
"""Convert Markdown to PDF using reportlab (no external system deps)."""

from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
import tempfile
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import re

IN_MD = Path("reports/parking_problem_report.md")
OUT_PDF = Path("reports/parking_problem_report_pretty.pdf")


def _render_math_to_image(expr: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=out_dir)
    try:
        fig = plt.figure()
        fig.text(0.01, 0.5, f"${expr}$", fontsize=12)
        fig.patch.set_alpha(0.0)
        fig.savefig(tmp.name, dpi=200, bbox_inches="tight", pad_inches=0.05, transparent=True)
        plt.close(fig)
        return Path(tmp.name)
    except Exception:
        # Fallback: render as plain text without LaTeX
        clean = expr
        clean = clean.replace("\\\\", "\n")
        clean = clean.replace("\\begin{cases}", "")
        clean = clean.replace("\\end{cases}", "")
        clean = clean.replace("\\text{", "").replace("}", "")
        clean = clean.replace("\\lambda", "lambda")
        clean = clean.replace("\\sum", "sum")
        clean = clean.replace("\\le", "<=")
        clean = clean.replace("\\ge", ">=")
        clean = clean.replace("\\forall", "forall")
        clean = clean.replace("\\in", "in")
        fig = plt.figure()
        fig.text(0.01, 0.5, clean, fontsize=11)
        fig.patch.set_alpha(0.0)
        fig.savefig(tmp.name, dpi=200, bbox_inches="tight", pad_inches=0.05, transparent=True)
        plt.close(fig)
        return Path(tmp.name)


def _preprocess_markdown(text: str) -> list[str]:
    def block_math_repl(match):
        expr = match.group(1).strip().replace("\n", " ")
        return f"\n[[BLOCK_MATH:{expr}]]\n"

    text = re.sub(r"\\\[(.*?)\\\]", block_math_repl, text, flags=re.DOTALL)
    text = re.sub(r"\$\$(.*?)\$\$", block_math_repl, text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"[[INLINE_MATH:\1]]", text)
    return text.splitlines()


def parse_markdown(lines: list[str]):
    styles = getSampleStyleSheet()
    flow = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if line.strip() == "":
            flow.append(Spacer(1, 8))
            i += 1
            continue

        # Block math token
        if line.strip().startswith("[[BLOCK_MATH:") and line.strip().endswith("]]"):
            expr = line.strip()[13:-2].strip()
            img = _render_math_to_image(expr, Path("reports/plots"))
            flow.append(Image(str(img), width=400, height=40))
            flow.append(Spacer(1, 8))
            i += 1
            continue

        # Table detection
        if line.strip().startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
            tbl = Table(rows, repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            flow.append(tbl)
            flow.append(Spacer(1, 8))
            continue

        # Headings
        if line.startswith("### "):
            flow.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith("## "):
            flow.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("# "):
            flow.append(Paragraph(line[2:], styles["Heading1"]))
        elif line.startswith("- "):
            flow.append(Paragraph(f"• {line[2:]}", styles["BodyText"]))
        else:
            parts = re.split(r"(\[\[INLINE_MATH:.*?\]\])", line)
            for part in parts:
                if part.startswith("[[INLINE_MATH:") and part.endswith("]]"):
                    expr = part[14:-2].strip()
                    if expr:
                        img = _render_math_to_image(expr, Path("reports/plots"))
                        flow.append(Image(str(img), width=120, height=20))
                else:
                    if part.strip():
                        flow.append(Paragraph(part, styles["BodyText"]))

        i += 1

    return flow


def main() -> None:
    text = IN_MD.read_text(encoding="utf-8")
    lines = _preprocess_markdown(text)
    flow = parse_markdown(lines)

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    doc.build(flow)
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
