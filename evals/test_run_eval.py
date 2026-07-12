"""Self-contained pytest tests for the eval harness runner.

Drives run_eval.py via subprocess (sys.executable) against synthetic tmp
workspaces. Does NOT read the real workspace/ directory.

The resume prefix is resolved at runtime via scripts/config.py so no personal
name is hard-coded in this file (keeps the guard green).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = REPO_ROOT / "evals"
RUN_EVAL = EVALS_DIR / "run_eval.py"

# Resolve the resume prefix the same way the subprocess will, so test
# fixtures can name resume files correctly without hard-coding a personal name.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from config import load_profile, resume_glob_prefix  # noqa: E402

RESUME_PREFIX = resume_glob_prefix()
USER_EMAIL = load_profile()["user_email"]

# build_resume_pdf (reportlab-dependent) is imported lazily inside the
# resume-export green-path test so a machine without reportlab skips that one
# test instead of failing collection for the whole eval suite — the same
# graceful degradation the resume-export step itself promises.

ROLE_FOLDER = "Acme - Senior Agent Builder"
PIPELINE_ROLE = "Acme — Senior Agent Builder"

PIPELINE_HEADER = "| Role | Stage | Next action | Date | Contacts | Folder |"
PIPELINE_SEP = "| --- | --- | --- | --- | --- | --- |"

# Synthetic people used by the contacts-ledger / emails / outreach fixtures.
# Kept consistent across builders so cross-skill references resolve.
PEOPLE = {
    "recruiter": ("Jordan Reyes", "jordan.reyes@acme.com"),
    "hm": ("Morgan Patel", "morgan.patel@acme.com"),
    "peer": ("Casey Singh", "casey.singh@acme.com"),
}


def _run_eval(args: list[str]) -> subprocess.CompletedProcess:
    """Run run_eval.py via subprocess, returning the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(RUN_EVAL), *args],
        capture_output=True,
        text=True,
    )


def _build_good_intake_workspace(workspace: Path) -> None:
    """Build a workspace that passes all four intake clauses."""
    roles_dir = workspace / "Roles"
    role = roles_dir / ROLE_FOLDER
    role.mkdir(parents=True)
    (role / "Job Description.md").write_text(
        "# Acme — Senior Agent Builder\n\nA full JD here.\n",
        encoding="utf-8",
    )
    pipeline = workspace / "Pipeline.md"
    pipeline.write_text(
        "## Active\n\n"
        f"{PIPELINE_HEADER}\n{PIPELINE_SEP}\n\n"
        "## Considering / not yet applied\n\n"
        f"{PIPELINE_HEADER}\n{PIPELINE_SEP}\n"
        f"| **{PIPELINE_ROLE}** | Considering — JD reviewed | Review resume | "
        f"2026-07-10 | recruiter@acme.com | [[{ROLE_FOLDER}]] |\n",
        encoding="utf-8",
    )


