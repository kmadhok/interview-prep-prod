import os
import sys

import pytest

# Put this package dir on sys.path so the test modules' top-level imports
# (`import job_parser`, `import dedupe`) resolve when pytest is run from the
# repo root (e.g. in CI), not only from inside scripts/drip_runner/.
sys.path.insert(0, os.path.dirname(__file__))
# The parent scripts/ dir holds config.py, imported by apply_packet /
# prepped_not_applied for the resume filename prefix.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config  # noqa: E402  (after sys.path bootstrap)

TEST_PROFILE = {
    "user_name": "Test User",
    "user_email": "test.user@example.com",
    "resume_filename_pattern": "{name} Resume - {company} {role}",
    "timezone": "America/Chicago",
}


@pytest.fixture(autouse=True)
def _stub_profile(monkeypatch):
    """Pin the profile to a synthetic user so tests never read the real
    profile.yaml — keeps fixtures name-agnostic and the guard green."""
    monkeypatch.setattr(config, "load_profile", lambda *a, **k: dict(TEST_PROFILE))
