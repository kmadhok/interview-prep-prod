"""Tests for scripts/config.py — profile loading and workspace resolution."""
from pathlib import Path

import pytest

import config


def test_repo_root_is_parent_of_scripts():
    assert (config.REPO_ROOT / "scripts" / "config.py").exists()


def test_workspace_is_repo_root_slash_workspace():
    assert config.WORKSPACE == config.REPO_ROOT / "workspace"


def test_load_profile_reads_known_keys():
    profile = config.load_profile()
    assert profile["user_name"], "user_name must be non-empty"
    assert "{company}" in profile["resume_filename_pattern"]
    assert "{name}" in profile["resume_filename_pattern"]


def test_load_profile_from_explicit_path(tmp_path):
    p = tmp_path / "profile.yaml"
    p.write_text(
        "user_name: Test User\n"
        "user_email: test@example.com\n"
        "resume_filename_pattern: \"{name} Resume - {company} {role}\"\n"
        "timezone: America/Chicago\n",
        encoding="utf-8",
    )
    profile = config.load_profile(p)
    assert profile["user_name"] == "Test User"
    assert profile["user_email"] == "test@example.com"


def test_load_profile_ignores_comments_and_blanks(tmp_path):
    p = tmp_path / "profile.yaml"
    p.write_text("# a comment\n\nuser_name: X\n", encoding="utf-8")
    assert config.load_profile(p)["user_name"] == "X"


def test_load_profile_missing_file_raises_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        config.load_profile(tmp_path / "nope.yaml")
    assert "onboard" in str(exc.value).lower()


def test_resume_filename():
    profile = {"user_name": "Test User",
               "resume_filename_pattern": "{name} Resume - {company} {role}"}
    assert (config.resume_filename(profile, "Acme", "Data PM")
            == "Test User Resume - Acme Data PM")
