#!/usr/bin/env python3
"""Build a lightweight application dashboard from Pipeline.md and role folders."""

from __future__ import annotations

import re
from html import escape
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "Pipeline.md"
OUT_MD = ROOT / "Application Dashboard.md"
OUT_HTML = ROOT / "Application Dashboard.html"


@dataclass
class Role:
    name: str
    stage: str = ""
    next_action: str = ""
    date_text: str = ""
    folder: str = ""
    section: str = ""
    has_jd: bool = False
    has_resume: bool = False
    has_outreach: bool = False
    jd_placeholder: bool = False

    @property
    def missing(self) -> list[str]:
        missing = []
        if not self.has_jd or self.jd_placeholder:
            missing.append("JD")
        if not self.has_resume:
            missing.append("resume")
        if not self.has_outreach:
            missing.append("outreach")
        return missing


def split_markdown_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line.strip("|").split("|")]


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    return text.strip()


def extract_folder(text: str) -> str:
    match = re.search(r"\[\[(.*?)\]\]", text)
    return match.group(1).strip() if match else strip_md(text)


def parse_pipeline() -> list[Role]:
    roles: list[Role] = []
    section = ""
    if not PIPELINE.exists():
        return roles

    for line in PIPELINE.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line.removeprefix("## ").strip()
            continue
        if not line.startswith("| **"):
            continue
        cells = split_markdown_row(line)
        if len(cells) < 6:
            continue
        role, stage, next_action, date_text, _contacts, folder = cells[:6]
        roles.append(
            Role(
                name=strip_md(role),
                stage=strip_md(stage),
                next_action=strip_md(next_action),
                date_text=strip_md(date_text),
                folder=extract_folder(folder),
                section=section,
            )
        )
    return roles


def role_folders() -> set[str]:
    folders = set()
    roles_dir = ROOT / "Roles"
    if not roles_dir.is_dir():
        return folders
    for path in roles_dir.iterdir():
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        if (path / "Job Description.md").exists():
            folders.add(path.name)
    return folders


def is_placeholder_jd(path: Path, role: Role) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    combined = f"{role.stage} {role.next_action}".lower()
    markers = (
        "full jd (paste below)",
        "paste from linkedin",
        "url not surfaced",
        "jd body is empty",
        "linkedin paste pending",
        "capture jd body",
    )
    if any(marker in text for marker in markers):
        return True
    if any(marker in combined for marker in ("capture jd body", "url not surfaced", "paste from linkedin")):
        return True
    return False


def add_artifacts(roles: list[Role]) -> list[Role]:
    by_folder = {role.folder: role for role in roles if role.folder}
    for folder in sorted(role_folders()):
        role = by_folder.get(folder)
        if role is None:
            role = Role(name=folder, folder=folder, section="Untracked folder")
            roles.append(role)
        path = ROOT / "Roles" / folder
        jd_path = path / "Job Description.md"
        role.has_jd = jd_path.exists()
        role.jd_placeholder = jd_path.exists() and is_placeholder_jd(jd_path, role)
        role.has_outreach = (path / "Cold Outreach.md").exists()
        role.has_resume = any(path.glob("Kanu Madhok Resume*.md"))
    return roles


def mentions_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def bucket(role: Role) -> str:
    combined = f"{role.stage} {role.next_action}".lower()
    if role.section == "Untracked folder":
        return "Untracked folder"
    if role.section.startswith("Closed") or mentions_any(combined, ("rejected", "closed", "withdrawn")):
        return "Closed / on hold"
    if mentions_any(combined, ("interview", "panel", "thank-you", "thank you", "today", "due", "awaiting decision")):
        return "Urgent / dated actions"
    if mentions_any(combined, ("filed only", "capture jd body", "url not surfaced", "paste from linkedin")) or role.jd_placeholder:
        return "Filed only / missing JD"
    if role.has_jd and role.has_resume and role.has_outreach and not mentions_any(combined, ("applied", "sent", "await", "waiting")):
        return "Ready to apply + send"
    if role.has_jd and role.has_resume and role.has_outreach:
        return "Prepared / needs human action"
    if len(role.missing) == 1:
        return "One-step blocked"
    if role.has_jd:
        return "Needs prep"
    return "Filed only / missing JD"


def artifact_text(role: Role) -> str:
    bits = [
        "JD placeholder" if role.jd_placeholder else ("JD" if role.has_jd else "JD missing"),
        "resume" if role.has_resume else "resume missing",
        "outreach" if role.has_outreach else "outreach missing",
    ]
    return " · ".join(bits)


