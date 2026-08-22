#!/usr/bin/env python3
"""Build the canonical synthetic workspace used by behavior evals."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "evals" / "fixtures"
ROLE_FOLDER = "Acme - Senior Agent Builder"
RESUME_NAME = "Jordan Agent Resume - Acme Senior Agent Builder"


def _prepare_target(target: Path, *, force: bool) -> None:
    target = target.resolve()
    if target == Path(target.anchor) or target == REPO_ROOT:
        raise ValueError(f"refusing unsafe fixture target: {target}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"target exists and is not a directory: {target}")
    if target.is_dir() and any(target.iterdir()):
        if not force:
            raise FileExistsError(
                f"target is not empty: {target} (pass --force to replace its contents)"
            )
        for child in target.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    target.mkdir(parents=True, exist_ok=True)


def build_fixture_workspace(target: Path, *, force: bool = False) -> Path:
    """Create a complete, deterministic Acme fixture workspace at *target*."""
    target = target.resolve()
    _prepare_target(target, force=force)
    role = target / "Roles" / ROLE_FOLDER
    role.mkdir(parents=True)

    shutil.copyfile(FIXTURES / "profile.yaml", target / "profile.yaml")
    shutil.copyfile(FIXTURES / "application-profile.md", target / "Application Profile.md")
    shutil.copyfile(FIXTURES / "pipeline-fixture.md", target / "Pipeline.md")
    shutil.copyfile(FIXTURES / "jd-acme-agent-builder.md", role / "Job Description.md")
    shutil.copyfile(FIXTURES / "classification.json", role / ".classification.json")

    resume = role / f"{RESUME_NAME}.md"
    resume.write_text(
        """Jordan Agent
jordan.agent@example.com | (555) 123-4567 | linkedin.com/in/jordan-agent

## PROFESSIONAL EXPERIENCE

**Senior Agent Builder | Acme | 2023-Present**
- Designed and shipped production LLM agents with tool-use orchestration and guardrails.
- Built retrieval pipelines grounded in customer data; owned chunking and retrieval strategy.
- Wrote evaluation suites that caught regressions before customers encountered them.

**Agent Engineer | Beta Corp | 2021-2023**
- Turned ambiguous product needs into reliable agent workflows used by operating teams.

## SKILLS

Python, LLM orchestration, RAG, MCP, evaluation harnesses, production monitoring

## EDUCATION

B.S. Computer Science — State University, 2021
""",
        encoding="utf-8",
    )
    # The resume-export verifier intentionally uses a stdlib page-marker count.
    resume.with_suffix(".pdf").write_bytes(b"%PDF-1.4\n/Type /Page \n%%EOF\n")

    (role / "Application Answers.md").write_text(
        """# Application Answers — Acme

## Salary expectation

$X

## Work authorization

authorized, no sponsorship

## Notice period

2 weeks
""",
        encoding="utf-8",
    )
    (role / ".apply-packet.json").write_text(
        json.dumps(
            {
                "state": "queued",
                "remote_dir": "Apply Queue_test/acme-senior-agent-builder",
                "answers_md": "Application Answers.md",
                "ts": "2026-07-10",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    ledger = (FIXTURES / "contacts-ledger.md").read_text(encoding="utf-8")
    divider = (
        "| Casey Singh | peer | 2 | \"Senior Agent Builder\" | 1 | 1 | 1 | 1 | "
        "6 | 2nd | enrich | activity | 4 | casey.singh@acme.com | Medium (inferred) |"
    )
    ledger += (
        divider
        + "\n\n## hooks\n\n"
        + "- Jordan Reyes — shared a source-backed update about the AI Platform team.\n"
    )
    (role / ".contacts-ledger.md").write_text(ledger, encoding="utf-8")

    (role / "Verified Emails.md").write_text(
        """# Verified Emails — Acme

| Name | Email | Status |
| --- | --- | --- |
| Jordan Reyes | jordan.reyes@acme.com | inferred |
| Morgan Patel | morgan.patel@acme.com | inferred |
| Casey Singh | casey.singh@acme.com | inferred |
""",
        encoding="utf-8",
    )
    (role / "Cold Outreach.md").write_text(
        """# Cold Outreach — Acme

## Intro — Recruiter

To: jordan.reyes@acme.com

Subject: Acme Senior Agent Builder — introduction

Hi Jordan, I saw the Senior Agent Builder role and its focus on production agent systems.

## Intro — Hiring Manager

To: morgan.patel@acme.com

Subject: Acme Senior Agent Builder — production agents

Hi Morgan, I build production LLM agents and was drawn to your end-to-end ownership model.
""",
        encoding="utf-8",
    )
    (role / ".drafts.json").write_text(
        json.dumps(
            [
                {"id": "fixture-recruiter", "toRecipients": ["jordan.reyes@acme.com"], "sent": False},
                {"id": "fixture-hm", "toRecipients": ["morgan.patel@acme.com"], "sent": False},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def build_parser() -> argparse.ArgumentParser:
    """Accept a fixture target and an explicit opt-in for replacing its contents."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Workspace directory to create")
    parser.add_argument(
        "--force", action="store_true", help="Replace contents when target is non-empty"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build the fixture, returning one for unsafe or unusable targets instead of traceback."""
    args = build_parser().parse_args(argv)
    try:
        target = build_fixture_workspace(args.target, force=args.force)
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Built synthetic fixture workspace: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
