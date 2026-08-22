"""Deterministic per-skill artifact verifier for the two-orchestrator E2E test.

Pure functions + a thin CLI, same shape as dedupe.py. Stdlib only. Cannot reach
MCP servers — Gmail-draft state and PDF/worklist results are passed in as args.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

# config.py lives in the repo-root scripts/ dir. This file sits at
# .claude/skills/<skill>/scripts/, so the repo root is parents[4]. resolve()
# follows the global symlink to the real repo, so profile resolves correctly
# whether invoked here or via ~/.claude/skills/. Same parents[4] pattern as
# verify_postings.py / verify_emails.py.
REPO_ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PROFILE = REPO_ROOT / "profile.yaml"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "evals"))

from config import load_profile, resume_glob_prefix
from common import ARCHETYPE_VOCAB, THEME_VOCAB, run_verifier
from verify_behavior_traces import audit_runs

def check(name: str, ok: bool, detail: str = "", severity: str = "fail") -> dict:
    """Normalize a truthy condition into the verifier's serializable check schema."""
    return {"name": name, "ok": bool(ok), "detail": detail, "severity": severity}


def rollup(checks: list[dict]) -> str:
    """Return fail for failed hard checks, warn for only softer failures, else pass."""
    failed = [c for c in checks if not c["ok"]]
    if any(c["severity"] == "fail" for c in failed):
        return "fail"
    if failed:
        return "warn"
    return "pass"


def skill_result(checks: list[dict], notes: str = "") -> dict:
    """Package checks with their rolled-up status and optional diagnostic notes."""
    return {"status": rollup(checks), "checks": checks, "notes": notes}


def blocked_result(note: str = "") -> dict:
    """Represent an intentionally unrun skill without fabricating individual checks."""
    return {"status": "blocked", "checks": [], "notes": note}


