#!/usr/bin/env python3
"""Regenerate Pipeline.html from Pipeline.md.

Usage:
    python3 scripts/render_pipeline.py [path-to-Pipeline.md] [path-to-Pipeline.html]

Defaults to ../Pipeline.md and ../Pipeline.html (relative to this script).
Per `feedback_html_regen.md`, run this any time Pipeline.md changes.
"""
from __future__ import annotations
import html
import re
import sys
from pathlib import Path

from config import WORKSPACE, load_profile


SECTION_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)
UPDATED_RE = re.compile(r"^_Last updated:\s*(?P<value>.+?)_(?:\s+_(?P<note>.+?)_)?\s*$", re.MULTILINE)


def split_sections(md: str) -> dict:
    sections: dict = {}
    matches = list(SECTION_RE.finditer(md))
    for i, m in enumerate(matches):
        title = m.group("title").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        sections[title] = md[start:end].strip()
    return sections


def parse_this_week(body: str) -> list:
    items: list = []
    current: list = []
    for line in body.splitlines():
        if line.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
                current = []
            current.append(line[2:].strip())
        elif line.startswith("  ") and current:
            current.append(line.strip())
        elif line.strip() == "":
            if current:
                items.append(" ".join(current).strip())
                current = []
        elif line.startswith("---"):
            break
        elif current:
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    return items


def parse_table(body: str) -> list:
    lines = [ln for ln in body.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [c.strip() for c in lines[0].strip().strip("|").split("|")]
    rows: list = []
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append({h: c for h, c in zip(headers, cells)})
    return rows


def md_inline(text: str) -> str:
    code_spans: list = []
    def stash_code(m):
        code_spans.append(m.group(1))
        return "\x00CODE{}\x00".format(len(code_spans) - 1)
    text = re.sub(r"`([^`]+)`", stash_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[\[([^\]]+)\]\]", lambda m: "<code>{}/</code>".format(m.group(1)), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: '<a href="{}">{}</a>'.format(m.group(2), m.group(1)), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", text)
    def restore(m):
        idx = int(m.group(1))
        return "<code>{}</code>".format(html.escape(code_spans[idx], quote=False))
    text = re.sub(r"\x00CODE(\d+)\x00", restore, text)
    return text


def stage_chip_class(stage_text: str) -> str:
    s = stage_text.lower()
    if "offer" in s:
        return "stage-offer"
    if "closed" in s or "withdrawn" in s or "rejected" in s or "ghosted" in s:
        return "stage-closed"
    if "panel" in s or "advanced" in s or "interview" in s or "scheduled" in s or "complete" in s:
        return "stage-panel"
    if "screen" in s or "applied" in s or "considering" in s:
        return "stage-screen"
    return ""


def split_company_role(role_md: str):
    cleaned = re.sub(r"^\*\*|\*\*$", "", role_md.strip())
    for sep in [" — ", " – ", " - "]:
        if sep in cleaned:
            company, _, role = cleaned.partition(sep)
            return company.strip(), role.strip()
    return cleaned.strip(), ""


def render_card(row: dict) -> str:
    company, role = split_company_role(row.get("Role", ""))
    stage = row.get("Stage", "").strip()
    next_action = row.get("Next action", "").strip()
    date = row.get("Date", "").strip()
    contacts = row.get("Contacts", "").strip()
    folder = row.get("Folder", "").strip()

    folder_html = md_inline(folder) if folder else ""

    contact_parts = [p.strip() for p in re.split(r"\s+·\s+", contacts) if p.strip()]
    if len(contact_parts) <= 1:
        contacts_value = md_inline(contacts) if contacts else "<span class='empty'>TBD</span>"
    else:
        items = "".join("<li>{}</li>".format(md_inline(p)) for p in contact_parts)
        contacts_value = "<ul>{}</ul>".format(items)

    chip_class = stage_chip_class(stage)
    chip_html = '<span class="chip {}">{}</span>'.format(chip_class, md_inline(stage)) if stage else ""

    return """
    <div class="card">
      <div class="top">
        <div>
          <div class="role">{role}</div>
          <div class="company">{company}</div>
        </div>
        {chip}
      </div>
      <div class="grid">
        <div class="field" style="grid-column: 1 / -1;">
          <div class="label">Next action</div>
          <div class="value">{na}</div>
        </div>
        <div class="field" style="grid-column: 1 / -1;">
          <div class="label">Date / timeline</div>
          <div class="value date">{date}</div>
        </div>
        <div class="field" style="grid-column: 1 / -1;">
          <div class="label">Contacts</div>
          <div class="value contacts">{contacts}</div>
        </div>
      </div>
      <div class="folder-link">Folder: {folder}</div>
    </div>
    """.format(
        role=md_inline(role) or md_inline(company),
        company=md_inline(company) if role else "",
        chip=chip_html,
        na=md_inline(next_action),
        date=md_inline(date),
        contacts=contacts_value,
        folder=folder_html,
    ).strip()


