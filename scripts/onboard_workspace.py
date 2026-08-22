#!/usr/bin/env python3
"""Apply structured onboarding answers to profile.yaml and workspace masters."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MASTER_NAMES = (
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
CORE_MASTERS = {
    "Resume Achievements Master.md",
    "Master Story Bank.md",
    "Tell Me About Yourself - Master.md",
    "Job Search Target Profile.md",
    "Application Profile.md",
}
PROFILE_NAME = "profile.yaml"


def _parse_flat_yaml(path: Path) -> tuple[list[str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    keys = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and ":" in stripped:
            keys.append(stripped.partition(":")[0].strip())
    return lines, keys


def _render_profile(template: Path, values: dict[str, object]) -> str:
    lines, keys = _parse_flat_yaml(template)
    missing = [
        key
        for key in keys
        if values.get(key) is None or not str(values.get(key, "")).strip()
    ]
    if missing:
        raise ValueError("profile answers missing keys: " + ", ".join(missing))
    rendered = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            rendered.append(line)
            continue
        key = stripped.partition(":")[0].strip()
        rendered.append(f"{key}: {json.dumps(str(values[key]), ensure_ascii=False)}")
    return "\n".join(rendered) + "\n"


def _follow_up_copy(template_text: str, name: str) -> str:
    return (
        template_text.rstrip()
        + "\n\n<!-- Onboarding follow-up: customize this master after the core setup is complete. "
        + f"File: {name}. -->\n"
    )


def apply_answers(
    repo_root: Path,
    answers: dict[str, object],
    *,
    refresh: set[str] | None = None,
) -> list[Path]:
    """Write a fresh instance or explicitly refreshed files, returning paths written."""
    repo_root = repo_root.resolve()
    templates = repo_root / "templates"
    workspace = repo_root / "workspace"
    refresh = refresh or set()
    allowed = {PROFILE_NAME, *MASTER_NAMES}
    unknown = refresh - allowed
    if unknown:
        raise ValueError("unknown refresh target(s): " + ", ".join(sorted(unknown)))
    if not templates.is_dir():
        raise ValueError(f"templates directory missing: {templates}")

    existing = []
    if (repo_root / PROFILE_NAME).exists():
        existing.append(PROFILE_NAME)
    existing.extend(name for name in MASTER_NAMES if (workspace / name).exists())
    if existing and not refresh:
        raise FileExistsError(
            "existing instance detected; choose per-file refresh targets: "
            + ", ".join(existing)
        )

    profile_values = answers.get("profile", {})
    master_values = answers.get("masters", {})
    if not isinstance(profile_values, dict) or not isinstance(master_values, dict):
        raise ValueError("answers must contain object-valued 'profile' and 'masters' fields")

    fresh = not existing
    if fresh:
        missing_core = [
            name
            for name in sorted(CORE_MASTERS)
            if not isinstance(master_values.get(name), str)
            or not master_values[name].strip()
        ]
        if missing_core:
            raise ValueError("core master answers missing: " + ", ".join(missing_core))

    planned: dict[Path, str] = {}
    if fresh or PROFILE_NAME in refresh:
        planned[repo_root / PROFILE_NAME] = _render_profile(
            templates / PROFILE_NAME, profile_values
        )

    for name in MASTER_NAMES:
        if not fresh and name not in refresh:
            continue
        raw_content = master_values.get(name)
        supplied = raw_content.strip() if isinstance(raw_content, str) else ""
        if supplied:
            content = supplied.rstrip() + "\n"
        elif fresh and name not in CORE_MASTERS:
            content = _follow_up_copy(
                (templates / name).read_text(encoding="utf-8"), name
            )
        else:
            raise ValueError(f"no content supplied for refresh target: {name}")
        planned[workspace / name] = content

    workspace.mkdir(parents=True, exist_ok=True)
    written = []
    for path, content in planned.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    (workspace / "Roles").mkdir(exist_ok=True)
    return written


def build_parser() -> argparse.ArgumentParser:
    """Build onboarding arguments with repeatable, per-file refresh authorization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--answers", type=Path, required=True, help="Structured onboarding JSON")
    parser.add_argument(
        "--refresh",
        action="append",
        default=[],
        metavar="FILE",
        help="Explicit existing file to replace; repeat per file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Load structured answers and print only paths successfully written."""
    args = build_parser().parse_args(argv)
    try:
        answers = json.loads(args.answers.read_text(encoding="utf-8"))
        if not isinstance(answers, dict):
            raise ValueError("answers JSON must be an object")
        written = apply_answers(args.repo_root, answers, refresh=set(args.refresh))
    except (FileExistsError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