def _build_broken_intake_workspace(workspace: Path) -> None:
    """Build a workspace that fails intake-C2 (missing Job Description.md)."""
    roles_dir = workspace / "Roles"
    role = roles_dir / ROLE_FOLDER
    role.mkdir(parents=True)
    # No Job Description.md — C2 will fail.
    pipeline = workspace / "Pipeline.md"
    pipeline.write_text(
        "## Active\n\n"
        f"{PIPELINE_HEADER}\n{PIPELINE_SEP}\n\n"
        "## Considering / not yet applied\n\n"
        f"{PIPELINE_HEADER}\n{PIPELINE_SEP}\n"
        f"| **{PIPELINE_ROLE}** | Considering — JD reviewed | Review resume | "
        f"2026-07-10 | recruiter@acme.com | [[{ROLE_FOLDER}]] |\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Test a: --list output contains both skills
# ---------------------------------------------------------------------------

def test_list_output_contains_all_nine_skills():
    result = _run_eval(["--list"])
    assert result.returncode == 0, f"--list failed: {result.stderr}"
    expected = {
        "interview-prep-intake", "tailor-resume", "classify", "resume-export",
        "apply-packet", "find-contacts", "enrich-contacts", "verify-emails",
        "write-outreach",
    }
    listed = {ln.strip() for ln in result.stdout.splitlines() if ln.strip()}
    missing = expected - listed
    assert not missing, f"--list missing skills: {missing}; got:\n{result.stdout}"


# ---------------------------------------------------------------------------
# Test b: GOOD intake workspace → exit 0
# ---------------------------------------------------------------------------

def test_good_intake_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_intake_workspace(workspace)

    result = _run_eval(["interview-prep-intake", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Test c: BROKEN intake workspace → exit 1, output names intake-C2
# ---------------------------------------------------------------------------

def test_broken_intake_workspace_exits_one_names_c2(tmp_path):
    workspace = tmp_path / "ws"
    _build_broken_intake_workspace(workspace)

    result = _run_eval(["interview-prep-intake", "--workspace", str(workspace)])
    assert result.returncode == 1, (
        f"Expected exit 1 for broken workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "intake-C2" in result.stdout, (
        f"Output must name the failed clause intake-C2; got:\n{result.stdout}"
    )
    assert "FAIL" in result.stdout


def test_intake_duplicate_pipeline_row_fails_idempotency_clause(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_intake_workspace(workspace)
    pipeline = workspace / "Pipeline.md"
    row = next(line for line in pipeline.read_text(encoding="utf-8").splitlines()
               if PIPELINE_ROLE in line)
    pipeline.write_text(pipeline.read_text(encoding="utf-8") + row + "\n", encoding="utf-8")
    result = _run_eval(["interview-prep-intake", "--workspace", str(workspace)])
    assert result.returncode == 1
    assert "intake-C4" in result.stdout


# ---------------------------------------------------------------------------
# Test d: --json output parses, 4 entries for intake, each with required keys
# ---------------------------------------------------------------------------

def test_json_output_parses_with_required_keys(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_intake_workspace(workspace)

    result = _run_eval(["interview-prep-intake", "--workspace", str(workspace), "--json"])
    assert result.returncode == 0, f"--json run failed: {result.stderr}"

    data = json.loads(result.stdout)
    assert isinstance(data, list), f"Expected JSON array; got {type(data)}"
    assert len(data) == 4, f"Expected 4 clause results; got {len(data)}"
    for entry in data:
        assert "id" in entry, f"Missing 'id' key in {entry}"
        assert "description" in entry, f"Missing 'description' key in {entry}"
        assert "passed" in entry, f"Missing 'passed' key in {entry}"
        assert entry["passed"] is True, f"Expected all passed=True; got {entry}"
    ids = [e["id"] for e in data]
    assert ids == ["intake-C1", "intake-C2", "intake-C3", "intake-C4"], (
        f"Expected clause ids in order; got {ids}"
    )


# ---------------------------------------------------------------------------
# Test e: bad skill name → exit 2
# ---------------------------------------------------------------------------

def test_bad_skill_name_exits_two(tmp_path):
    result = _run_eval(["nonexistent-skill", "--workspace", str(tmp_path)])
    assert result.returncode == 2, (
        f"Expected exit 2 for bad skill name; got {result.returncode}"
    )
    assert "nonexistent-skill" in result.stderr


# ---------------------------------------------------------------------------
# Test f: tailor-resume against a good fixture workspace → exit 0
# ---------------------------------------------------------------------------

def test_tailor_resume_good_workspace_exits_zero(tmp_path):
    """Build a workspace with a clean resume and structured runtime gaps."""
    workspace = tmp_path / "ws"
    roles_dir = workspace / "Roles"
    role = roles_dir / ROLE_FOLDER
    role.mkdir(parents=True)

    # JD with the deliberate unmatched requirement.
    (role / "Job Description.md").write_text(
        "# Acme — Senior Agent Builder\n\n"
        "Must have an advanced orbital mechanics certification.\n",
        encoding="utf-8",
    )
    # Resume matching the profile prefix, clean of all markers.
    resume_name = f"{RESUME_PREFIX}Acme Senior Agent Builder.md"
    (role / resume_name).write_text(
        f"# Tailored Resume\n\n{USER_EMAIL}\n\n"
        + ("Senior agent builder with production LLM experience. " * 12),
        encoding="utf-8",
    )
    # Runtime classification artifact records the no-canonical-match gap.
    (role / ".classification.json").write_text(
        json.dumps({"gaps": [{
            "source": "tailor-resume", "kind": "no-canonical-match",
            "detail": "fusion reactor requirement has no canonical claim",
        }]}),
        encoding="utf-8",
    )

    result = _run_eval(["tailor-resume", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good tailor-resume workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Test g: tailor-resume with placeholder leak → exit 1, names C3
# ---------------------------------------------------------------------------

def test_tailor_resume_placeholder_leak_exits_one(tmp_path):
    workspace = tmp_path / "ws"
    roles_dir = workspace / "Roles"
    role = roles_dir / ROLE_FOLDER
    role.mkdir(parents=True)
    (role / "Job Description.md").write_text(
        "# Acme — Senior Agent Builder\n", encoding="utf-8",
    )
    resume_name = f"{RESUME_PREFIX}Acme Senior Agent Builder.md"
    # Contains a placeholder leak — C3 should catch [NUMBER?].
    (role / resume_name).write_text(
        "# Resume\n\nImproved throughput by [NUMBER?] percent.\n", encoding="utf-8",
    )

    result = _run_eval(["tailor-resume", "--workspace", str(workspace)])
    assert result.returncode == 1, (
        f"Expected exit 1 for placeholder leak; got {result.returncode}\n"
        f"stdout:\n{result.stdout}"
    )
    assert "tailor-resume-C3" in result.stdout


# ===========================================================================
# Task 2: builders + green-path tests for the remaining seven skills.
# ===========================================================================

def _role_dir(workspace: Path) -> Path:
    """Create and return the Acme role folder in the workspace."""
    role = workspace / "Roles" / ROLE_FOLDER
    role.mkdir(parents=True, exist_ok=True)
    return role


def _write_ledger(role: Path, *, enrich_row: bool = False) -> None:
    """Write a scored .contacts-ledger.md with the fixture column set.

    If enrich_row is True, append a row whose Source cell records enrichment.
    """
    recruiter_name, recruiter_email = PEOPLE["recruiter"]
    hm_name, hm_email = PEOPLE["hm"]
    peer_name, peer_email = PEOPLE["peer"]
    header = (
        "| Name | Category | Practice (0-3) | Practice evidence | Loc (0-2) | "
        "Title (0-2) | Tenure (0-1) | Snr (0-1) | Total | Conn-degree | Source | "
        "Provenance | Rank | Email (inferred) | Confidence |"
    )
    divider = "|" + "|".join(["------"] * 15) + "|"
    rows = [
        f"| {recruiter_name} | recruiter | 3 | \"Talent Acquisition\" | 2 | 2 | 1 | 1 | 9 | 2nd | search | | 1 | {recruiter_email} | Medium (inferred) |",
        f"| {hm_name} | hiring manager | 3 | \"Head of AI Platform\" | 1 | 2 | 1 | 1 | 8 | 2nd | search | | 2 | {hm_email} | Medium (inferred) |",
    ]
    if enrich_row:
        rows.append(
            f"| {peer_name} | peer | 2 | \"Senior Agent Builder\" | 1 | 1 | 1 | 1 | 6 | 2nd | enrich | activity | 3 | {peer_email} | Medium (inferred) |"
        )
    body = "# Contacts Ledger — Acme\n\n" + "\n".join([header, divider, *rows]) + "\n"
    (role / ".contacts-ledger.md").write_text(body, encoding="utf-8")


def _write_verified_emails(role: Path) -> None:
    """Write Verified Emails.md with one row per contact, each tagged inferred."""
    rows = []
    for _, (name, email) in sorted(PEOPLE.items()):
        rows.append(f"| {name} | {email} | inferred |")
    body = (
        "# Verified Emails — Acme\n\n"
        "| Name | Email | Status |\n"
        "|------|-------|--------|\n"
        + "\n".join(rows) + "\n"
    )
    (role / "Verified Emails.md").write_text(body, encoding="utf-8")


_MINIMAL_RESUME_MD = f"""\
Jordan Agent
{USER_EMAIL} | (555) 123-4567 | linkedin.com/in/jordan-agent

## PROFESSIONAL EXPERIENCE

**Senior Agent Builder | Acme | 2023-Present**
- Designed and shipped production LLM agents with tool-use orchestration.
- Built RAG pipelines grounded in customer data; owned chunking and retrieval.

**Agent Engineer | Beta Corp | 2021-2023**
- Wrote evaluation suites that caught regressions before customers did.

## SKILLS

Python, LLM orchestration, RAG, MCP, evaluation harnesses

## EDUCATION

B.S. Computer Science — State University, 2021
"""


# ---------------------------------------------------------------------------
# classify — green path
# ---------------------------------------------------------------------------

def _build_good_classify_workspace(workspace: Path) -> None:
    role = _role_dir(workspace)
    (role / "Job Description.md").write_text(
        "Design and ship production LLM agents. Prompt scaffolds and tool-use "
        "orchestration. Build RAG pipelines grounded in customer data. Write "
        "evaluation suites that catch regressions.",
        encoding="utf-8",
    )
    (role / ".classification.json").write_text(
        json.dumps({
            "themes": [
                {"tag": "agents", "evidence": "design and ship production LLM agents"},
                {"tag": "LLM-orchestration", "evidence": "prompt scaffolds and tool-use orchestration"},
                {"tag": "RAG", "evidence": "build RAG pipelines grounded in customer data"},
                {"tag": "evaluation", "evidence": "write evaluation suites that catch regressions"},
            ],
            "archetype": "agent-builder",
            "archetype_rationale": "Hands-on agent design, build, and operation.",
            "notes": "Hard gate: shipped a production LLM agent.",
            "classified_ts": "2026-07-10",
            "gaps": [],
        }, indent=2),
        encoding="utf-8",
    )


def test_classify_good_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_classify_workspace(workspace)
    result = _run_eval(["classify", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good classify workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# classify — red path (bad theme, off-vocab)
# ---------------------------------------------------------------------------

def test_classify_bad_theme_exits_one_names_c3(tmp_path):
    """An off-vocab theme must fail classify-C3 (themes within the vocab)."""
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    (role / ".classification.json").write_text(
        json.dumps({
            "themes": [
                {"tag": "agents", "evidence": "design and ship production LLM agents"},
                {"tag": "quantum-computing", "evidence": "not a real theme in the vocab"},
            ],
            "archetype": "agent-builder",
            "classified_ts": "2026-07-10",
        }, indent=2),
        encoding="utf-8",
    )
    result = _run_eval(["classify", "--workspace", str(workspace)])
    assert result.returncode == 1, (
        f"Expected exit 1 for bad-theme classify; got {result.returncode}\n"
        f"stdout:\n{result.stdout}"
    )
    assert "classify-C3" in result.stdout
    assert "FAIL" in result.stdout


def test_classify_rejects_unresolved_evidence_and_incomplete_metadata(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_classify_workspace(workspace)
    role = _role_dir(workspace)
    path = role / ".classification.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["themes"][0]["evidence"] = "evidence absent from the JD"
    data["themes"] = data["themes"][:3]
    data["archetype_rationale"] = ""
    data["classified_ts"] = "not-a-date"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = _run_eval(["classify", "--workspace", str(workspace), "--json"])
    assert result.returncode == 1
    clauses = {item["id"]: item["status"] for item in json.loads(result.stdout)}
    for clause_id in ("classify-C5", "classify-C6", "classify-C7", "classify-C8"):
        assert clauses[clause_id] == "FAIL"


# ---------------------------------------------------------------------------
# resume-export — green path (PDF built via build_resume_pdf at test time)
# ---------------------------------------------------------------------------

def test_resume_export_good_workspace_exits_zero(tmp_path):
    """Build a real one-page PDF via build_resume_pdf.py, then verify."""
    pytest.importorskip("reportlab", reason="resume-export fixture needs reportlab")
    import build_resume_pdf

    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    resume_md = role / f"{RESUME_PREFIX}Acme Senior Agent Builder.md"
    resume_md.write_text(_MINIMAL_RESUME_MD, encoding="utf-8")
    pdf_path = resume_md.with_suffix(".pdf")
    pages, title_leak, _ = build_resume_pdf.build_pdf(resume_md, pdf_path)
    assert pages == 1, f"Fixture resume should be one page; got {pages}"

    result = _run_eval(["resume-export", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good resume-export workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# apply-packet — green path
# ---------------------------------------------------------------------------

def _build_good_apply_packet_workspace(workspace: Path) -> None:
    role = _role_dir(workspace)
    (role / "Application Answers.md").write_text(
        "# Application Answers — Acme\n\n"
        "## Salary expectation\n\n$X\n\n"
        "## Work authorization\n\nauthorized, no sponsorship\n\n"
        "## Notice period\n\n2 weeks\n",
        encoding="utf-8",
    )
    (role / ".apply-packet.json").write_text(
        json.dumps({
            "state": "queued",
            "remote_dir": "Apply Queue_test/acme",
            "answers_md": "Application Answers.md",
            "ts": "2026-07-10",
        }, indent=2),
        encoding="utf-8",
    )


def test_apply_packet_good_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_apply_packet_workspace(workspace)
    result = _run_eval(["apply-packet", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good apply-packet workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# find-contacts — green path
# ---------------------------------------------------------------------------

def test_find_contacts_good_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role)
    result = _run_eval(["find-contacts", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good find-contacts workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# enrich-contacts — green path
# ---------------------------------------------------------------------------

def test_enrich_contacts_good_workspace_exits_zero(tmp_path):
    """Ledger with enrichment provenance and source-backed hooks passes."""
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role, enrich_row=True)
    recruiter_name, _ = PEOPLE["recruiter"]
    hm_name, _ = PEOPLE["hm"]
    peer_name, _ = PEOPLE["peer"]
    (role / ".contacts-ledger.md").write_text(
        (role / ".contacts-ledger.md").read_text(encoding="utf-8")
        + f"\n## hooks\n\n"
          f"- {recruiter_name} — replied to intro, offered a chat next week.\n"
          f"- {hm_name} — was referenced by {peer_name} in a thread.\n",
        encoding="utf-8",
    )
    result = _run_eval(["enrich-contacts", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good enrich-contacts workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


def test_enrich_missing_hooks_requires_explicit_trace_gap(tmp_path):
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role, enrich_row=True)
    failed = _run_eval(["enrich-contacts", "--workspace", str(workspace)])
    assert failed.returncode == 1
    assert "enrich-contacts-C3" in failed.stdout

    trace = workspace / "runs" / "fixture-run" / "trace.jsonl"
    trace.parent.mkdir(parents=True)
    trace.write_text(json.dumps({
        "event": "step_end",
        "gaps": [{"source": "enrich-contacts", "kind": "no-activity",
                  "detail": "fixture profiles exposed no relevant activity"}],
    }) + "\n", encoding="utf-8")
    passed = _run_eval(["enrich-contacts", "--workspace", str(workspace)])
    assert passed.returncode == 0, passed.stdout


# ---------------------------------------------------------------------------
# verify-emails — green path
# ---------------------------------------------------------------------------

def test_verify_emails_good_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role)
    _write_verified_emails(role)
    result = _run_eval(["verify-emails", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good verify-emails workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# write-outreach — green path
# ---------------------------------------------------------------------------

def _build_good_write_outreach_workspace(workspace: Path) -> None:
    role = _role_dir(workspace)
    _write_ledger(role)
    _write_verified_emails(role)
    recruiter_name, recruiter_email = PEOPLE["recruiter"]
    hm_name, hm_email = PEOPLE["hm"]
    (role / "Cold Outreach.md").write_text(
        "# Cold Outreach — Acme\n\n"
        f"## Intro — Recruiter\n\n"
        f"To: {recruiter_email}\n\n"
        f"Subject: Acme Senior Agent Builder — intro\n\n"
        f"Hi {recruiter_name.split()[0]}, saw the Senior Agent Builder role.\n\n"
        f"## Intro — Hiring Manager\n\n"
        f"To: {hm_email}\n\n"
        f"Subject: Acme Senior Agent Builder — building agents in production\n\n"
        f"Hi {hm_name.split()[0]}, I build production LLM agents and saw your role.\n",
        encoding="utf-8",
    )
    (role / ".drafts.json").write_text(json.dumps([
        {"id": "fixture-recruiter", "toRecipients": [recruiter_email], "sent": False},
        {"id": "fixture-hm", "toRecipients": [hm_email], "sent": False},
    ]), encoding="utf-8")


def test_write_outreach_good_workspace_exits_zero(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_write_outreach_workspace(workspace)
    result = _run_eval(["write-outreach", "--workspace", str(workspace)])
    assert result.returncode == 0, (
        f"Expected exit 0 for good write-outreach workspace; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# write-outreach — red path (placeholder leak)
# ---------------------------------------------------------------------------

def test_write_outreach_placeholder_leak_exits_one(tmp_path):
    """A [NUMBER?] placeholder in Cold Outreach.md must fail write-outreach-C3."""
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role)
    _write_verified_emails(role)
    recruiter_name, recruiter_email = PEOPLE["recruiter"]
    hm_name, hm_email = PEOPLE["hm"]
    (role / "Cold Outreach.md").write_text(
        "# Cold Outreach — Acme\n\n"
        f"## Intro — Recruiter\n\nTo: {recruiter_email}\n\n"
        f"Hi {recruiter_name.split()[0]}, improved throughput by [NUMBER?] percent.\n\n"
        f"## Intro — Hiring Manager\n\nTo: {hm_email}\n\n"
        f"Hi {hm_name.split()[0]}, saw your role.\n",
        encoding="utf-8",
    )
    result = _run_eval(["write-outreach", "--workspace", str(workspace)])
    assert result.returncode == 1, (
        f"Expected exit 1 for placeholder leak; got {result.returncode}\n"
        f"stdout:\n{result.stdout}"
    )
    assert "write-outreach-C3" in result.stdout
    assert "FAIL" in result.stdout


# ---------------------------------------------------------------------------
# runner robustness — a crashing verifier is exit 4, not a fake clause failure
# ---------------------------------------------------------------------------

def test_crashing_verifier_exits_4_with_clean_message(tmp_path):
    crash_dir = EVALS_DIR / "zz-crash-fixture"
    crash_dir.mkdir()
    try:
        (crash_dir / "verify.py").write_text(
            'def verify(workspace):\n    raise RuntimeError("boom")\n', encoding="utf-8"
        )
        result = _run_eval(["zz-crash-fixture", "--workspace", str(tmp_path)])
        assert result.returncode == 4
        assert "crashed" in result.stderr
        assert "Traceback" not in result.stderr
    finally:
        import shutil
        shutil.rmtree(crash_dir, ignore_errors=True)


def test_explicit_role_parameter_removes_acme_dependency(tmp_path):
    workspace = tmp_path / "ws"
    role = workspace / "Roles" / "Orbit - Platform Engineer"
    role.mkdir(parents=True)
    evidence = [
        ("platform", "owns platform reliability"),
        ("ML-pipeline", "builds machine learning pipelines"),
        ("engineering-rigor", "tests production systems"),
        ("cross-functional", "partners across product and engineering"),
    ]
    (role / "Job Description.md").write_text(
        ". ".join(text for _, text in evidence), encoding="utf-8"
    )
    (role / ".classification.json").write_text(json.dumps({
        "themes": [{"tag": tag, "evidence": text} for tag, text in evidence],
        "archetype": "platform / ML engineering",
        "archetype_rationale": "Platform ownership is the primary requirement.",
        "classified_ts": "2026-07-11",
        "gaps": [],
    }), encoding="utf-8")
    result = _run_eval([
        "classify", "--workspace", str(workspace),
        "--role", "Roles/Orbit - Platform Engineer",
    ])
    assert result.returncode == 0, result.stdout + result.stderr


def test_live_only_contact_clause_is_blocked_not_passed(tmp_path):
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role)
    result = _run_eval(["find-contacts", "--workspace", str(workspace), "--json"])
    assert result.returncode == 0
    clauses = {item["id"]: item for item in json.loads(result.stdout)}
    assert clauses["find-contacts-C5"]["status"] == "BLOCKED"
    assert clauses["find-contacts-C5"]["passed"] is False


def test_eval_enriched_sidecar_cannot_mask_missing_enrichment(tmp_path):
    workspace = tmp_path / "ws"
    role = _role_dir(workspace)
    _write_ledger(role, enrich_row=False)
    result = _run_eval(["enrich-contacts", "--workspace", str(workspace)])
    assert result.returncode == 1
    assert "enrich-contacts-C2" in result.stdout


def test_sent_fixture_draft_fails_never_send_clause(tmp_path):
    workspace = tmp_path / "ws"
    _build_good_write_outreach_workspace(workspace)
    role = _role_dir(workspace)
    (role / ".drafts.json").write_text(
        json.dumps([{"id": "bad", "sent": True}]), encoding="utf-8"
    )
    result = _run_eval(["write-outreach", "--workspace", str(workspace)])
    assert result.returncode == 1
    assert "write-outreach-C4" in result.stdout


def _build_all_behavior_workspace(workspace: Path) -> None:
    _build_good_intake_workspace(workspace)
    _build_good_classify_workspace(workspace)
    role = _role_dir(workspace)
    resume = role / f"{RESUME_PREFIX}Acme Senior Agent Builder.md"
    resume.write_text(_MINIMAL_RESUME_MD, encoding="utf-8")
    resume.with_suffix(".pdf").write_bytes(b"%PDF-1.4\n/Type /Page \n")
    _build_good_apply_packet_workspace(workspace)
    _build_good_write_outreach_workspace(workspace)
    _write_ledger(role, enrich_row=True)
    recruiter_name, _ = PEOPLE["recruiter"]
    (role / ".contacts-ledger.md").write_text(
        (role / ".contacts-ledger.md").read_text(encoding="utf-8")
        + f"\n## hooks\n\n- {recruiter_name} — source-backed activity.\n",
        encoding="utf-8",
    )
    _write_verified_emails(role)


def test_all_runs_nine_contracts_and_tolerates_blocked_live_clauses(tmp_path):
    workspace = tmp_path / "ws"
    _build_all_behavior_workspace(workspace)
    result = _run_eval(["--all", "--workspace", str(workspace), "--json"])
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["skills"]) == 9
    statuses = {
        clause["status"]
        for clauses in payload["skills"].values()
        for clause in clauses
    }
    assert "BLOCKED" in statuses
    assert "FAIL" not in statuses


def test_all_exits_nonzero_for_local_clause_failure(tmp_path):
    workspace = tmp_path / "ws"
    _build_all_behavior_workspace(workspace)
    (workspace / "Roles" / ROLE_FOLDER / "Job Description.md").unlink()
    result = _run_eval(["--all", "--workspace", str(workspace)])
    assert result.returncode == 1
    assert "intake-C2" in result.stdout
