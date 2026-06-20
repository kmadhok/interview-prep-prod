#!/usr/bin/env python3
"""Verify not-yet-applied job postings from Pipeline.md.

The script parses Kanu Madhok's Interview Prep pipeline, selects roles that have
not been applied to, verifies company ATS/job URLs deterministically over HTTP,
and emits ordered LinkedIn MCP worklists for postings that require authenticated
LinkedIn access.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, build_opener
from urllib.request import HTTPRedirectHandler


ROOT = Path(__file__).resolve().parents[4]
PIPELINE = ROOT / "Pipeline.md"

if not PIPELINE.exists():
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "Pipeline.md"
        if candidate.exists():
            ROOT = parent
            PIPELINE = candidate
            break
    else:
        raise SystemExit(
            "Could not find Pipeline.md from verify_postings.py; "
            f"started at {Path(__file__).resolve()}"
        )


LINKEDIN_JOB_RE = re.compile(
    r"https?://[^\s)\"']*linkedin\.com/jobs/view/(\d+)", re.IGNORECASE
)
ATS_URL_RE = re.compile(
    r"https?://[^\s)\"']*(workday|myworkdayjobs|avature|greenhouse|lever|"
    r"smartrecruiters|icims|eightfold|apply\.deloitte|mckinsey|careers|/jobs|"
    r"/job/)[^\s)\"']*",
    re.IGNORECASE,
)
DEAD_MARKERS = (
    "no longer accepting",
    "no longer available",
    "position has been filled",
    "job not found",
    "this job is closed",
    "not currently accepting",
)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


@dataclass
class Role:
    name: str
    stage: str = ""
    next_action: str = ""
    date_text: str = ""
    folder: str = ""
    section: str = ""


@dataclass
class UrlInfo:
    kind: str
    url: str = ""
    job_id: str = ""


@dataclass
class HttpResult:
    status: str
    http: str
    signal: str
    url: str


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


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
        if line.startswith("### "):
            section = line.removeprefix("### ").strip()
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


def should_verify(role: Role) -> bool:
    section = role.section
    if section != "Considering / not yet applied" and not section.startswith("Bulk-imported"):
        return False
    combined = f"{role.stage} {role.next_action}".lower()
    if "submitted via" in combined:
        return False
    if "applied" in combined and not re.search(r"\b(not yet|not|never)\s+applied\b", combined):
        return False
    return True


def jd_text(role: Role) -> str:
    if not role.folder:
        return ""
    path = ROOT / "Roles" / role.folder / "Job Description.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def clean_url(url: str) -> str:
    return url.rstrip(".,;]")


def extract_url_info(text: str) -> UrlInfo:
    linkedin_match = LINKEDIN_JOB_RE.search(text)
    if linkedin_match:
        return UrlInfo(
            kind="linkedin",
            url=clean_url(linkedin_match.group(0)),
            job_id=linkedin_match.group(1),
        )
    ats_match = ATS_URL_RE.search(text)
    if ats_match:
        return UrlInfo(kind="ats", url=clean_url(ats_match.group(0)))
    return UrlInfo(kind="none")


def truncate(text: str, limit: int = 80) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def find_dead_marker(body: str) -> str:
    lowered = body.lower()
    for marker in DEAD_MARKERS:
        if marker in lowered:
            return marker
    return ""


def request_for(url: str) -> Request:
    return Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )


def header_url(headers: Any, key: str) -> str:
    value = headers.get(key)
    return str(value) if value else ""


def resolve_redirect(current_url: str, location: str) -> str:
    return urljoin(current_url, location)


def fetch_url(url: str, timeout: int = 10, max_redirects: int = 5) -> tuple[int, str, str]:
    opener = build_opener(NoRedirectHandler)
    current_url = url
    for _hop in range(max_redirects + 1):
        try:
            with opener.open(request_for(current_url), timeout=timeout) as response:
                raw = response.read(1_000_000)
                body = raw.decode("utf-8", errors="ignore")
                return response.status, body, response.geturl()
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308}:
                location = header_url(exc.headers, "Location")
                if location:
                    current_url = resolve_redirect(current_url, location)
                    continue
            raw = exc.read(1_000_000)
            body = raw.decode("utf-8", errors="ignore")
            return exc.code, body, exc.geturl()
    raise RuntimeError(f"too many redirects after {max_redirects} hops")


def classify_ats_url(url: str) -> HttpResult:
    try:
        status_code, body, final_url = fetch_url(url)
    except (HTTPError, URLError, TimeoutError, socket.timeout, ssl.SSLError, OSError, RuntimeError) as exc:
        reason = truncate(str(exc))
        return HttpResult(
            status="UNVERIFIED",
            http="",
            signal=f"blocked or error: {reason}",
            url=url,
        )

    marker = find_dead_marker(body)
    if status_code in {404, 410}:
        return HttpResult("DEAD", str(status_code), "HTTP 404/410", final_url)
    if marker:
        return HttpResult("DEAD", str(status_code), marker, final_url)
    if status_code == 200:
        return HttpResult("LIVE", str(status_code), "HTTP 200", final_url)
    if status_code in {401, 403}:
        return HttpResult("UNVERIFIED", str(status_code), f"blocked or error: HTTP {status_code}", final_url)
    return HttpResult("UNVERIFIED", str(status_code), f"blocked or error: HTTP {status_code}", final_url)


def split_company_title(role_name: str) -> tuple[str, str]:
    for delimiter in (" — ", " - "):
        if delimiter in role_name:
            company, title = role_name.split(delimiter, 1)
            return company.strip(), title.strip()
    return role_name.strip(), ""


def short_title(title: str) -> str:
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def linkedin_details_call(job_id: str) -> str:
    return f'mcp__linkedin__get_job_details(job_id="{job_id}")'


def linkedin_search_call(company: str, title: str) -> str:
    keywords = " ".join(part for part in (company, title) if part).strip()
    return f"mcp__linkedin__search_jobs(keywords={json_string(keywords)})"


def table_cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def build_report() -> dict[str, Any]:
    selected = [role for role in parse_pipeline() if should_verify(role)]
    tier1: list[dict[str, str]] = []
    tier2: list[dict[str, str]] = []
    tier3: list[dict[str, str]] = []

    for role in selected:
        info = extract_url_info(jd_text(role))
        if info.kind == "ats":
            result = classify_ats_url(info.url)
            tier1.append(
                {
                    "role": role.name,
                    "status": result.status,
                    "http": result.http,
                    "signal": result.signal,
                    "url": result.url,
                }
            )
            continue
        if info.kind == "linkedin":
            tier2.append(
                {
                    "role": role.name,
                    "job_id": info.job_id,
                    "url": info.url,
                    "mcp_call": linkedin_details_call(info.job_id),
                }
            )
            continue
        company, title = split_company_title(role.name)
        title = short_title(title)
        tier3.append(
            {
                "role": role.name,
                "company": company,
                "title": title,
                "mcp_call": linkedin_search_call(company, title),
            }
        )

    summary = {
        "roles_checked": len(selected),
        "tier1_live": sum(1 for item in tier1 if item["status"] == "LIVE"),
        "tier1_dead": sum(1 for item in tier1 if item["status"] == "DEAD"),
        "tier1_unverified": sum(1 for item in tier1 if item["status"] == "UNVERIFIED"),
        "tier2_linkedin_get_job_details": len(tier2),
        "tier3_linkedin_search": len(tier3),
    }
    return {
        "checked_at": date.today().isoformat(),
        "tier1": tier1,
        "tier2": tier2,
        "tier3": tier3,
        "summary": summary,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# Posting Verification Report — {report['checked_at']}", ""]
    lines.extend(
        [
            "## Tier 1 — ATS/HTTP (verified by this script)",
            "",
            "| Role | Status | HTTP | Signal | URL |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["tier1"]:
        lines.append(
            f"| {table_cell(item['role'])} | {table_cell(item['status'])} | "
            f"{table_cell(item['http'])} | {table_cell(item['signal'])} | "
            f"{table_cell(item['url'])} |"
        )
    if not report["tier1"]:
        lines.append("| _None_ |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Tier 2 — LinkedIn job pages (run these MCP calls, sequentially)",
            "",
            "```python",
        ]
    )
    for item in report["tier2"]:
        lines.append(f"# {item['role']}")
        lines.append(item["mcp_call"])
    lines.extend(
        [
            "```",
            "",
            "## Tier 3 — No captured URL (run these MCP searches, sequentially)",
            "",
            "```python",
        ]
    )
    for item in report["tier3"]:
        lines.append(f"# {item['role']}")
        lines.append(item["mcp_call"])
    lines.extend(["```", "", "## Summary", ""])

    summary = report["summary"]
    lines.extend(
        [
            f"- {summary['roles_checked']} roles checked",
            f"- {summary['tier1_live']} live (tier1)",
            f"- {summary['tier1_dead']} dead (tier1)",
            f"- {summary['tier1_unverified']} unverified (tier1)",
            f"- {summary['tier2_linkedin_get_job_details']} needing LinkedIn get_job_details",
            f"- {summary['tier3_linkedin_search']} needing LinkedIn search",
            "",
            "LinkedIn MCP calls must be run ONE AT A TIME (sequential), never in parallel — see linkedin-mcp-operations skill.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify not-yet-applied postings from Pipeline.md."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the markdown report.",
    )
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    print(render_markdown(report))


if __name__ == "__main__":
    main()
