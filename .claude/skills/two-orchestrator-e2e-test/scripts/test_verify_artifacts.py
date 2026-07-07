import os, re, sys, json, tempfile
from pathlib import Path

import pytest

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


_RESUME_OK = ("# Test User\n\ntest.user@example.com\n\n" +
              "## EXPERIENCE\n- Built a registry-governed semantic layer over 67 tables.\n" * 6)


def test_tailor_resume_pass():
    clone = _clone_with({"Test User Resume - Snowflake FDE.md": _RESUME_OK})
    assert va.check_tailor_resume(clone)["status"] == "pass"


def test_tailor_resume_verify_leak_fails():
    leaked = _RESUME_OK + "\n- Drove [VERIFY: 95% accuracy] across the org.\n"
    clone = _clone_with({"Test User Resume - Snowflake FDE.md": leaked})
    res = va.check_tailor_resume(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "no-verify-leak" and not c["ok"] for c in res["checks"])


def test_tailor_resume_missing_fails():
    assert va.check_tailor_resume(_clone_with({}))["status"] == "fail"


def test_pdf_clean_and_overflow():
    clone = _clone_with({"Test User Resume - Snowflake FDE.pdf": "%PDF-1.4"})
    assert va.check_pdf(clone, pages=1, title_leak=0)["status"] == "pass"
    # 2 pages = warn (pass-with-gap), not fail
    assert va.check_pdf(clone, pages=2, title_leak=0)["status"] == "warn"
    # title leak = hard fail
    assert va.check_pdf(clone, pages=1, title_leak=1)["status"] == "fail"


def test_pdf_missing_contract_warns():
    # PAGES/TITLE_LEAK not captured -> the skipped checks must surface as a warn,
    # not read as a clean pass.
    clone = _clone_with({"Test User Resume - Snowflake FDE.pdf": "%PDF-1.4"})
    res = va.check_pdf(clone, pages=None, title_leak=None)
    assert res["status"] == "warn", res
    assert any(c["name"] == "pdf-contract-provided" and not c["ok"] for c in res["checks"])


def test_gate_surfaces_role():
    out = "Snowflake\tForward Deployed Analytics Engineer\nMeta\tBusiness Engineer\n"
    assert va.check_gate(out, "Snowflake")["status"] == "pass"
    assert va.check_gate(out, "Datadog")["status"] == "fail"


_LEDGER = "\n".join([
    "# Contacts Ledger",
    "## Recruiters (ranked)",
    "| Rank | Name | Practice | Email (inferred) | Source (search/enrich) |",
    "|------|------|----------|------------------|------------------------|",
    "| 1 | Brad Mallmann | GTM | brad.mallmann@snowflake.com | search |",
    "| 2 | Diane Nguyen | Cortex | diane.nguyen@snowflake.com | search |",
    "| 3 | Kaitlyn Ryu | Cortex | kaitlyn.ryu@snowflake.com | enrich |",
    "## hooks[]",
    "- Brad: posted about data-foundation governance.",
])

# Pre-enrich shape: no hooks section, no enrich rows (what find-contacts alone writes).
_LEDGER_PRE_ENRICH = "\n".join([
    "# Contacts Ledger",
    "## Recruiters (ranked)",
    "| Rank | Name | Practice | Email (inferred) | Source (search/enrich) |",
    "|------|------|----------|------------------|------------------------|",
    "| 1 | Brad Mallmann | GTM | brad.mallmann@snowflake.com | search |",
])


def test_find_contacts_counts_rows():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    res = va.check_find_contacts(clone)
    assert res["status"] == "pass"
    assert va._ledger_contact_rows(_LEDGER) == 3


def test_find_contacts_missing_fails():
    assert va.check_find_contacts(_clone_with({}))["status"] == "fail"


def test_find_contacts_header_only_ledger_fails():
    # A ledger with only a header + divider must count 0 contacts even if the
    # header-skip's column-name keying drifts — rows must carry an email/integer.
    header_only = "\n".join([
        "## Recruiters (ranked)",
        "| Position | Person | Practice |",
        "|----------|--------|----------|",
    ])
    clone = _clone_with({".contacts-ledger.md": header_only})
    res = va.check_find_contacts(clone)
    assert res["status"] == "fail"
    assert va._ledger_contact_rows(header_only) == 0


