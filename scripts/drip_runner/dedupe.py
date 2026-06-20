"""Decide whether a role is already in Pipeline.md. Pure + a thin CLI."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path


def company_in_pipeline(company: str, pipeline_text: str) -> bool:
    # Word-boundary match so a short name does not match inside another word
    # (e.g. "AM" must not match "Amazon"). Soft signal only — see is_duplicate.
    company = (company or "").strip()
    if not company:
        return False
    return re.search(r"\b" + re.escape(company) + r"\b", pipeline_text or "", re.IGNORECASE) is not None


def job_id_in_pipeline(job_id: str, pipeline_text: str) -> bool:
    return bool(job_id) and job_id in (pipeline_text or "")


def is_duplicate(company: str, job_id: str, pipeline_text: str) -> bool:
    # Auto-skip ONLY on the precise LinkedIn job_id. Company-name matching is too
    # coarse for an auto-skip: a company that appears anywhere in append-only
    # Pipeline.md — including closed/archived rows — would falsely mark a
    # genuinely new role as a duplicate and silently drop it. Biasing toward NEW
    # means at worst we re-file (intake's folder-exists check is the backstop),
    # never silently lose a job.
    return job_id_in_pipeline(job_id, pipeline_text)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--company", default="")
    p.add_argument("--job-id", default="")
    p.add_argument("--pipeline", required=True)
    args = p.parse_args(argv)
    text = Path(args.pipeline).read_text(encoding="utf-8-sig", errors="ignore")
    dup = is_duplicate(args.company, args.job_id, text)
    print("DUPLICATE" if dup else "NEW")
    return 0 if dup else 1


if __name__ == "__main__":
    sys.exit(main())
