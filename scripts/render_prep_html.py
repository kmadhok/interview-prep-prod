#!/usr/bin/env python3
"""Render selected prep .md files into self-contained, styled .html.

Why HTML *and* .md: GitHub renders .md natively in the repo view but shows
raw .html as source. These HTML files are for local viewing and are
GitHub Pages-ready (drop them under /docs or a gh-pages branch to serve them).

Usage:
    python3 scripts/render_prep_html.py "path/one.md" "path/two.md" ...
If no args, renders the default BCG round-2 prep set.
"""
import sys, pathlib, markdown

CSS = """
:root { --ink:#1a1a1a; --bcg:#177b4b; --bcg-dark:#0f5e39; --muted:#5b6470;
        --line:#e3e8ee; --bg:#ffffff; --soft:#f5f8fb; --accent:#1A6FB3; }
* { box-sizing: border-box; }
body { font-family:-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif;
       color:var(--ink); line-height:1.62; max-width:860px; margin:0 auto;
       padding:48px 28px 96px; background:var(--bg); font-size:16px; }
h1 { font-size:30px; line-height:1.2; letter-spacing:-0.4px; margin:0 0 18px;
     padding-bottom:14px; border-bottom:3px solid var(--bcg); }
h2 { font-size:21px; margin:38px 0 12px; padding-top:14px; border-top:1px solid var(--line);
     letter-spacing:-0.2px; }
h3 { font-size:17px; margin:26px 0 8px; color:var(--bcg-dark); }
h2:first-of-type { border-top:none; padding-top:0; }
p, li { font-size:15.5px; }
a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
strong { color:var(--ink); }
ul, ol { padding-left:24px; } li { margin:4px 0; }
code { background:var(--soft); border:1px solid var(--line); border-radius:4px;
       padding:1px 5px; font-family:"SF Mono",Menlo,Consolas,monospace; font-size:13px; }
pre { background:var(--soft); border:1px solid var(--line); border-radius:8px;
      padding:14px 16px; overflow:auto; } pre code { border:none; background:none; padding:0; }
blockquote { margin:16px 0; padding:12px 18px; background:var(--soft);
             border-left:4px solid var(--bcg); border-radius:0 8px 8px 0; }
blockquote p { margin:6px 0; }
table { border-collapse:collapse; width:100%; margin:18px 0; font-size:14px; }
th, td { border:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top; }
th { background:var(--bcg); color:#fff; font-weight:600; }
tr:nth-child(even) td { background:var(--soft); }
hr { border:none; border-top:1px solid var(--line); margin:30px 0; }
em { color:var(--muted); }
@media (max-width:600px){ body{padding:28px 16px 64px;font-size:15px;} h1{font-size:24px;} }
"""

DEFAULTS = [
    "BCG X - Senior AI Factory Product Builder/Resume Deep-Dive Question Bank - Patrick Freyer.md",
    "BCG X - Senior AI Factory Product Builder/Round 2 Prep Plan - Patrick Freyer.md",
]

def render(md_path: pathlib.Path):
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "toc"])
    title = md_path.stem
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title><style>{CSS}</style></head>
<body>{body}</body></html>"""
    out = md_path.with_suffix(".html")
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} bytes)")

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    args = sys.argv[1:] or DEFAULTS
    for a in args:
        p = pathlib.Path(a)
        if not p.is_absolute():
            p = root / a
        if p.exists():
            render(p)
        else:
            print(f"SKIP (not found): {p}")

if __name__ == "__main__":
    main()