def test_enrich_requires_hooks_section():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    assert va.check_enrich_contacts(clone)["status"] == "pass"
    no_hooks = _clone_with({".contacts-ledger.md": "| Rank | Name |\n| 1 | X |"})
    assert va.check_enrich_contacts(no_hooks)["status"] == "fail"


def test_enrich_hook_substring_alone_does_not_pass():
    # The word "hook" in column wording (or anywhere) must not satisfy the check —
    # only the "## hooks" heading enrich actually writes does.
    sneaky = "| Name | Hook |\n| Brad | loves fishing hooks |"
    clone = _clone_with({".contacts-ledger.md": sneaky})
    res = va.check_enrich_contacts(clone)
    assert res["status"] == "fail"


def test_enrich_heading_without_enrich_rows_warns():
    # Heading present but no Source: enrich rows -> warn (legit when no new people),
    # and the header cell "Source (search/enrich)" must NOT count as an enrich row.
    text = _LEDGER_PRE_ENRICH + "\n## hooks[]\n- Brad: posted about governance.\n"
    clone = _clone_with({".contacts-ledger.md": text})
    res = va.check_enrich_contacts(clone)
    assert res["status"] == "warn", res
    assert any(c["name"] == "enrich-rows-present" and not c["ok"] for c in res["checks"])


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


def test_verify_emails_all_inferred_warns():
    # EmailFinder down -> every row degrades to inferred. That must warn (fail-loud),
    # not read identically to a fully SMTP-verified run.
    degraded = "\n".join([
        "# Verified Emails",
        "| Name | Email | Confidence |",
        "|---|---|---|",
        "| Brad Mallmann | brad.mallmann@snowflake.com | Medium (inferred first.last) |",
        "| Diane Nguyen | diane.nguyen@snowflake.com | Medium (inferred first.last) |",
    ])
    clone = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": degraded})
    res = va.check_verify_emails(clone)
    assert res["status"] == "warn", res
    assert any(c["name"] == "not-all-inferred" and not c["ok"] for c in res["checks"])
    # A mixed file (one SMTP-verified row) stays pass.
    mixed = degraded.replace("Medium (inferred first.last) |\n| Diane",
                             "High (EmailFinder-verified) |\n| Diane")
    clone2 = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": mixed})
    assert va.check_verify_emails(clone2)["status"] == "pass"


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


