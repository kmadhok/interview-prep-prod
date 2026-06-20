#!/usr/bin/env python3
"""Verify recruiter emails from a role contacts ledger.

The script parses a role's `.contacts-ledger.md`, selects the top ranked
recruiters, resolves SMTP-verified emails through EmailFinder.dev's person
endpoint, caches paid results, and writes a `## Verified Emails` block back to
the ledger.

Usage:
  python3 verify_emails.py --ledger "Roles/Company - Role/.contacts-ledger.md"
  python3 verify_emails.py --ledger "Roles/Company - Role/.contacts-ledger.md" --emails-md-default
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import ssl
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler
from urllib.request import Request, build_opener


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
            "Could not find Pipeline.md from verify_emails.py; "
            f"started at {Path(__file__).resolve()}"
        )


BASE_URL = "https://www.emailfinder.dev"
CACHE_PATH = ROOT / ".claude" / "skills" / "verify-emails" / ".email-cache.json"
PATTERN_TEMPLATES = {"first.last", "firstlast", "first", "flast", "first_last", "last"}
EMAIL_PATTERN_RE = re.compile(r"`?([a-z_\.]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})`?")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


@dataclass
class Recruiter:
    rank: int
    name: str
    title: str


@dataclass
class ApiResult:
    status: str
    email: str = ""
    credits_charged: int = 0
    person_job_title: str = ""
    reason: str = ""
    should_stop: bool = False


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def split_markdown_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    placeholder = "\0PIPE\0"
    line = line.replace(r"\|", placeholder)
    return [cell.replace(placeholder, "|").strip() for cell in line.strip("|").split("|")]


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\[\[(.*?)\]\]", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"[↑↓🏠✅❌]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def table_cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def resolve_ledger_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def resolve_output_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def company_from_ledger(ledger_path: Path) -> str:
    folder = ledger_path.parent.name
    if " - " in folder:
        return folder.split(" - ", 1)[0].strip()
    return folder.strip()


def parse_email_pattern(text: str) -> tuple[str, str]:
    for line in text.splitlines():
        if not line.strip().startswith("**Email pattern:**"):
            continue
        match = EMAIL_PATTERN_RE.search(line)
        if not match:
            return "", ""
        pattern, domain = match.group(1).lower(), match.group(2).lower()
        if pattern not in PATTERN_TEMPLATES:
            return "", ""
        return domain, pattern
    return "", ""


def is_divider_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def clean_header(text: str) -> str:
    text = strip_md(text).lower()
    return re.sub(r"\s+", " ", text).strip()


def rank_from_cell(text: str) -> int:
    match = re.search(r"\bRec\s*#\s*(\d+)\b", strip_md(text), re.IGNORECASE)
    return int(match.group(1)) if match else 10_000


def title_from_row(headers: list[str], cells: list[str]) -> str:
    for index, header in enumerate(headers):
        if header.startswith("title") and index < len(cells):
            title = strip_md(cells[index])
            if title and not re.fullmatch(r"\d+", title):
                return title
    for index, header in enumerate(headers):
        if "evidence" in header and index < len(cells):
            return strip_md(cells[index])
    return ""


def parse_recruiters(text: str, top: int) -> list[Recruiter]:
    lines = text.splitlines()
    for line_number, line in enumerate(lines):
        header_cells = split_markdown_row(line)
        headers = [clean_header(cell) for cell in header_cells]
        if not {"name", "category", "rank"}.issubset(set(headers)):
            continue
        return recruiters_from_table(lines[line_number + 1 :], headers, top)
    return []


def recruiters_from_table(lines: list[str], headers: list[str], top: int) -> list[Recruiter]:
    name_index = headers.index("name")
    category_index = headers.index("category")
    rank_index = headers.index("rank")
    recruiters: list[Recruiter] = []

    for line in lines:
        cells = split_markdown_row(line)
        if not cells:
            break
        if is_divider_row(cells):
            continue
        if len(cells) < len(headers):
            continue
        category = strip_md(cells[category_index]).lower()
        if category != "recruiter":
            continue
        recruiters.append(
            Recruiter(
                rank=rank_from_cell(cells[rank_index]),
                name=strip_md(cells[name_index]),
                title=title_from_row(headers, cells),
            )
        )
    return sorted(recruiters, key=lambda item: item.rank)[:top]


def load_env_file() -> dict[str, str]:
    path = ROOT / ".env"
    values: dict[str, str] = {}
    if not path.exists():
        return values
    # utf-8-sig tolerates a leading BOM (e.g. PowerShell `Set-Content -Encoding utf8`
    # writes one), which would otherwise mangle the first key name and silently
    # drop the API key. Reads plain UTF-8 unchanged when no BOM is present.
    for line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key_from_env() -> str:
    key = os.environ.get("Email_Finder_Dev", "")
    if key:
        return key
    return load_env_file().get("Email_Finder_Dev", "")


def load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def cache_key(full_name: str, company: str) -> str:
    return f"{full_name.lower()}|{company.lower()}"


def endpoint_url(name: str, company: str, domain: str) -> str:
    params = {"full_name": name, "company_name": company}
    if domain:
        params["domain"] = domain
    return f"{BASE_URL}/api/find-email/person?{urlencode(params)}"


def request_for(url: str, api_key: str) -> Request:
    return Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )


def response_json(exc: HTTPError) -> dict[str, Any]:
    raw = exc.read(1_000_000)
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def api_reason(code: int, body: dict[str, Any]) -> str:
    if code == 401:
        return "unauthorized"
    if code == 402:
        return "insufficient credits"
    if code == 403:
        return "forbidden"
    if code == 429:
        return "rate limit"
    message = body.get("message") or body.get("error") or f"HTTP {code}"
    return str(message)


def parse_api_hit(data: dict[str, Any]) -> ApiResult:
    email = str(data.get("valid_email") or "")
    credits = data.get("credits_charged", 1)
    title = str(data.get("person_job_title") or "")
    try:
        credits_charged = int(credits)
    except (TypeError, ValueError):
        credits_charged = 1
    if email:
        return ApiResult("VERIFIED", email, credits_charged, title)
    return ApiResult("NOT FOUND", credits_charged=0)


def find_email(name: str, company: str, domain: str, api_key: str) -> ApiResult:
    opener = build_opener(NoRedirectHandler)
    try:
        with opener.open(request_for(endpoint_url(name, company, domain), api_key), timeout=15) as response:
            raw = response.read(1_000_000)
    except HTTPError as exc:
        body = response_json(exc)
        if exc.code == 404:
            return ApiResult("NOT FOUND")
        if exc.code in {401, 402, 403, 429}:
            reason = api_reason(exc.code, body)
            return ApiResult("SKIPPED", reason=f"api: {reason}", should_stop=exc.code in {402, 429})
        return ApiResult("SKIPPED", reason=f"api: HTTP {exc.code}")
    except (URLError, TimeoutError, socket.timeout, ssl.SSLError, OSError):
        return ApiResult("SKIPPED", reason="network")

    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except json.JSONDecodeError:
        return ApiResult("SKIPPED", reason="api: invalid JSON")
    return parse_api_hit(data if isinstance(data, dict) else {})


def clean_name_part(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def infer_email(full_name: str, domain: str, pattern: str) -> str:
    parts = [clean_name_part(part) for part in full_name.split()]
    parts = [part for part in parts if part]
    if len(parts) < 2:
        return ""
    first, last = parts[0], parts[-1]
    local_parts = {
        "first.last": f"{first}.{last}",
        "firstlast": f"{first}{last}",
        "first": first,
        "flast": f"{first[0]}{last}",
        "first_last": f"{first}_{last}",
        "last": last,
    }
    local_part = local_parts.get(pattern, "")
    return f"{local_part}@{domain}" if local_part and domain else ""


def cache_entry(result: ApiResult) -> dict[str, Any]:
    return {
        "email": result.email,
        "status": result.status,
        "credits_charged": result.credits_charged,
        "person_job_title": result.person_job_title,
        "checked_at": date.today().isoformat(),
    }


def row_from_cache(recruiter: Recruiter, entry: dict[str, Any], domain: str, pattern: str) -> dict[str, Any]:
    status = str(entry.get("status") or "")
    email = str(entry.get("email") or "")
    if status == "NOT FOUND" and domain and pattern:
        email = infer_email(recruiter.name, domain, pattern)
        status = "INFERRED" if email else "NOT FOUND"
    source = "cache" if status == "VERIFIED" else "inferred" if status == "INFERRED" else "none"
    return recruiter_row(recruiter, email, status, source, 0)


def recruiter_row(
    recruiter: Recruiter,
    email: str,
    status: str,
    source: str,
    credits: int,
    api_url: str = "",
) -> dict[str, Any]:
    row = {
        "rank": recruiter.rank,
        "name": recruiter.name,
        "title": recruiter.title,
        "email": email,
        "status": status,
        "source": source,
        "credits": credits,
    }
    if api_url:
        row["api_url"] = api_url
    return row


def skipped_row(recruiter: Recruiter, reason: str) -> dict[str, Any]:
    return recruiter_row(recruiter, "", f"SKIPPED ({reason})", "none", 0)


def row_from_miss(recruiter: Recruiter, domain: str, pattern: str) -> dict[str, Any]:
    email = infer_email(recruiter.name, domain, pattern)
    if email:
        return recruiter_row(recruiter, email, "INFERRED", "inferred", 0)
    return recruiter_row(recruiter, "", "NOT FOUND", "none", 0)


def resolve_recruiters(
    recruiters: list[Recruiter],
    company: str,
    domain: str,
    pattern: str,
    max_credits: int,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cache = load_cache()
    rows: list[dict[str, Any]] = []
    api_key = "" if dry_run else api_key_from_env()
    credits_spent = 0
    cache_hits = 0

    if not dry_run and not api_key:
        raise SystemExit("Email_Finder_Dev API key not found in environment or workspace .env")

    for index, recruiter in enumerate(recruiters):
        key = cache_key(recruiter.name, company)
        entry = cache.get(key)
        if isinstance(entry, dict) and entry.get("status") in {"VERIFIED", "NOT FOUND"}:
            cache_hits += 1
            rows.append(row_from_cache(recruiter, entry, domain, pattern))
            continue
        if dry_run:
            rows.append(skipped_row(recruiter, "dry-run") | {"api_url": endpoint_url(recruiter.name, company, domain)})
            continue
        if credits_spent + 1 > max_credits:
            rows.extend(skipped_row(item, "max-credits") for item in recruiters[index:])
            break

        result = find_email(recruiter.name, company, domain, api_key)
        if result.status in {"VERIFIED", "NOT FOUND"}:
            cache[key] = cache_entry(result)
            save_cache(cache)
        if result.status == "VERIFIED":
            credits_spent += result.credits_charged
            rows.append(recruiter_row(recruiter, result.email, "VERIFIED", "api", result.credits_charged))
            continue
        if result.status == "NOT FOUND":
            rows.append(row_from_miss(recruiter, domain, pattern))
            continue
        rows.append(skipped_row(recruiter, result.reason))
        if result.should_stop:
            rows.extend(skipped_row(item, result.reason) for item in recruiters[index + 1 :])
            break

    summary = summarize(rows, credits_spent, cache_hits)
    return rows, summary


def summarize(rows: list[dict[str, Any]], credits_spent: int, cache_hits: int) -> dict[str, int]:
    return {
        "credits_spent": credits_spent,
        "cache_hits": cache_hits,
        "verified": count_status(rows, "VERIFIED"),
        "inferred": count_status(rows, "INFERRED"),
        "not_found": count_status(rows, "NOT FOUND"),
        "skipped": sum(1 for row in rows if str(row["status"]).startswith("SKIPPED")),
    }


def count_status(rows: list[dict[str, Any]], status: str) -> int:
    return sum(1 for row in rows if row["status"] == status)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    ledger_path = resolve_ledger_path(args.ledger)
    text = ledger_path.read_text(encoding="utf-8")
    company = company_from_ledger(ledger_path)
    domain, pattern = parse_email_pattern(text)
    recruiters = parse_recruiters(text, args.top)
    rows, summary = resolve_recruiters(
        recruiters,
        company,
        domain,
        pattern,
        args.max_credits,
        args.dry_run,
    )
    return {
        "ledger": str(ledger_path),
        "company": company,
        "domain": domain,
        "pattern": pattern,
        "date": date.today().isoformat(),
        "recruiters": rows,
        "summary": summary,
        "emails_md_path": emails_md_path(args, ledger_path),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "## Verified Emails",
        "",
        f"_Generated by verify-emails on {report['date']}_",
        "",
        "| Rank | Name | Title (from ledger) | Email | Status | Source | Credits |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report["recruiters"]:
        lines.append(
            f"| {table_cell(item['rank'])} | {table_cell(item['name'])} | "
            f"{table_cell(item['title'])} | {table_cell(item['email'])} | "
            f"{table_cell(item['status'])} | {table_cell(item['source'])} | "
            f"{table_cell(item['credits'])} |"
        )

    summary = report["summary"]
    domain_pattern = f"{report['pattern']}@{report['domain']}" if report["domain"] and report["pattern"] else "disabled"
    lines.extend(
        [
            "",
            f"- Credits spent this run: {summary['credits_spent']}",
            f"- Cache hits: {summary['cache_hits']}",
            f"- Verified: {summary['verified']}",
            f"- Inferred: {summary['inferred']}",
            f"- Not found: {summary['not_found']}",
            f"- Skipped: {summary['skipped']}",
            f"- Domain/pattern used: {domain_pattern}",
            "",
            "INFERRED rows are unverified pattern guesses — do not treat as confirmed.",
        ]
    )
    return "\n".join(lines)


def emails_md_path(args: argparse.Namespace, ledger_path: Path) -> str | None:
    if args.dry_run or args.no_write:
        return None
    if args.emails_md:
        return str(resolve_output_path(args.emails_md))
    if args.emails_md_default:
        return str(ledger_path.parent / "Verified Emails.md")
    return None


def confidence_for(item: dict[str, Any], pattern: str) -> str:
    if item["status"] == "VERIFIED":
        return "High (EmailFinder-verified)"
    if item["status"] == "INFERRED":
        return f"Medium (inferred {pattern})"
    return ""


def render_emails_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Verified Emails",
        "",
        f"_Generated by verify-emails on {report['date']}_",
        "",
        "| Name | Email | Confidence |",
        "|---|---|---|",
    ]
    for item in report["recruiters"]:
        confidence = confidence_for(item, report["pattern"])
        if not confidence or not item["email"]:
            continue
        lines.append(
            f"| {table_cell(item['name'])} | {table_cell(item['email'])} | "
            f"{table_cell(confidence)} |"
        )
    lines.extend(
        [
            "",
            "_INFERRED rows are unverified pattern guesses — verify before send._",
            "",
        ]
    )
    return "\n".join(lines)


def replace_verified_section(text: str, section: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.strip() == "## Verified Emails"), -1)
    if start == -1:
        separator = "\n\n" if text and not text.endswith("\n") else "\n"
        return f"{text}{separator}{section}\n"

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "".join(lines[:start]) + section + "\n\n" + "".join(lines[end:])


def write_ledger(report: dict[str, Any]) -> None:
    path = Path(report["ledger"])
    text = path.read_text(encoding="utf-8")
    section = render_markdown(report)
    path.write_text(replace_verified_section(text, section), encoding="utf-8")


def write_emails_markdown(report: dict[str, Any]) -> None:
    path_text = report.get("emails_md_path")
    if not path_text:
        return
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_emails_markdown(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify top recruiter emails from a role contacts ledger."
    )
    parser.add_argument(
        "--ledger",
        required=True,
        help="Absolute or workspace-relative path to a role's .contacts-ledger.md.",
    )
    parser.add_argument(
        "--max-credits",
        type=int,
        default=10,
        help="Hard cap for paid EmailFinder.dev credits this run.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="How many ranked recruiters to resolve.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show planned calls without calling the API or writing the ledger.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of markdown.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Call API and update cache, but do not modify the ledger file.",
    )
    parser.add_argument(
        "--emails-md",
        help="Optional path for a derived Verified Emails.md pipeline artifact.",
    )
    parser.add_argument(
        "--emails-md-default",
        action="store_true",
        help="Write Verified Emails.md next to the ledger file.",
    )
    args = parser.parse_args()
    _started_at = time.time()
    report = build_report(args)
    if not args.dry_run and not args.no_write:
        write_ledger(report)
        write_emails_markdown(report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    print(render_markdown(report))


if __name__ == "__main__":
    main()