CSS = """
:root {
  --bg: #0f1115; --panel: #171a21; --panel-2: #1d2129; --border: #2a2f3a;
  --text: #e6e8ee; --muted: #9aa3b2; --accent: #f59e0b;
  --accent-soft: rgba(245, 158, 11, 0.12);
  --green: #34d399; --blue: #60a5fa; --red: #f87171; --chip-bg: #232836;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f7f7f8; --panel: #ffffff; --panel-2: #fafbfc; --border: #e4e6ea;
    --text: #1a1d24; --muted: #5b6373; --accent: #b45309;
    --accent-soft: rgba(180, 83, 9, 0.10);
    --green: #047857; --blue: #1d4ed8; --red: #b91c1c; --chip-bg: #eef0f4;
  }
}
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.5; padding: 32px 24px 80px; }
.wrap { max-width: 1080px; margin: 0 auto; }
header { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap;
         gap: 12px; margin-bottom: 28px; }
h1 { font-size: 28px; margin: 0; letter-spacing: -0.01em; }
.updated { color: var(--muted); font-size: 13px; text-align: right; }
.updated .note { display: block; font-style: italic; margin-top: 2px; max-width: 600px; }
h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted);
     margin: 32px 0 12px; font-weight: 600; }
.banner { background: var(--accent-soft); border: 1px solid var(--accent); border-left: 4px solid var(--accent);
          border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; font-size: 14px; }
.banner strong { color: var(--accent); }
.banner code { background: rgba(0,0,0,0.15); padding: 1px 5px; border-radius: 4px; font-size: 12px; }
.cards { display: grid; gap: 14px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; }
.card .top { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 10px; }
.card .role { font-size: 17px; font-weight: 600; }
.card .company { color: var(--muted); font-size: 13px; margin-top: 2px; }
.chip { display: inline-block; background: var(--chip-bg); color: var(--text); font-size: 12px;
        font-weight: 500; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.chip.stage-panel { background: var(--accent-soft); color: var(--accent); }
.chip.stage-screen { background: rgba(96, 165, 250, 0.15); color: var(--blue); }
.chip.stage-offer { background: rgba(52, 211, 153, 0.15); color: var(--green); }
.chip.stage-closed { background: rgba(248, 113, 113, 0.15); color: var(--red); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; margin-top: 12px; }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
.field .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 4px; }
.field .value { font-size: 14px; }
.field .value.date { font-weight: 600; font-variant-numeric: tabular-nums; }
.contacts li { margin: 2px 0; font-size: 14px; }
.contacts ul { margin: 0; padding-left: 16px; }
.folder-link { margin-top: 14px; font-size: 13px; color: var(--muted); }
.folder-link code { background: var(--chip-bg); padding: 2px 6px; border-radius: 4px; font-size: 12px; }
footer { margin-top: 40px; font-size: 12px; color: var(--muted); border-top: 1px solid var(--border); padding-top: 16px; }
.empty { color: var(--muted); font-style: italic; font-size: 14px; }
""".strip()


def render(md: str) -> str:
    h1_m = H1_RE.search(md)
    title = h1_m.group("title").strip() if h1_m else "Job Application Pipeline"

    upd_m = UPDATED_RE.search(md)
    updated_value = upd_m.group("value").strip() if upd_m else ""
    updated_note = upd_m.group("note").strip() if upd_m and upd_m.group("note") else ""

    sections = split_sections(md)

    this_week_items = parse_this_week(sections.get("This week", ""))
    banners_html = "\n".join('<div class="banner">{}</div>'.format(md_inline(it)) for it in this_week_items)

    active_rows = parse_table(sections.get("Active", ""))
    active_html = "\n".join(render_card(r) for r in active_rows) or '<p class="empty">None.</p>'

    considering_rows = parse_table(sections.get("Considering / not yet applied", ""))
    considering_html = "\n".join(render_card(r) for r in considering_rows) or '<p class="empty">None.</p>'

    closed_body = sections.get("Closed / On hold", "").strip()
    if not closed_body or closed_body.lower().startswith("_none"):
        closed_html = '<p class="empty">None yet.</p>'
    else:
        closed_rows = parse_table(closed_body)
        if closed_rows:
            closed_html = "\n".join(render_card(r) for r in closed_rows)
        else:
            closed_html = "<p>{}</p>".format(md_inline(closed_body))

    updated_html = ""
    if updated_value:
        note_html = '<span class="note">{}</span>'.format(md_inline(updated_note)) if updated_note else ""
        updated_html = '<div class="updated">Last updated: {}{}</div>'.format(html.escape(updated_value), note_html)

    owner = load_profile()["user_name"]
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{title} — {owner}</title>
<style>
{css}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <h1>{title}</h1>
    {updated}
  </header>

  <h2>This week</h2>
  {banners}

  <h2>Active</h2>
  <div class="cards">
    {active}
  </div>

  <h2>Considering / not yet applied</h2>
  <div class="cards">
    {considering}
  </div>

  <h2>Closed / On hold</h2>
  {closed}

  <footer>
    Source of truth is <code>Pipeline.md</code>. This HTML is auto-regenerated by
    <code>scripts/render_pipeline.py</code> on every Pipeline.md edit (see
    <code>feedback_html_regen.md</code> in memory).
  </footer>

</div>
</body>
</html>
""".format(
        title=html.escape(title),
        owner=html.escape(owner),
        css=CSS,
        updated=updated_html,
        banners=banners_html or '<p class="empty">Nothing flagged.</p>',
        active=active_html,
        considering=considering_html,
        closed=closed_html,
    )


def main(argv):
    default_md = WORKSPACE / "Pipeline.md"
    default_html = WORKSPACE / "Pipeline.html"

    md_path = Path(argv[1]) if len(argv) > 1 else default_md
    html_path = Path(argv[2]) if len(argv) > 2 else default_html

    if not md_path.exists():
        print("error: source not found: {}".format(md_path), file=sys.stderr)
        return 1

    md = md_path.read_text(encoding="utf-8")
    out = render(md)
    html_path.write_text(out, encoding="utf-8")
    print("wrote {} ({:,} bytes)".format(html_path, len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
