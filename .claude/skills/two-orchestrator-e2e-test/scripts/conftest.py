import sys
from pathlib import Path

import pytest

# Put config.py (repo-root scripts/) on sys.path so verify_artifacts can import
# it during collection. This conftest sits at .claude/skills/<skill>/scripts/,
# repo root is parents[4].
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))

import verify_artifacts  # noqa: E402  (patched below at its import site)

# Synthetic profile: pins the code-under-test to a name-agnostic user so tests
# never read the real profile.yaml, keeping fixtures clean and the guard green.
TEST_PROFILE = {
    "user_name": "Test User",
    "user_email": "test.user@example.com",
    "resume_filename_pattern": "{name} Resume - {company} {role}",
    "timezone": "America/Chicago",
}


@pytest.fixture(autouse=True)
def _stub_profile(monkeypatch):
    stub = lambda *a, **k: dict(TEST_PROFILE)
    # verify_artifacts did `from config import load_profile, resume_glob_prefix`,
    # so those names are bound in verify_artifacts's namespace — patch there.
    monkeypatch.setattr(verify_artifacts, "load_profile", stub)
    monkeypatch.setattr(verify_artifacts, "resume_glob_prefix",
                        lambda profile=None: f"{TEST_PROFILE['user_name']} Resume - ")
