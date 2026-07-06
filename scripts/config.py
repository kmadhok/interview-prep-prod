"""Load profile.yaml and resolve workspace paths.

profile.yaml is deliberately flat (key: value lines only) so it can be parsed
with stdlib alone — no PyYAML dependency. Skills read the same file directly.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = REPO_ROOT / "workspace"
PROFILE_PATH = REPO_ROOT / "profile.yaml"


def load_profile(path: Path | None = None) -> dict[str, str]:
    """Parse the flat key: value profile file. Comments (#) and blanks ignored."""
    path = path or PROFILE_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run the /onboard skill to create your profile."
        )
    profile: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        profile[key.strip()] = value.strip().strip('"').strip("'")
    return profile


def resume_filename(profile: dict[str, str], company: str, role: str) -> str:
    """Render the resume filename (no extension) from the profile pattern."""
    return profile["resume_filename_pattern"].format(
        name=profile["user_name"], company=company, role=role
    )
