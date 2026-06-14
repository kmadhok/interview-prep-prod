#!/usr/bin/env python3
"""Export a tailored resume markdown to a one-page PDF + editable DOCX.

Pipeline: md --pandoc--> styled HTML --headless Chrome--> PDF, and md --pandoc--> DOCX.
Auto-tightens font/margin until the rendered content fits one US-Letter page,
stopping at a 9pt readability floor. Prints OVERFLOW if it can't fit at 9pt.

Usage:
    python3 export_resume.py "/abs/path/Kanu Madhok Resume - X.md"

Degrades gracefully: missing pandoc/Chrome => prints a SKIP line and exits 0,
so the caller (jd-to-ready step 3.5) records a gap instead of failing the run.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

# (font_pt, margin_in, line_height, h2top, h3top, ul_margin, li_margin) tiers:
# comfortable -> tightest readable floor (9pt). The 9pt floor matches the
# hand-verified one-page render (lh 1.15, h2top 6, li 1.5).
TIERS = [
    (10.5, 0.55, 1.32, 10, 6, 3, 3),
    (10.0, 0.50, 1.28, 9, 5, 3, 2.5),
    (9.5, 0.45, 1.24, 8, 5, 2.5, 2.5),
    (9.25, 0.42, 1.20, 7, 4.5, 2, 2),
    (9.0, 0.40, 1.15, 6, 3.5, 1.5, 1.5),
]

CSS_TMPL = """
@page {{ size: letter; margin: {margin}in; }}
body {{ font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
        font-size: {fs}pt; line-height: {lh}; color: #1a1a1a; }}
h1 {{ font-size: {h1}pt; margin: 0 0 0 0; }}
h2 {{ font-size: {h2}pt; text-transform: uppercase; letter-spacing: 0.3px;
      border-bottom: 1px solid #999; padding-bottom: 1px; margin: {h2top}pt 0 2pt 0; }}
h3 {{ font-size: {fs}pt; margin: {h3top}pt 0 0 0;
      display: flex; justify-content: space-between; align-items: baseline; gap: 8pt; }}
h3 .org {{ font-weight: 700; min-width: 0; }}
h3 .meta {{ font-weight: 400; color: #555; white-space: nowrap; flex: 0 0 auto; }}
h1 {{ text-align: center; }}
ul {{ margin: {ulm}pt 0; padding-left: 13pt; }}
li {{ margin-bottom: {lim}pt; }}
p {{ margin: 0.5pt 0; }}
em {{ color: #555; }}
a {{ color: #1a1a1a; text-decoration: none; }}
hr {{ display: none; }}
"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def page_budget_px(margin_in):
    # US Letter 11in tall @96dpi = 1056px; subtract top+bottom margins.
    return int(1056 - 2 * margin_in * 96) - 8  # 8px safety


def _split_h3_columns(html):
    """Wrap company-header h3 inner text into left (.org) / right (.meta) columns.

    Each h3 looks like `Org [— Sub-org] — City, ST · Date`. The right column is
    the final ` — `-delimited segment (the City · Date meta); the left column is
    everything before it. Defensive: only rewraps when the split yields 2 parts
    AND the right part contains the ` · ` meta separator, so non-matching h3s
    (and any with an embedded newline) pass through untouched.
    """
    SPLIT = " — "  # space + em-dash + space
    DOT = " · "    # space + middle-dot + space

    def repl(m):
        open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
        if "\n" in inner:
            return m.group(0)
        parts = inner.rsplit(SPLIT, 1)
        if len(parts) != 2 or DOT not in parts[1]:
            return m.group(0)
        left, right = parts
        return (f'{open_tag}<span class="org">{left}</span>'
                f'<span class="meta">{right}</span>{close_tag}')

    return re.sub(r'(<h3\b[^>]*>)(.*?)(</h3>)', repl, html, flags=re.DOTALL)


def render_html(md_path, css, tmp):
    html_path = os.path.join(tmp, "resume.html")
    # strip the internal editor-note line; it's not resume content
    clean = os.path.join(tmp, "clean.md")
    with open(md_path, encoding="utf-8") as f:
        body = "".join(
            l for l in f
            if "_Text source for the .docx" not in l and "right-aligned" not in l
        )
    with open(clean, "w", encoding="utf-8") as f:
        f.write(body)
    subprocess.run(
        ["pandoc", clean, "-s", "--wrap=none", "-o", html_path],
        check=True,
    )
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    html = _split_h3_columns(html)
    html = html.replace("</head>", f"<style>{css}</style></head>")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path, clean


def measure_px(chrome, html_path, tmp):
    meas = os.path.join(tmp, "measure.html")
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    inject = ('<script>window.addEventListener("load",function(){'
              'document.title="H:"+document.body.scrollHeight;});</script>')
    with open(meas, "w", encoding="utf-8") as f:
        f.write(html.replace("</head>", inject + "</head>"))
    out = subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--virtual-time-budget=2000",
         "--dump-dom", f"file://{meas}"],
        capture_output=True, text=True,
    ).stdout
    m = re.search(r"H:(\d+)", out)
    return int(m.group(1)) if m else 10**9


def main():
    if len(sys.argv) < 2:
        print("usage: export_resume.py <resume.md>", file=sys.stderr)
        return 2
    md = sys.argv[1]
    if not os.path.exists(md):
        print(f"SKIP: not found: {md}", file=sys.stderr)
        return 2
    if not shutil.which("pandoc"):
        print("SKIP: pandoc missing; .md only, no PDF/DOCX")
        return 0
    chrome = find_chrome()
    base = os.path.splitext(md)[0]

    # DOCX always (pandoc-only).
    with tempfile.TemporaryDirectory() as tmp:
        clean = os.path.join(tmp, "clean.md")
        with open(md, encoding="utf-8") as f:
            body = "".join(
                l for l in f
                if "_Text source for the .docx" not in l and "right-aligned" not in l
            )
        with open(clean, "w", encoding="utf-8") as f:
            f.write(body)
        subprocess.run(["pandoc", clean, "-o", base + ".docx"], check=True)
    print(f"DOCX: {base}.docx")

    if not chrome:
        print("SKIP-PDF: no Chrome; DOCX written, no PDF")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        chosen = None
        for fs, margin, lh, h2top, h3top, ulm, lim in TIERS:
            css = CSS_TMPL.format(margin=margin, fs=fs, lh=lh,
                                  h1=fs + 7, h2=fs + 0.5, h2top=h2top,
                                  h3top=h3top, ulm=ulm, lim=lim)
            html_path, _ = render_html(md, css, tmp)
            h = measure_px(chrome, html_path, tmp)
            budget = page_budget_px(margin)
            if h <= budget:
                chosen = (fs, margin, html_path, h, budget)
                break
            last = (fs, margin, html_path, h, budget)
        if chosen is None:
            chosen = last  # tightest tier; will overflow
        fs, margin, html_path, h, budget = chosen
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={base}.pdf", f"file://{html_path}"],
            capture_output=True,
        )
        with open(base + ".pdf", "rb") as f:
            pages = len(re.findall(rb"/Type\s*/Page[^s]", f.read()))
        print(f"PDF: {base}.pdf  (font={fs}pt margin={margin}in pages={pages})")
        if pages > 1:
            # Actual Chrome pagination is the source of truth, not the px estimate
            # (which carries an 8px safety margin and can read "over" while still
            # fitting one page).
            print(f"OVERFLOW: {pages}-page PDF at {fs}pt floor "
                  f"(content {h}px vs {budget}px budget). "
                  f"Trim a bullet to fit one page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
