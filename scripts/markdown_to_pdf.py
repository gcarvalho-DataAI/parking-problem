#!/usr/bin/env python3
"""Convert Markdown to a styled PDF using xhtml2pdf."""

from __future__ import annotations

from pathlib import Path
import markdown
from xhtml2pdf import pisa

IN_MD = Path("reports/parking_problem_report.md")
OUT_PDF = Path("reports/parking_problem_report_pretty.pdf")

CSS = """
body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; }
h1 { font-size: 20pt; }
h2 { font-size: 16pt; }
h3 { font-size: 13pt; }
hr { margin: 12pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
th, td { border: 1px solid #999; padding: 4px; }
code { font-family: Courier, monospace; font-size: 9pt; }
"""


def main() -> None:
    text = IN_MD.read_text(encoding="utf-8")
    html_body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = f"""
    <html>
      <head>
        <style>{CSS}</style>
      </head>
      <body>
        {html_body}
      </body>
    </html>
    """

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PDF.open("wb") as f:
        pisa.CreatePDF(html, dest=f)

    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
