"""Regression tests for role_folder.py — canonical naming + ensure CLI.

Drives the real CLI via subprocess. Synthetic data only — no real
names/emails/paths (guard scans scripts/).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("role_folder.py")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


# ---------------------------------------------------------------------------
# 1. name strips forbidden chars + collapses whitespace
# ---------------------------------------------------------------------------

def test_name_strips_forbidden_and_collapses_whitespace():
    # "Acme/Sub" → "AcmeSub", "AI:  Builder?" → "AI  Builder" → "AI Builder"
    r = _run("name", "--company", "Acme/Sub", "--role", "AI:  Builder?")
    assert r.returncode == 0, f"name failed: {r.stderr}"
    name = r.stdout.strip()
    # Forbidden chars (/:*?"<>|) removed, whitespace runs collapsed
    assert "/" not in name
    assert ":" not in name
    assert "?" not in name
    assert "  " not in name, f"whitespace not collapsed: {name!r}"
    assert name == "AcmeSub - AI Builder", f"got {name!r}"


# ---------------------------------------------------------------------------
# 2. ensure creates workspace/Roles/<name> and prints CREATED
# ---------------------------------------------------------------------------

def test_ensure_creates_folder(tmp_path):
    workspace = tmp_path / "ws"
    (workspace / "Roles").mkdir(parents=True)

    r = _run("ensure", "--workspace", str(workspace),
             "--company", "Acme", "--role", "Agent Builder")
    assert r.returncode == 0, f"ensure failed: {r.stderr}"
    assert "CREATED" in r.stdout, f"expected CREATED in stdout: {r.stdout!r}"
    assert (workspace / "Roles" / "Acme - Agent Builder").is_dir()


# ---------------------------------------------------------------------------
# 3. ensure again → EXISTS, exit 0
# ---------------------------------------------------------------------------

def test_ensure_again_exists(tmp_path):
    workspace = tmp_path / "ws"
    (workspace / "Roles").mkdir(parents=True)

    _run("ensure", "--workspace", str(workspace),
         "--company", "Acme", "--role", "Agent Builder")
    r = _run("ensure", "--workspace", str(workspace),
             "--company", "Acme", "--role", "Agent Builder")
    assert r.returncode == 0, f"second ensure failed: {r.stderr}"
    assert "EXISTS" in r.stdout, f"expected EXISTS in stdout: {r.stdout!r}"


# ---------------------------------------------------------------------------
# 4. archived collision → ARCHIVED, exit 3
# ---------------------------------------------------------------------------

def test_ensure_archived_collision_exit3(tmp_path):
    workspace = tmp_path / "ws"
    (workspace / "Roles").mkdir(parents=True)
    (workspace / "_Archived" / "Acme - Agent Builder").mkdir(parents=True)

    r = _run("ensure", "--workspace", str(workspace),
             "--company", "Acme", "--role", "Agent Builder")
    assert r.returncode == 3, f"expected exit 3 for archived, got {r.returncode}: {r.stdout}{r.stderr}"
    assert "ARCHIVED" in r.stdout, f"expected ARCHIVED in stdout: {r.stdout!r}"
    # Active folder must NOT have been created
    assert not (workspace / "Roles" / "Acme - Agent Builder").exists()