def contract_result(skill: str, clone: Path) -> dict:
    """Adapt authoritative per-behavior clause results to the legacy E2E JSON."""
    results = run_verifier(skill, clone, role=clone, profile=CONTRACT_PROFILE)
    checks = [
        {
            "name": result.id,
            "ok": result.verdict != "FAIL",
            "detail": result.detail,
            "severity": "blocked" if result.verdict in {"BLOCKED", "NOT_RUN"} else "fail",
            "status": result.verdict.lower(),
        }
        for result in results
    ]
    if any(result.verdict == "FAIL" for result in results):
        status = "fail"
    elif any(result.verdict in {"BLOCKED", "NOT_RUN"} for result in results):
        status = "blocked"
    else:
        status = "pass"
    return {"status": status, "checks": checks, "notes": "delegated to evals/<behavior>/contract.md"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def check_intake(clone: Path) -> dict:
    """Require a role clone and a nontrivial Job Description artifact."""
    jd = clone / "Job Description.md"
    text = _read(jd)
    return skill_result([
        check("clone-folder-exists", clone.is_dir(), str(clone)),
        check("job-description-present", jd.exists(), str(jd)),
        check("job-description-nonempty", len(text.strip()) > 50, f"{len(text)} chars"),
    ])


def check_classify(clone: Path) -> dict:
    """Validate classification JSON vocabulary, theme cardinality, evidence, and timestamp."""
    f = clone / ".classification.json"
    if not f.exists():
        return skill_result([check("classification-present", False, str(f))])
    try:
        data = json.loads(_read(f))
    except ValueError as exc:
        return skill_result([check("classification-parses", False, str(exc))])
    themes = data.get("themes", []) if isinstance(data.get("themes"), list) else []
    tags = [t.get("tag") for t in themes if isinstance(t, dict)]
    off = [t for t in tags if t not in THEME_VOCAB]
    no_ev = [t for t in themes if isinstance(t, dict) and not str(t.get("evidence", "")).strip()]
    return skill_result([
        check("classification-parses", True),
        check("theme-count-4-6", 4 <= len(tags) <= 6, f"{len(tags)} themes"),
        check("themes-in-vocab", not off, f"off-vocab: {off}"),
        check("archetype-in-vocab", data.get("archetype") in ARCHETYPE_VOCAB, str(data.get("archetype"))),
        check("evidence-present", not no_ev, f"{len(no_ev)} theme(s) missing evidence"),
        check("classified-ts-present", bool(str(data.get("classified_ts", "")).strip())),
    ])


def find_resume(clone: Path, prefix: str | None = None) -> Path | None:
    """Return the lexically first matching resume, or None when no configured prefix matches."""
    prefix = prefix if prefix is not None else resume_glob_prefix()
    matches = sorted(clone.glob(f"{prefix}*.md"))
    return matches[0] if matches else None


def check_tailor_resume(clone: Path, prefix: str | None = None,
                        email: str | None = None) -> dict:
    """Require a substantial tailored resume with contact email and no verification tokens."""
    prefix = prefix if prefix is not None else resume_glob_prefix()
    email = email if email is not None else load_profile()["user_email"]
    r = find_resume(clone, prefix)
    if r is None:
        return skill_result([check("resume-md-present", False, f"glob: {prefix}*.md")])
    text = _read(r)
    leaks = re.findall(r"\[VERIFY|\[NUMBER\?", text)
    return skill_result([
        check("resume-md-present", True, r.name),
        check("resume-nontrivial", len(text.strip()) > 400, f"{len(text)} chars"),
        check("no-verify-leak", not leaks, f"{len(leaks)} leak(s)"),
        check("contact-header-present", email in text),
    ])


def check_pdf(clone: Path, pages, title_leak, prefix: str | None = None) -> dict:
    """Check PDF presence and supplied export contract, warning when diagnostics are absent."""
    prefix = prefix if prefix is not None else resume_glob_prefix()
    checks = [check("resume-pdf-present", bool(list(clone.glob(f"{prefix}*.pdf"))), "glob: *.pdf")]
    if pages is not None:
        checks.append(check("pdf-one-page", pages == 1, f"PAGES={pages}", severity="warn"))
    if title_leak is not None:
        checks.append(check("pdf-no-title-leak", title_leak == 0, f"TITLE_LEAK={title_leak}"))
    if pages is None or title_leak is None:
        # A missing export contract must surface as a warn, not silently skip checks.
        checks.append(check("pdf-contract-provided", False,
                            "PAGES/TITLE_LEAK not captured from build_resume_pdf.py",
                            severity="warn"))
    return skill_result(checks)


def check_packet(clone: Path) -> dict:
    """Apply-packet artifacts: record exists, parses, and — non-negotiable —
    points at a _test remote, never the real Apply Queue."""
    f = clone / ".apply-packet.json"
    if not f.exists():
        return skill_result([check("packet-present", False, str(f))])
    try:
        rec = json.loads(f.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return skill_result([check("packet-parses", False, str(exc))])
    return skill_result([
        check("packet-parses", True),
        check("packet-state-queued", rec.get("state") == "queued", str(rec.get("state"))),
        check("packet-remote-is-test", "_test" in str(rec.get("remote_dir", "")),
              rec.get("remote_dir", "")),
        check("answers-md-present", (clone / "Application Answers.md").exists()),
    ])


def check_gate(worklist_text: str, company: str) -> dict:
    """Require the apply-gate worklist to surface the expected nonempty company name."""
    ok = bool(company) and company.lower() in (worklist_text or "").lower()
    return skill_result([check("worklist-surfaces-role", ok, f"company={company!r}")])


# NOTE: the header-skip below is keyed to find-contacts' current "| Rank | Name | ... |"
# column wording. If those names change, the data-bearing requirement (an email or a
# bare-integer Rank/Total cell) still keeps a header-only ledger from counting as 1 contact.
def _ledger_contact_rows(text: str) -> int:
    rows = 0
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if all(re.fullmatch(r":?-{2,}:?", (c or "-")) for c in cells):  # divider
            continue
        lowered = {c.lower() for c in cells}
        if "name" in lowered and "rank" in lowered:  # header row
            continue
        # A contact row must carry data: an email or a bare-integer (Rank/Total) cell.
        if not any("@" in c or re.fullmatch(r"\d+", c) for c in cells):
            continue
        rows += 1
    return rows


def check_find_contacts(clone: Path) -> dict:
    """Require a contacts ledger containing at least one data-bearing contact row."""
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    n = _ledger_contact_rows(_read(f))
    return skill_result([
        check("ledger-present", True),
        check("ledger-has-contacts", n >= 1, f"{n} contact row(s)"),
    ])


def check_enrich_contacts(clone: Path) -> dict:
    """Require the hooks section and warn when enrichment added no source-tagged rows."""
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    text = _read(f)
    # The heading enrich-contacts actually writes ("## hooks[]"), not a bare substring —
    # "hook" appears in find-contacts column wording and would silently pass pre-enrich.
    has_heading = bool(re.search(r"^##\s*hooks", text, re.MULTILINE | re.IGNORECASE))
    checks = [check("ledger-has-hooks-section", has_heading,
                    "expected a '## hooks' section from enrich-contacts")]
    # Whole-cell match: the header cell "Source (search/enrich)" must not count.
    enrich_rows = any(
        "enrich" in (c.strip().lower() for c in line.strip().strip("|").split("|"))
        for line in text.splitlines() if line.strip().startswith("|"))
    checks.append(check("enrich-rows-present", enrich_rows,
                        "no 'Source: enrich' rows — enrich ran but appended no new people",
                        severity="warn"))
    return skill_result(checks)


def _verified_email_rows(text: str) -> int:
    rows = 0
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any("@" in c and "." in c for c in cells):
            rows += 1
    return rows


def check_verify_emails(clone: Path) -> dict:
    """Require email rows, warning on all-inferred output and failing ledger format mismatches."""
    f = clone / "Verified Emails.md"
    if not f.exists():
        return skill_result([check("verified-emails-present", False, str(f))])
    text = _read(f)
    rows = _verified_email_rows(text)
    ledger = clone / ".contacts-ledger.md"
    ledger_contacts = _ledger_contact_rows(_read(ledger)) if ledger.exists() else 0
    checks = [
        check("verified-emails-present", True),
        check("verified-rows-present", rows >= 1, f"{rows} verified row(s)"),
    ]
    if rows >= 1:
        # An EmailFinder-down run degrades every row to "inferred" — that must warn,
        # not read identically to a fully SMTP-verified run (fail-loud invariant).
        email_lines = [ln for ln in text.splitlines()
                       if ln.strip().startswith("|")
                       and any("@" in c and "." in c for c in ln.split("|"))]
        all_inferred = all("inferred" in ln.lower() for ln in email_lines)
        checks.append(check("not-all-inferred", not all_inferred,
                            "every row is inferred — EmailFinder likely unavailable (degraded run)",
                            severity="warn"))
    if ledger_contacts >= 1 and rows == 0:
        checks.append(check(
            "issue1-ledger-parsed", False,
            f"ledger has {ledger_contacts} contacts but Verified Emails.md is empty — "
            "find-contacts→verify-emails format mismatch (Issue 1)",
        ))
    return skill_result(checks)


def _draft_recipients(draft: dict) -> list[str]:
    return [str(r).lower() for r in (draft or {}).get("toRecipients", [])]


def _load_drafts(path_str: str) -> list[dict]:
    """Parse --draft-json, which may hold a single draft object or a list of them."""
    if not path_str:
        return []
    try:
        data = json.loads(_read(Path(path_str)))
    except ValueError:
        return []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    return []


def check_write_outreach(clone: Path, drafts, expected_recipient: str,
                         expected_lead_recipient: str = "") -> dict:
    """write-outreach drip mode produces TWO Gmail drafts (recruiter #1 + the
    HM/peer-IC lead). `drafts` accepts a single draft dict (back-compat) or a
    list of draft dicts; every draft must be unsent."""
    f = clone / "Cold Outreach.md"
    checks = [check("cold-outreach-present", f.exists(), str(f))]
    if isinstance(drafts, dict):
        drafts = [drafts]
    drafts = [d for d in (drafts or []) if isinstance(d, dict)]
    if not drafts:
        checks.append(check("gmail-draft-present", False, "no draft provided"))
        return skill_result(checks)
    with_id = [d for d in drafts if d.get("id")]
    checks.append(check("gmail-draft-present", bool(with_id), f"{len(with_id)} draft(s) with id"))
    all_recips = [r for d in drafts for r in _draft_recipients(d)]
    if expected_recipient:
        checks.append(check("recruiter-draft-recipient-matches",
                            expected_recipient.lower() in all_recips, f"to={all_recips}"))
    if expected_lead_recipient:
        checks.append(check("lead-draft-recipient-matches",
                            expected_lead_recipient.lower() in all_recips, f"to={all_recips}"))
        # drip should draft both; <2 is a gap-with-note (the same-company guard or
        # a missing HM can legitimately yield one), not a hard failure.
        checks.append(check("both-drafts-present", len(with_id) >= 2,
                            f"{len(with_id)} draft(s) with id; recruiter + HM/peer expected",
                            severity="warn"))
    checks.append(check("all-drafts-unsent",
                        all(not d.get("sent", False) for d in drafts),
                        f"{len(drafts)} draft(s)"))
    return skill_result(checks)


def run_all(args) -> dict:
    """Run authoritative contracts plus diagnostics and compute the overall E2E status."""
    clone = Path(args.clone)
    worklist_text = _read(Path(args.worklist_out)) if args.worklist_out else ""
    drafts = _load_drafts(args.draft_json)
    skills = {
        "interview-prep-intake": contract_result("interview-prep-intake", clone),
        "classify": contract_result("classify", clone),
        "tailor-resume": contract_result("tailor-resume", clone),
        "pdf": contract_result("resume-export", clone),
        "apply-packet": contract_result("apply-packet", clone),
        "apply-gate": check_gate(worklist_text, args.company),
        "find-contacts": contract_result("find-contacts", clone),
        "enrich-contacts": contract_result("enrich-contacts", clone),
        "verify-emails": contract_result("verify-emails", clone),
        "write-outreach": contract_result("write-outreach", clone),
    }
    # Legacy capture values remain diagnostic only. Contract clauses above own
    # pass/fail semantics, so these checks cannot override the PDF verdict.
    if args.pages is not None:
        skills["pdf"]["checks"].append(
            check("legacy-pages-capture", args.pages == 1, f"PAGES={args.pages}", severity="info")
        )
    if args.title_leak is not None:
        skills["pdf"]["checks"].append(
            check(
                "legacy-title-leak-capture", args.title_leak == 0,
                f"TITLE_LEAK={args.title_leak}", severity="info",
            )
        )
    # Ordering signal (invariant 2): the gate writes _worklist.txt; the apply side's
    # first artifact is the ledger. A ledger older than the worklist suggests LinkedIn
    # was spent before the apply gate — warn, don't fail (mtimes are edit-sensitive).
    wl = Path(args.worklist_out) if args.worklist_out else None
    ledger = clone / ".contacts-ledger.md"
    if wl is not None and wl.exists() and ledger.exists():
        ordered = ledger.stat().st_mtime >= wl.stat().st_mtime - 2
        gate = skills["apply-gate"]
        gate["checks"].append(check(
            "apply-after-gate", ordered,
            "ledger predates the apply-gate worklist — apply side may have run before the gate",
            severity="warn"))
        gate["status"] = rollup(gate["checks"])
    if getattr(args, "blocked_apply", False):
        note = "apply side not run (LinkedIn daemon down at preflight)"
        for name in ("find-contacts", "enrich-contacts", "verify-emails", "write-outreach"):
            skills[name] = blocked_result(note)
    trace_runs_dir = getattr(args, "trace_runs_dir", "")
    if trace_runs_dir:
        trace_results = audit_runs(Path(trace_runs_dir))
        trace_checks = [
            check(result.behavior, result.passed, result.detail)
            for result in trace_results
        ]
        skills["behavior-traces"] = skill_result(
            trace_checks,
            notes="all nine closed primitive behavior traces are required",
        )
    statuses = [s["status"] for s in skills.values()]
    if "fail" in statuses:
        overall = "fail"
    elif "warn" in statuses:
        overall = "warn"
    elif "blocked" in statuses:
        overall = "blocked"
    else:
        overall = "pass"
    summary = {
        "pass": statuses.count("pass"), "warn": statuses.count("warn"),
        "fail": statuses.count("fail"), "blocked": statuses.count("blocked"),
        "overall": overall,
    }
    return {"skills": skills, "summary": summary}


def build_parser() -> argparse.ArgumentParser:
    """Build E2E artifact inputs, including optional legacy captures and trace auditing."""
    p = argparse.ArgumentParser(description="Two-orchestrator E2E artifact verifier")
    p.add_argument("--clone", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--worklist-out", default="")
    p.add_argument("--pages", type=int, default=None)
    p.add_argument("--title-leak", type=int, default=None)
    p.add_argument("--draft-json", default="")
    p.add_argument("--expected-recipient", default="",
                   help="recruiter #1 draft recipient email")
    p.add_argument("--expected-lead-recipient", default="",
                   help="HM/peer-IC lead draft recipient email (drip mode drafts two)")
    p.add_argument("--blocked-apply", action="store_true",
                   help="LinkedIn was down at preflight; mark apply-side skills blocked and exclude from fail/warn rollup")
    p.add_argument(
        "--trace-runs-dir", default="",
        help="audit all nine closed primitive traces; omitted for legacy runs",
    )
    return p


def main(argv=None) -> int:
    """Print the E2E report as JSON and exit nonzero only for an overall failure."""
    args = build_parser().parse_args(argv)
    report = run_all(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["summary"]["overall"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
