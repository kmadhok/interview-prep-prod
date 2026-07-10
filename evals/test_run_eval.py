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
from config import resume_glob_prefix  # noqa: E402

RESUME_PREFIX = resume_glob_prefix()

ROLE_FOLDER = "Acme - Senior Agent Builder"
PIPELINE_ROLE = "Acme — Senior Agent Builder"

PIPELINE_HEADER = "| Role | Stage | Next action | Date | Contacts | Folder |"
PIPELINE_SEP = "| --- | --- | --- | --- | --- | --- |"


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

def test_list_output_contains_skills():
    result = _run_eval(["--list"])
    assert result.returncode == 0, f"--list failed: {result.stderr}"
    assert "interview-prep-intake" in result.stdout
    assert "tailor-resume" in result.stdout


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
    """Build a workspace with a resume matching the profile prefix, no
    quarantine markers, no placeholder leaks, and a gaps file (JD has
    'fusion reactors'). All four tailor-resume clauses pass."""
    workspace = tmp_path / "ws"
    roles_dir = workspace / "Roles"
    role = roles_dir / ROLE_FOLDER
    role.mkdir(parents=True)

    # JD with the deliberate unmatched requirement.
    (role / "Job Description.md").write_text(
        "# Acme — Senior Agent Builder\n\n"
        "Must have 10+ years operating fusion reactors.\n",
        encoding="utf-8",
    )
    # Resume matching the profile prefix, clean of all markers.
    resume_name = f"{RESUME_PREFIX}Acme Senior Agent Builder.md"
    (role / resume_name).write_text(
        "# Tailored Resume\n\nSenior agent builder with production LLM experience.\n",
        encoding="utf-8",
    )
    # Gaps file recording the no-canonical-match gap.
    (role / ".eval-gaps.json").write_text(
        json.dumps([{
            "source": "resume",
            "kind": "no-canonical-match",
            "detail": "JD requires 10+ years operating fusion reactors; no canonical claim matches.",
        }]),
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
