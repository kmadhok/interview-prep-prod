#!/usr/bin/env python3
"""Verify an onboarded repository and its canonical behavior fixture."""
from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from build_fixture_workspace import build_fixture_workspace  # noqa: E402
from config import load_profile  # noqa: E402

CANONICAL_MASTERS = (
    "Resume Achievements Master.md",
    "Resume Claims To Verify.md",
    "Master Story Bank.md",
    "Tell Me About Yourself - Master.md",
    "AI Build Walkthrough - Master.md",
    "Demo Portfolio.md",
    "Outreach Templates.md",
    "Job Search Target Profile.md",
    "Application Profile.md",
)
DEFAULT_LINKEDIN_ENDPOINT = "http://127.0.0.1:8765/mcp"


@dataclass(frozen=True)
class Check:
    """One immutable setup-gate verdict with its user-facing diagnostic."""
    status: str
    name: str
    detail: str


def _template_keys(path: Path) -> list[str]:
    return list(load_profile(path).keys())


def _check_profile(repo_root: Path) -> tuple[dict[str, str], Check]:
    profile_path = repo_root / "profile.yaml"
    template_path = repo_root / "templates" / "profile.yaml"
    if not profile_path.is_file():
        return {}, Check("FAIL", "profile", "profile.yaml missing; run /onboard")
    if not template_path.is_file():
        return {}, Check("FAIL", "profile", "templates/profile.yaml missing")
    try:
        profile = load_profile(profile_path)
        required = _template_keys(template_path)
    except (OSError, ValueError) as exc:
        return {}, Check("FAIL", "profile", f"could not parse profile.yaml: {exc}")
    missing = [key for key in required if not profile.get(key, "").strip()]
    if missing:
        return profile, Check(
            "FAIL", "profile", "missing or blank keys: " + ", ".join(missing)
        )
    return profile, Check("PASS", "profile", f"{len(required)} required keys populated")


def _check_workspace(repo_root: Path) -> list[Check]:
    workspace = repo_root / "workspace"
    templates = repo_root / "templates"
    if not workspace.is_dir():
        return [Check("FAIL", "workspace", "workspace/ missing; run /onboard")]
    checks: list[Check] = []
    for name in CANONICAL_MASTERS:
        live = workspace / name
        starter = templates / name
        label = f"workspace/{name}"
        if not starter.is_file():
            checks.append(Check("FAIL", label, f"template missing: templates/{name}"))
            continue
        if not live.is_file() or not live.read_text(encoding="utf-8").strip():
            checks.append(Check("FAIL", label, "missing or blank; run /onboard"))
            continue
        if live.read_bytes() == starter.read_bytes():
            checks.append(Check("FAIL", label, "still identical to blank starter; finish /onboard"))
            continue
        checks.append(Check("PASS", label, "present and customized"))
    return checks


def _check_reportlab() -> Check:
    try:
        importlib.import_module("reportlab")
    except (ImportError, OSError) as exc:
        return Check(
            "WARN",
            "reportlab",
            f"not importable ({exc}); PDF export will degrade gracefully "
            "(optional: python3 -m pip install reportlab)",
        )
    else:
        return Check("PASS", "reportlab", "PDF export available")


def _check_linkedin(endpoint: str, *, skip_live: bool) -> Check:
    if skip_live:
        return Check("SKIP", "LinkedIn MCP", "live check skipped by --skip-live")
    request = Request(endpoint, headers={"Accept": "application/json, text/event-stream"})
    try:
        with urlopen(request, timeout=3) as response:
            status = response.status
    except HTTPError as exc:
        # Streamable HTTP MCP endpoints normally reject a bare GET while proving
        # that the configured daemon and route are alive.
        status = exc.code
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return Check(
            "FAIL",
            "LinkedIn MCP",
            f"unreachable at {endpoint}: {exc}; see docs/onboarding/linkedin-mcp.md",
        )
    if 200 <= status < 500:
        return Check("PASS", "LinkedIn MCP", f"reachable at {endpoint} (HTTP {status})")
    return Check(
        "FAIL",
        "LinkedIn MCP",
        f"endpoint returned HTTP {status}; see docs/onboarding/linkedin-mcp.md",
    )


def _check_fixture_eval() -> Check:
    run_eval = REPO_ROOT / "evals" / "run_eval.py"
    try:
        with tempfile.TemporaryDirectory(prefix="interview-prep-fixture-") as tmp:
            workspace = build_fixture_workspace(Path(tmp) / "workspace")
            result = subprocess.run(
                [sys.executable, str(run_eval), "--all", "--workspace", str(workspace), "--json"],
                capture_output=True,
                text=True,
            )
    except (OSError, ValueError) as exc:
        return Check("FAIL", "fixture eval", f"could not build/run fixture: {exc}")
    if result.returncode == 0:
        return Check("PASS", "fixture eval", "all local behavior clauses passed")
    output = (result.stderr or result.stdout).strip().replace("\n", " ")
    return Check("FAIL", "fixture eval", f"run_eval exited {result.returncode}: {output[:240]}")


def _format_table(checks: list[Check]) -> str:
    status_width = max(8, *(len(check.status) for check in checks))
    name_width = max(5, *(len(check.name) for check in checks))
    lines = [
        f"{'STATUS':<{status_width}}  {'CHECK':<{name_width}}  DETAIL",
        f"{'-' * status_width}  {'-' * name_width}  {'-' * 6}",
    ]
    lines.extend(
        f"{check.status:<{status_width}}  {check.name:<{name_width}}  {check.detail}"
        for check in checks
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Accept an alternate instance root and an explicit machine-only live-check skip."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=REPO_ROOT, help="Repository instance to inspect"
    )
    parser.add_argument(
        "--skip-live", action="store_true", help="Skip the required LinkedIn reachability check"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run instance, dependency, live endpoint, and fixture gates; fail on any FAIL."""
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    profile, profile_check = _check_profile(repo_root)
    endpoint = profile.get("linkedin_mcp_endpoint", DEFAULT_LINKEDIN_ENDPOINT)
    checks = [
        profile_check,
        *_check_workspace(repo_root),
        _check_reportlab(),
        _check_linkedin(endpoint, skip_live=args.skip_live),
        _check_fixture_eval(),
    ]
    print(_format_table(checks))
    failures = sum(check.status == "FAIL" for check in checks)
    warnings = sum(check.status == "WARN" for check in checks)
    print(f"\n{len(checks) - failures}/{len(checks)} checks non-failing; {warnings} warning(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
