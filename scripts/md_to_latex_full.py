#!/usr/bin/env python3
"""Convert full Markdown report to LaTeX, preserving all sections."""

from __future__ import annotations

from pathlib import Path
import re

IN_MD = Path("reports/parking_problem_report.md")
OUT_TEX = Path("reports/parking_problem_report_full.tex")


def esc_tex_text(text: str) -> str:
    return (
        text.replace("&", "\\&")
        .replace("%", "\\%")
        .replace("$", "\\$")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("~", "\\textasciitilde{}")
        .replace("^", "\\textasciicircum{}")
    )


def md_inline_to_tex(line: str) -> str:
    # Inline code `code` (protect from further formatting)
    code_map: list[str] = []

    def _store_code(m: re.Match) -> str:
        code = r"\texttt{" + esc_tex_text(m.group(1)) + r"}"
        token = f"@@CODE{len(code_map)}@@"
        code_map.append(code)
        return token

    line = re.sub(r"`([^`]+)`", _store_code, line)
    # Markdown links [text](url) -> \href{url}{text}
    def _esc_url(url: str) -> str:
        return (
            url.replace("%", r"\%")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("&", r"\&")
        )

    def _repl_link(m: re.Match) -> str:
        url = _esc_url(m.group(2))
        return r"\href{" + url + r"}{\url{" + url + r"}}"

    line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _repl_link, line)
    # Bold **text**
    def _repl_bold(m: re.Match) -> str:
        return r"\textbf{" + esc_tex_text(m.group(1)) + r"}"

    line = re.sub(r"\*\*(.+?)\*\*", _repl_bold, line)
    # Italic *text* (avoid bold already handled)
    def _repl_italic(m: re.Match) -> str:
        return r"\textit{" + esc_tex_text(m.group(1)) + r"}"

    line = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", _repl_italic, line)
    # Restore code segments
    for idx, code in enumerate(code_map):
        line = line.replace(f"@@CODE{idx}@@", code)
    # Convert bare <https://...> into clickable URLs
    line = re.sub(r"<\s*(https?://[^>\s]+)\s*>", r"\\url{\1}", line)
    return line


def escape_preserving_math(line: str) -> str:
    # Preserve \( ... \) and $...$ segments
    parts = re.split(r"(\\\(.*?\\\)|\\\[.*?\\\]|\$.*?\$)", line)
    out = []
    # Preserve selected LaTeX commands we inject
    cmd_pattern = re.compile(
        r"(\\href\{.*?\}\{.*?\}|\\textbf\{.*?\}|\\textit\{.*?\}|\\texttt\{.*?\})"
    )
    for part in parts:
        if part.startswith("\\(") or part.startswith("\\[") or (part.startswith("$") and part.endswith("$")):
            out.append(part)
        else:
            subparts = cmd_pattern.split(part)
            for sub in subparts:
                if cmd_pattern.fullmatch(sub):
                    out.append(sub)
                else:
                    out.append(esc_tex_text(sub))
    return "".join(out)


def convert_table(lines: list[str], idx: int) -> tuple[list[str], int]:
    header = lines[idx].strip()
    sep = lines[idx + 1].strip()
    rows = []
    i = idx
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    # Build tabular
    cols = len(rows[0]) if rows else 0
    tex = ["\\begin{center}", "\\scriptsize", f"\\begin{{tabular}}{{{'l'*cols}}}", "\\hline"]
    if rows:
        tex.append(" & ".join(esc_tex_text(md_inline_to_tex(c)) for c in rows[0]) + r"\\")
        tex.append("\\hline")
        for r in rows[1:]:
            tex.append(" & ".join(esc_tex_text(md_inline_to_tex(c)) for c in r) + r"\\")
    tex.append("\\hline")
    tex.append("\\end{tabular}")
    tex.append("\\end{center}")
    return tex, i


def main() -> None:
    md = IN_MD.read_text(encoding="utf-8")
    lines = md.splitlines()

    out = []
    out.append(r"\documentclass[11pt,a4paper]{article}")
    out.append(r"\usepackage[utf8]{inputenc}")
    out.append(r"\usepackage{amsmath,amssymb}")
    out.append(r"\usepackage{graphicx}")
    out.append(r"\usepackage{url}")
    out.append(r"\usepackage{geometry}")
    out.append(r"\geometry{margin=2.5cm}")
    out.append(r"\Urlmuskip=0mu plus 1mu")
    out.append(r"")
    out.append(r"% Clickable links without hyperref (no extra dependencies)")
    out.append(
        r"\def\href#1#2{\leavevmode\pdfstartlink attr{/Border[0 0 0]} user{/Subtype/Link/A<< /S/URI /URI(\pdfescapestring{#1}) >>}#2\pdfendlink}"
    )
    out.append(r"\def\url#1{\href{#1}{#1}}")
    out.append("")
    out.append(r"\begin{document}")
    out.append(r"\input{reports/cover.tex}")
    out.append(r"\tableofcontents")
    out.append(r"\clearpage")

    i = 0
    in_itemize = False
    in_math_block = False
    front_matter_skipped = False
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if not front_matter_skipped:
            if line.strip() == "---":
                front_matter_skipped = True
            i += 1
            continue

        if in_math_block:
            out.append(line)
            if line.strip() in {"\\]", "$$"}:
                in_math_block = False
            i += 1
            continue

        if line.strip() in {"\\[", "$$"}:
            out.append(line)
            in_math_block = True
            i += 1
            continue

        if line.strip() == "---":
            out.append(r"\hrulefill")
            i += 1
            continue

        # Images: ![alt](path) or ![](path)
        m = re.match(r"!\[(.*?)\]\((.+?)\)", line.strip())
        if m:
            alt = esc_tex_text(m.group(1).strip())
            path = esc_tex_text(m.group(2).strip())
            out.append(r"\begin{center}")
            out.append(rf"\includegraphics[width=0.9\textwidth]{{{path}}}")
            if alt:
                out.append(rf"\par\small\textit{{{alt}}}")
            out.append(r"\end{center}")
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            title = line[2:].strip()
            title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
            out.append(r"\section*{" + esc_tex_text(title) + "}")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
            if title.lower() == "references":
                out.append(r"\clearpage")
            out.append(r"\section{" + esc_tex_text(title) + "}")
            i += 1
            continue
        if line.startswith("### "):
            title = line[4:].strip()
            title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
            out.append(r"\subsection{" + esc_tex_text(title) + "}")
            i += 1
            continue

        # Table
        if line.strip().startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            tex_table, next_i = convert_table(lines, i)
            if in_itemize:
                out.append(r"\\end{itemize}")
                in_itemize = False
            out.extend(tex_table)
            i = next_i
            continue

        # Lists
        if line.startswith("- "):
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            item = md_inline_to_tex(line[2:].strip())
            out.append(r"\item " + escape_preserving_math(item))
            i += 1
            continue
        else:
            if in_itemize and line.strip() == "":
                out.append(r"\end{itemize}")
                in_itemize = False

        # Preserve LaTeX blocks as-is
        if line.strip().startswith("\\[") or line.strip().startswith("$$"):
            out.append(line)
            i += 1
            continue

        # Empty
        if line.strip() == "":
            out.append("")
            i += 1
            continue

        # Normal paragraph
        out.append(escape_preserving_math(md_inline_to_tex(line)))
        out.append("")
        i += 1

    if in_itemize:
        out.append(r"\end{itemize}")

    out.append(r"\end{document}")

    OUT_TEX.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
