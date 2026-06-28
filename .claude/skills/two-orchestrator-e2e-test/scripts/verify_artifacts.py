"""Deterministic per-skill artifact verifier for the two-orchestrator E2E test.

Pure functions + a thin CLI, same shape as dedupe.py. Stdlib only. Cannot reach
MCP servers — Gmail-draft state and PDF/worklist results are passed in as args.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

# Classification vocab — must match jd-to-ready/SKILL.md (themes ~line 115, archetypes ~118).
THEME_VOCAB = {
    "agents", "RAG", "NL→SQL", "MCP", "LLM-orchestration", "ML-pipeline", "platform",
    "business-translation", "end-to-end", "RPA", "experimentation", "dashboards",
    "consulting", "simplification", "leverage", "cross-functional", "engineering-rigor", "evaluation",
}
ARCHETYPE_VOCAB = {
    "agent-builder", "FDE / client-facing", "consulting / product-builder",
    "platform / ML engineering", "data-engineering / analytics",
}


def check(name: str, ok: bool, detail: str = "", severity: str = "fail") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail, "severity": severity}


def rollup(checks: list[dict]) -> str:
    failed = [c for c in checks if not c["ok"]]
    if any(c["severity"] == "fail" for c in failed):
        return "fail"
    if failed:
        return "warn"
    return "pass"


def skill_result(checks: list[dict], notes: str = "") -> dict:
    return {"status": rollup(checks), "checks": checks, "notes": notes}


def blocked_result(note: str = "") -> dict:
    return {"status": "blocked", "checks": [], "notes": note}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def check_intake(clone: Path) -> dict:
    jd = clone / "Job Description.md"
    text = _read(jd)
    return skill_result([
        check("clone-folder-exists", clone.is_dir(), str(clone)),
        check("job-description-present", jd.exists(), str(jd)),
        check("job-description-nonempty", len(text.strip()) > 50, f"{len(text)} chars"),
    ])


def check_classify(clone: Path) -> dict:
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


def find_resume(clone: Path) -> Path | None:
    matches = sorted(clone.glob("Kanu Madhok Resume - *.md"))
    return matches[0] if matches else None


def check_tailor_resume(clone: Path) -> dict:
    r = find_resume(clone)
    if r is None:
        return skill_result([check("resume-md-present", False, "glob: Kanu Madhok Resume - *.md")])
    text = _read(r)
    leaks = re.findall(r"\[VERIFY|\[NUMBER\?", text)
    return skill_result([
        check("resume-md-present", True, r.name),
        check("resume-nontrivial", len(text.strip()) > 400, f"{len(text)} chars"),
        check("no-verify-leak", not leaks, f"{len(leaks)} leak(s)"),
        check("contact-header-present", "madhok.kanu@gmail.com" in text),
    ])


def check_pdf(clone: Path, pages, title_leak) -> dict:
    checks = [check("resume-pdf-present", bool(list(clone.glob("Kanu Madhok Resume - *.pdf"))), "glob: *.pdf")]
    if pages is not None:
        checks.append(check("pdf-one-page", pages == 1, f"PAGES={pages}", severity="warn"))
    if title_leak is not None:
        checks.append(check("pdf-no-title-leak", title_leak == 0, f"TITLE_LEAK={title_leak}"))
    return skill_result(checks)


def check_gate(worklist_text: str, company: str) -> dict:
    ok = bool(company) and company.lower() in (worklist_text or "").lower()
    return skill_result([check("worklist-surfaces-role", ok, f"company={company!r}")])


# NOTE: the header-skip below is keyed to find-contacts' current "| Rank | Name | ... |"
# column wording; if those column names change, the header row is counted as a contact.
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
        rows += 1
    return rows


def check_find_contacts(clone: Path) -> dict:
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    n = _ledger_contact_rows(_read(f))
    return skill_result([
        check("ledger-present", True),
        check("ledger-has-contacts", n >= 1, f"{n} contact row(s)"),
    ])


def check_enrich_contacts(clone: Path) -> dict:
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    return skill_result([check("ledger-has-hooks", "hook" in _read(f).lower(),
                               "expected a hooks section from enrich-contacts")])


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
    f = clone / "Verified Emails.md"
    if not f.exists():
        return skill_result([check("verified-emails-present", False, str(f))])
    rows = _verified_email_rows(_read(f))
    ledger = clone / ".contacts-ledger.md"
    ledger_contacts = _ledger_contact_rows(_read(ledger)) if ledger.exists() else 0
    checks = [
        check("verified-emails-present", True),
        check("verified-rows-present", rows >= 1, f"{rows} verified row(s)"),
    ]
    if ledger_contacts >= 1 and rows == 0:
        checks.append(check(
            "issue1-ledger-parsed", False,
            f"ledger has {ledger_contacts} contacts but Verified Emails.md is empty — "
            "find-contacts→verify-emails format mismatch (Issue 1)",
        ))
    return skill_result(checks)


def check_write_outreach(clone: Path, draft: dict | None, expected_recipient: str) -> dict:
    f = clone / "Cold Outreach.md"
    checks = [check("cold-outreach-present", f.exists(), str(f))]
    if not draft:
        checks.append(check("gmail-draft-present", False, "no draft provided"))
        return skill_result(checks)
    recips = [str(r).lower() for r in draft.get("toRecipients", [])]
    checks.append(check("gmail-draft-present", bool(draft.get("id")), draft.get("id", "")))
    if expected_recipient:
        checks.append(check("draft-recipient-matches", expected_recipient.lower() in recips, f"to={recips}"))
    checks.append(check("draft-unsent", not draft.get("sent", False), "drafts listing = unsent"))
    return skill_result(checks)


def run_all(args) -> dict:
    clone = Path(args.clone)
    worklist_text = _read(Path(args.worklist_out)) if args.worklist_out else ""
    draft = None
    if args.draft_json:
        try:
            draft = json.loads(_read(Path(args.draft_json)))
        except ValueError:
            draft = None
    skills = {
        "interview-prep-intake": check_intake(clone),
        "classify": check_classify(clone),
        "tailor-resume": check_tailor_resume(clone),
        "pdf": check_pdf(clone, args.pages, args.title_leak),
        "apply-gate": check_gate(worklist_text, args.company),
        "find-contacts": check_find_contacts(clone),
        "enrich-contacts": check_enrich_contacts(clone),
        "verify-emails": check_verify_emails(clone),
        "write-outreach": check_write_outreach(clone, draft, args.expected_recipient or ""),
    }
    if getattr(args, "blocked_apply", False):
        note = "apply side not run (LinkedIn daemon down at preflight)"
        for name in ("find-contacts", "enrich-contacts", "verify-emails", "write-outreach"):
            skills[name] = blocked_result(note)
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
    p = argparse.ArgumentParser(description="Two-orchestrator E2E artifact verifier")
    p.add_argument("--clone", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--worklist-out", default="")
    p.add_argument("--pages", type=int, default=None)
    p.add_argument("--title-leak", type=int, default=None)
    p.add_argument("--draft-json", default="")
    p.add_argument("--expected-recipient", default="")
    p.add_argument("--blocked-apply", action="store_true",
                   help="LinkedIn was down at preflight; mark apply-side skills blocked and exclude from fail/warn rollup")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    report = run_all(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["summary"]["overall"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
