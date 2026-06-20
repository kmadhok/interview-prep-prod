"""Decide whether a role is already in Pipeline.md. Pure + a thin CLI."""
from __future__ import annotations
import argparse, sys
from pathlib import Path


def company_in_pipeline(company: str, pipeline_text: str) -> bool:
    company = (company or "").strip().lower()
    return bool(company) and company in (pipeline_text or "").lower()


def job_id_in_pipeline(job_id: str, pipeline_text: str) -> bool:
    return bool(job_id) and job_id in (pipeline_text or "")


def is_duplicate(company: str, job_id: str, pipeline_text: str) -> bool:
    return job_id_in_pipeline(job_id, pipeline_text) or company_in_pipeline(company, pipeline_text)


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
