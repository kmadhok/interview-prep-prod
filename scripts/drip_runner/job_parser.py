"""Parse a 'JOB' drip-queue email into a structured job reference. Pure, no I/O."""
from __future__ import annotations
import argparse, json, re, sys
from dataclasses import dataclass, asdict

LINKEDIN_JOB_RE = re.compile(r"linkedin\.com/jobs/view/(\d+)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)


@dataclass
class JobRef:
    is_job: bool
    url: str = ""
    source: str = ""
    job_id: str = ""
    reason: str = ""


def is_job_subject(subject: str) -> bool:
    return bool(re.match(r"\s*job\b", subject or "", re.IGNORECASE))


def first_url(body: str) -> str:
    m = URL_RE.search(body or "")
    return m.group(0).rstrip(".,);]") if m else ""


def parse_job_email(subject: str, body: str) -> JobRef:
    if not is_job_subject(subject):
        return JobRef(False, reason="subject does not start with JOB token")
    url = first_url(body)
    if not url:
        return JobRef(False, reason="no URL found in body")
    m = LINKEDIN_JOB_RE.search(url)
    if m:
        return JobRef(True, url=url, source="linkedin", job_id=m.group(1))
    return JobRef(True, url=url, source="ats")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    args = p.parse_args(argv)
    print(json.dumps(asdict(parse_job_email(args.subject, args.body))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
