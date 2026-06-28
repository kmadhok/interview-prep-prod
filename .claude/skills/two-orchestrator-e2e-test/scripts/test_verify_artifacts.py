import sys, json, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import verify_artifacts as va


def _clone_with(files: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = d / name
        p.write_text(content, encoding="utf-8")
    return d


def test_rollup_severities():
    assert va.rollup([va.check("a", True)]) == "pass"
    assert va.rollup([va.check("a", False, severity="warn")]) == "warn"
    assert va.rollup([va.check("a", False, severity="fail")]) == "fail"
    # a hard fail dominates a warn
    assert va.rollup([va.check("a", False, "", "warn"), va.check("b", False, "", "fail")]) == "fail"


def test_intake_pass_and_fail():
    good = _clone_with({"Job Description.md": "# Role\n\n" + "x" * 100})
    res = va.check_intake(good)
    assert res["status"] == "pass", res

    empty = _clone_with({})  # no Job Description.md
    assert va.check_intake(empty)["status"] == "fail"


_GOOD_CLASS = json.dumps({
    "themes": [
        {"tag": "NL→SQL", "evidence": "expose tables to natural language"},
        {"tag": "agents", "evidence": "data agents need to reason"},
        {"tag": "end-to-end", "evidence": "source ingestion to semantic layer"},
        {"tag": "business-translation", "evidence": "translate business requirements"},
    ],
    "archetype": "FDE / client-facing",
    "archetype_rationale": "embeds with customers",
    "notes": "",
    "classified_ts": "2026-06-28",
})


def test_classify_pass():
    clone = _clone_with({".classification.json": _GOOD_CLASS})
    assert va.check_classify(clone)["status"] == "pass"


def test_classify_off_vocab_theme_fails():
    bad = json.loads(_GOOD_CLASS)
    bad["themes"][0]["tag"] = "made-up-tag"
    clone = _clone_with({".classification.json": json.dumps(bad)})
    res = va.check_classify(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "themes-in-vocab" and not c["ok"] for c in res["checks"])


def test_classify_missing_file_fails():
    assert va.check_classify(_clone_with({}))["status"] == "fail"


_RESUME_OK = ("# Kanu Madhok\n\nmadhok.kanu@gmail.com\n\n" +
              "## EXPERIENCE\n- Built a registry-governed semantic layer over 67 tables.\n" * 6)


def test_tailor_resume_pass():
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": _RESUME_OK})
    assert va.check_tailor_resume(clone)["status"] == "pass"


def test_tailor_resume_verify_leak_fails():
    leaked = _RESUME_OK + "\n- Drove [VERIFY: 95% accuracy] across the org.\n"
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": leaked})
    res = va.check_tailor_resume(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "no-verify-leak" and not c["ok"] for c in res["checks"])


def test_tailor_resume_missing_fails():
    assert va.check_tailor_resume(_clone_with({}))["status"] == "fail"


def test_pdf_clean_and_overflow():
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.pdf": "%PDF-1.4"})
    assert va.check_pdf(clone, pages=1, title_leak=0)["status"] == "pass"
    # 2 pages = warn (pass-with-gap), not fail
    assert va.check_pdf(clone, pages=2, title_leak=0)["status"] == "warn"
    # title leak = hard fail
    assert va.check_pdf(clone, pages=1, title_leak=1)["status"] == "fail"


def test_gate_surfaces_role():
    out = "Snowflake\tForward Deployed Analytics Engineer\nMeta\tBusiness Engineer\n"
    assert va.check_gate(out, "Snowflake")["status"] == "pass"
    assert va.check_gate(out, "Datadog")["status"] == "fail"


_LEDGER = "\n".join([
    "# Contacts Ledger",
    "## Recruiters (ranked)",
    "| Rank | Name | Practice | Email (inferred) |",
    "|------|------|----------|------------------|",
    "| 1 | Brad Mallmann | GTM | brad.mallmann@snowflake.com |",
    "| 2 | Diane Nguyen | Cortex | diane.nguyen@snowflake.com |",
    "## hooks[]",
    "- Brad: posted about data-foundation governance.",
])


def test_find_contacts_counts_rows():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    res = va.check_find_contacts(clone)
    assert res["status"] == "pass"
    assert va._ledger_contact_rows(_LEDGER) == 2


def test_find_contacts_missing_fails():
    assert va.check_find_contacts(_clone_with({}))["status"] == "fail"


def test_enrich_requires_hooks_section():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    assert va.check_enrich_contacts(clone)["status"] == "pass"
    no_hooks = _clone_with({".contacts-ledger.md": "| Rank | Name |\n| 1 | X |"})
    assert va.check_enrich_contacts(no_hooks)["status"] == "fail"


_VERIFIED_OK = "\n".join([
    "# Verified Emails",
    "| Name | Email | Confidence |",
    "|---|---|---|",
    "| Brad Mallmann | brad.mallmann@snowflake.com | High |",
])


def test_verify_emails_pass():
    clone = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": _VERIFIED_OK})
    assert va.check_verify_emails(clone)["status"] == "pass"


def test_verify_emails_issue1_empty_with_contacts_fails():
    # ledger HAS contacts but verification produced zero rows -> the Issue 1 regression
    empty = "# Verified Emails\n\n_no rows_\n"
    clone = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": empty})
    res = va.check_verify_emails(clone)
    assert res["status"] == "fail"
    assert any("issue1" in c["name"] for c in res["checks"])


def test_write_outreach_pass():
    clone = _clone_with({"Cold Outreach.md": "## Recruiter email\nHi Brad,"})
    draft = {"id": "r123", "toRecipients": ["brad.mallmann@snowflake.com"], "subject": "Re: ..."}
    assert va.check_write_outreach(clone, draft, "brad.mallmann@snowflake.com")["status"] == "pass"


def test_write_outreach_recipient_mismatch_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    draft = {"id": "r123", "toRecipients": ["someone.else@snowflake.com"]}
    res = va.check_write_outreach(clone, draft, "brad.mallmann@snowflake.com")
    assert res["status"] == "fail"


def test_write_outreach_no_draft_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    assert va.check_write_outreach(clone, None, "")["status"] == "fail"