def short(text: str, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_table(roles: list[Role]) -> str:
    lines = [
        "| Role | Stage | Artifacts | Next action | Folder |",
        "|---|---|---|---|---|",
    ]
    for role in roles:
        folder = f"[[{role.folder}]]" if role.folder else ""
        lines.append(
            f"| {role.name} | {short(role.stage, 90)} | {artifact_text(role)} | "
            f"{short(role.next_action)} | {folder} |"
        )
    return "\n".join(lines)


def status_class(bucket_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", bucket_name.lower()).strip("-")


def folder_href(role: Role) -> str:
    if not role.folder:
        return ""
    return quote(role.folder) + "/"


def render_html_table(roles: list[Role], bucket_name: str) -> str:
    if not roles:
        return '<p class="empty">None.</p>'
    rows = []
    for role in roles:
        folder = (
            f'<a href="{folder_href(role)}">{escape(role.folder)}</a>'
            if role.folder
            else ""
        )
        rows.append(
            "<tr>"
            f"<td><strong>{escape(role.name)}</strong></td>"
            f"<td>{escape(short(role.stage, 120))}</td>"
            f'<td><span class="pill {status_class(bucket_name)}">{escape(artifact_text(role))}</span></td>'
            f"<td>{escape(short(role.next_action, 260))}</td>"
            f"<td>{folder}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<thead><tr><th>Role</th><th>Stage</th><th>Artifacts</th><th>Next action</th><th>Folder</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def render_html(buckets: dict[str, list[Role]]) -> str:
    today = date.today().isoformat()
    count_cards = "\n".join(
        f'<a class="count-card {status_class(name)}" href="#{status_class(name)}">'
        f"<span>{escape(name)}</span><strong>{len(items)}</strong></a>"
        for name, items in buckets.items()
    )
    sections = "\n".join(
        f'<section id="{status_class(name)}">'
        f"<h2>{escape(name)} <span>{len(items)}</span></h2>"
        f"{render_html_table(items, name)}"
        "</section>"
        for name, items in buckets.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Application Dashboard</title>
  <style>
    :root {{
      --bg: #f7f7f4;
      --panel: #ffffff;
      --text: #1f2933;
      --muted: #667085;
      --line: #d8d6cf;
      --urgent: #9f1d1d;
      --ready: #17643b;
      --prepared: #245b8f;
      --blocked: #8a5a12;
      --filed: #6b7280;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfbf8;
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    h1 {{ margin: 0 0 6px; font-size: 28px; letter-spacing: 0; }}
    .sub {{ margin: 0; color: var(--muted); }}
    main {{ padding: 22px 32px 48px; max-width: 1500px; margin: 0 auto; }}
    .counts {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-bottom: 24px;
    }}
    .count-card {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-left-width: 5px;
      background: var(--panel);
      color: inherit;
      text-decoration: none;
      border-radius: 6px;
    }}
    .count-card strong {{ font-size: 22px; }}
    .urgent-dated-actions {{ border-left-color: var(--urgent); }}
    .ready-to-apply-send {{ border-left-color: var(--ready); }}
    .prepared-needs-human-action {{ border-left-color: var(--prepared); }}
    .one-step-blocked, .needs-prep {{ border-left-color: var(--blocked); }}
    .filed-only-missing-jd, .untracked-folder, .closed-on-hold {{ border-left-color: var(--filed); }}
    section {{
      margin: 18px 0 28px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    h2 {{
      margin: 0;
      padding: 14px 16px;
      font-size: 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfbf8;
    }}
    h2 span {{ color: var(--muted); font-weight: 500; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #eceae4;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      color: var(--muted);
      background: #fcfcfa;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    td:nth-child(1) {{ width: 22%; }}
    td:nth-child(2) {{ width: 20%; color: #344054; }}
    td:nth-child(3) {{ width: 14%; }}
    td:nth-child(4) {{ width: 34%; }}
    td:nth-child(5) {{ width: 10%; }}
    a {{ color: #174ea6; }}
    .pill {{
      display: inline-block;
      padding: 4px 7px;
      border-radius: 999px;
      background: #f2f4f7;
      color: #344054;
      white-space: normal;
    }}
    .empty {{ padding: 14px 16px; color: var(--muted); }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 14px; padding-right: 14px; }}
      table, thead, tbody, tr, th, td {{ display: block; }}
      thead {{ display: none; }}
      tr {{ border-bottom: 1px solid var(--line); padding: 8px 0; }}
      td {{ width: 100% !important; border-bottom: 0; padding: 5px 12px; }}
      td:nth-child(1) {{ font-size: 15px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Application Dashboard</h1>
    <p class="sub">Generated {today} from <code>Pipeline.md</code> and role folders. Work top to bottom.</p>
  </header>
  <main>
    <div class="counts">
      {count_cards}
    </div>
    {sections}
  </main>
</body>
</html>
"""


def main() -> None:
    roles = add_artifacts(parse_pipeline())
    buckets = {
        "Urgent / dated actions": [],
        "Ready to apply + send": [],
        "Prepared / needs human action": [],
        "One-step blocked": [],
        "Needs prep": [],
        "Filed only / missing JD": [],
        "Untracked folder": [],
        "Closed / on hold": [],
    }
    for role in roles:
        buckets.setdefault(bucket(role), []).append(role)

    lines = [
        "# Application Dashboard",
        "",
        f"_Generated {date.today().isoformat()} from `Pipeline.md` and role folders._",
        "",
        "Use this with `Application Operating System.md`. Work top to bottom.",
        "",
        "## Counts",
        "",
        "| Bucket | Count |",
        "|---|---:|",
    ]
    for name, items in buckets.items():
        lines.append(f"| {name} | {len(items)} |")

    for name, items in buckets.items():
        lines.extend(["", f"## {name}", ""])
        if items:
            lines.append(render_table(items))
        else:
            lines.append("_None._")

    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    OUT_HTML.write_text(render_html(buckets), encoding="utf-8")
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