def test_write_outreach_two_drafts_pass():
    clone = _clone_with({"Cold Outreach.md": "two intros"})
    drafts = [
        {"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]},
        {"id": "h1", "toRecipients": ["dana.hm@snowflake.com"]},
    ]
    res = va.check_write_outreach(clone, drafts, "brad.mallmann@snowflake.com",
                                  "dana.hm@snowflake.com")
    assert res["status"] == "pass", res


def test_write_outreach_any_draft_sent_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    drafts = [
        {"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]},
        {"id": "h1", "toRecipients": ["dana.hm@snowflake.com"], "sent": True},
    ]
    res = va.check_write_outreach(clone, drafts, "brad.mallmann@snowflake.com",
                                  "dana.hm@snowflake.com")
    assert res["status"] == "fail"
    assert any(c["name"] == "all-drafts-unsent" and not c["ok"] for c in res["checks"])


def test_write_outreach_lead_recipient_missing_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    drafts = [{"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]}]
    res = va.check_write_outreach(clone, drafts, "brad.mallmann@snowflake.com",
                                  "dana.hm@snowflake.com")
    assert res["status"] == "fail"


def test_write_outreach_same_company_guard_one_draft_warns():
    # Same-company double-send guard: recruiter and lead resolve to one address,
    # so write-outreach drafts once. The expected lead == recruiter, so the lead
    # match still passes; only both-drafts-present warns (gap-with-note, not fail).
    clone = _clone_with({"Cold Outreach.md": "x"})
    drafts = [{"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]}]
    res = va.check_write_outreach(clone, drafts, "brad.mallmann@snowflake.com",
                                  "brad.mallmann@snowflake.com")
    assert res["status"] == "warn", res
    assert any(c["name"] == "both-drafts-present" and not c["ok"] for c in res["checks"])


_PACKET_OK = json.dumps({
    "schema": 1, "state": "queued",
    "pdf_remote": "gdrive:_test/Apply Queue/2026-06-28 · Snowflake - FDE.pdf",
    "answers_remote": "gdrive:_test/Apply Queue/Snowflake - FDE - Answers.txt",
    "pdf_sha256": "0" * 64, "remote_dir": "gdrive:_test/Apply Queue",
})
_PACKET_FILES = {".apply-packet.json": _PACKET_OK, "Application Answers.md": "Q1: ...\nA1: ..."}


def test_run_all_two_drafts_list_pass():
    files = {
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Test User Resume - Snowflake FDE.md": _RESUME_OK,
        "Test User Resume - Snowflake FDE.pdf": "%PDF-1.4",
        ".contacts-ledger.md": _LEDGER,
        "Verified Emails.md": _VERIFIED_OK,
        "Cold Outreach.md": "two intros",
        **_PACKET_FILES,
    }
    clone = _clone_with(files)
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tForward Deployed Analytics Engineer\n", encoding="utf-8")
    draft = clone / "_draft.json"
    draft.write_text(json.dumps([
        {"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]},
        {"id": "h1", "toRecipients": ["dana.hm@snowflake.com"]},
    ]), encoding="utf-8")
    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake",
        "--worklist-out", str(worklist), "--pages", "1", "--title-leak", "0",
        "--draft-json", str(draft),
        "--expected-recipient", "brad.mallmann@snowflake.com",
        "--expected-lead-recipient", "dana.hm@snowflake.com",
    ])
    report = va.run_all(args)
    assert report["summary"]["overall"] == "pass", json.dumps(report, indent=2)
    assert report["skills"]["write-outreach"]["status"] == "pass"


def test_run_all_full_fixture_overall_pass():
    files = {
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Test User Resume - Snowflake FDE.md": _RESUME_OK,
        "Test User Resume - Snowflake FDE.pdf": "%PDF-1.4",
        ".contacts-ledger.md": _LEDGER,
        "Verified Emails.md": _VERIFIED_OK,
        "Cold Outreach.md": "Hi Brad,",
        **_PACKET_FILES,
    }
    clone = _clone_with(files)
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tForward Deployed Analytics Engineer\n", encoding="utf-8")
    draft = clone / "_draft.json"
    draft.write_text(json.dumps({"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]}), encoding="utf-8")

    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake",
        "--worklist-out", str(worklist), "--pages", "1", "--title-leak", "0",
        "--draft-json", str(draft), "--expected-recipient", "brad.mallmann@snowflake.com",
    ])
    report = va.run_all(args)
    assert report["summary"]["overall"] == "pass", json.dumps(report, indent=2)
    assert set(report["skills"]) >= {
        "interview-prep-intake", "classify", "tailor-resume", "pdf", "apply-gate",
        "find-contacts", "enrich-contacts", "verify-emails", "write-outreach",
    }


def test_run_all_flags_issue1_overall_fail():
    files = dict({
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Test User Resume - Snowflake FDE.md": _RESUME_OK,
        "Test User Resume - Snowflake FDE.pdf": "%PDF-1.4",
        ".contacts-ledger.md": _LEDGER,
        "Verified Emails.md": "# Verified Emails\n_no rows_\n",  # <- Issue 1
        "Cold Outreach.md": "Hi Brad,",
    })
    clone = _clone_with(files)
    args = va.build_parser().parse_args(["--clone", str(clone), "--company", "Snowflake"])
    report = va.run_all(args)
    assert report["summary"]["overall"] == "fail"
    assert report["skills"]["verify-emails"]["status"] == "fail"


def test_run_all_blocked_apply_marks_apply_skills_blocked():
    files = {
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Test User Resume - Snowflake FDE.md": _RESUME_OK,
        "Test User Resume - Snowflake FDE.pdf": "%PDF-1.4",
        **_PACKET_FILES,
    }
    clone = _clone_with(files)
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tForward Deployed Analytics Engineer\n", encoding="utf-8")
    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake",
        "--worklist-out", str(worklist), "--pages", "1", "--title-leak", "0",
        "--blocked-apply",
    ])
    report = va.run_all(args)
    for name in ("find-contacts", "enrich-contacts", "verify-emails", "write-outreach"):
        assert report["skills"][name]["status"] == "blocked", name
    assert report["summary"]["overall"] != "fail"
    assert report["summary"]["overall"] == "blocked"


def test_run_all_empty_draft_json_degrades_without_crash():
    clone = _clone_with({"Cold Outreach.md": "Hi Brad,"})
    empty = clone / "_draft.json"
    empty.write_text("", encoding="utf-8")  # empty file -> json.loads("") would raise
    args = va.build_parser().parse_args(["--clone", str(clone), "--draft-json", str(empty)])
    report = va.run_all(args)  # must not raise
    assert report["skills"]["write-outreach"]["status"] == "fail"


def test_check_packet_passes_on_test_remote(tmp_path):
    import json
    (tmp_path / ".apply-packet.json").write_text(json.dumps({
        "schema": 1, "state": "queued",
        "pdf_remote": "gdrive:_test/Apply Queue/2026-06-28 · X - Y.pdf",
        "answers_remote": "gdrive:_test/Apply Queue/X - Y - Answers.txt",
        "pdf_sha256": "0" * 64, "remote_dir": "gdrive:_test/Apply Queue",
    }), encoding="utf-8")
    (tmp_path / "Application Answers.md").write_text("x", encoding="utf-8")
    result = va.check_packet(tmp_path)
    assert all(c["ok"] for c in result["checks"])


def test_check_packet_fails_on_real_remote(tmp_path):
    import json
    (tmp_path / ".apply-packet.json").write_text(json.dumps({
        "schema": 1, "state": "queued", "pdf_remote": "gdrive:Apply Queue/x.pdf",
        "answers_remote": None, "pdf_sha256": "0" * 64,
        "remote_dir": "gdrive:Apply Queue",
    }), encoding="utf-8")
    result = va.check_packet(tmp_path)
    assert any(c["name"] == "packet-remote-is-test" and not c["ok"] for c in result["checks"])


def test_apply_after_gate_ordering_warns_when_ledger_predates_worklist():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tFDE\n", encoding="utf-8")
    # Backdate the ledger 100s before the worklist -> apply side ran before the gate.
    ledger = clone / ".contacts-ledger.md"
    past = worklist.stat().st_mtime - 100
    os.utime(ledger, (past, past))
    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake", "--worklist-out", str(worklist)])
    report = va.run_all(args)
    gate = report["skills"]["apply-gate"]
    assert gate["status"] == "warn", gate
    assert any(c["name"] == "apply-after-gate" and not c["ok"] for c in gate["checks"])


def test_apply_after_gate_ordering_passes_when_ledger_is_newer():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tFDE\n", encoding="utf-8")
    ledger = clone / ".contacts-ledger.md"
    future = worklist.stat().st_mtime + 100
    os.utime(ledger, (future, future))
    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake", "--worklist-out", str(worklist)])
    report = va.run_all(args)
    gate = report["skills"]["apply-gate"]
    assert all(c["ok"] for c in gate["checks"]), gate


def _parse_jd_to_ready_vocab(text: str) -> tuple[set, set]:
    """Pull the theme + archetype vocab out of jd-to-ready/SKILL.md prose."""
    theme_line = next(ln for ln in text.splitlines()
                      if ln.startswith("> `") and "agents" in ln)
    themes = set(re.findall(r"`([^`]+)`", theme_line))
    after = text.split("Archetypes:", 1)[1].splitlines()
    archetypes = set()
    for ln in after[1:]:
        m = re.match(r"^- \*\*(.+?)\*\*", ln)
        if not m:
            break
        archetypes.add(m.group(1))
    return themes, archetypes


def test_vocab_matches_jd_to_ready_skill():
    # THEME_VOCAB/ARCHETYPE_VOCAB are duplicated literals (can't import from Markdown);
    # this drift test fails loudly if jd-to-ready's vocab changes shape.
    jdtr = Path(__file__).resolve().parent.parent.parent / "jd-to-ready" / "SKILL.md"
    if not jdtr.exists():
        pytest.skip("jd-to-ready/SKILL.md not found (standalone checkout)")
    themes, archetypes = _parse_jd_to_ready_vocab(
        jdtr.read_text(encoding="utf-8-sig", errors="ignore"))
    assert len(themes) == 18 and len(archetypes) == 5, (len(themes), len(archetypes))
    assert themes == va.THEME_VOCAB
    assert archetypes == va.ARCHETYPE_VOCAB
