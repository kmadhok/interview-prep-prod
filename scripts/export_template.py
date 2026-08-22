#!/usr/bin/env python3
"""Export the shareable template surface to a clean target directory."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_no_personal_refs import FORBIDDEN, TEMPLATE_DIRS  # noqa: E402

EXTRA_DIRS = ("docs/trace",)
ROOT_FILES = ("README.md", "LICENSE", "AGENTS.md", "CLAUDE.md", "Skills.md")
EXTRA_FILES = ("docs/release-gate.md", ".claude/settings.json")
REQUIRED_EXPORT_FILES = (
    "README.md",
    "LICENSE",
    "CLAUDE.md",
    "AGENTS.md",
    "Skills.md",
    ".claude/settings.json",
    ".claude/skills/onboard/SKILL.md",
    ".claude/skills/jd-to-ready/SKILL.md",
    "templates/profile.yaml",
    "evals/fixtures/profile.yaml",
    "evals/fixtures/onboarding-answers.json",
    "scripts/verify_setup.py",
    "scripts/onboard_workspace.py",
    "scripts/build_fixture_workspace.py",
    "scripts/export_template.py",
    "scripts/test_no_personal_refs.py",
    "scripts/config.py",
    "docs/onboarding/linkedin-mcp.md",
    "docs/onboarding/gmail.md",
    "docs/onboarding/manual-mode.md",
    "docs/release-gate.md",
    "infra/launchd/com.example.linkedin-mcp.plist",
)
GENERATED_GITIGNORE_LINES = (
    "",
    "# Personal instance data — created by /onboard, never shipped",
    "workspace/",
    "/profile.yaml",
    "runs/",
    ".lavish/",
    ".obsidian/",
)
IGNORE_NAMES = {"__pycache__", ".DS_Store", ".pytest_cache"}


def _prepare_target(target: Path, *, force: bool) -> None:
    target = target.resolve()
    if target == Path(target.anchor) or target == REPO_ROOT:
        raise ValueError(f"refusing unsafe export target: {target}")
    if target.exists() and not target.is_dir():
        raise ValueError(f"target exists and is not a directory: {target}")
    if target.is_dir() and any(target.iterdir()):
        if not force:
            raise FileExistsError(
                f"target is not empty: {target} (pass --force to replace its contents)"
            )
        for child in target.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    target.mkdir(parents=True, exist_ok=True)


def _ignore_copy(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in IGNORE_NAMES or name.endswith((".pyc", ".pyo"))
    }


def _copy_relative(source_root: Path, target: Path, relative: str) -> None:
    source = source_root / relative
    if not source.exists():
        return
    destination = target / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=_ignore_copy)
    else:
        shutil.copy2(source, destination)


def _write_gitignore(target: Path) -> None:
    source = REPO_ROOT / ".gitignore"
    lines = source.read_text(encoding="utf-8").rstrip().splitlines() if source.exists() else []
    for line in GENERATED_GITIGNORE_LINES:
        if line and line in lines:
            continue
        lines.append(line)
    (target / ".gitignore").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _reset_runner_state(target: Path) -> None:
    """Ship runner schemas without exporting the private instance's job history."""
    state_files = {
        "scripts/drip_runner/saved_seen.json": {"entries": {}, "version": 1},
        "scripts/drip_runner/heartbeat.json": {
            "pc": {
                "last_ok_saved": None,
                "last_ok_outreach": None,
                "consecutive_aborts": 0,
                "daemon_ok": False,
            },
            "cloud": {"last_ok_sweep": None},
        },
    }
    for relative, value in state_files.items():
        destination = target / relative
        if destination.exists():
            destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def check_required_files(target: Path) -> list[str]:
    """Return problems for required files that are missing or ignored."""
    problems = [
        f"{relative}: missing from clean export"
        for relative in REQUIRED_EXPORT_FILES
        if not (target / relative).is_file()
    ]

    try:
        with tempfile.TemporaryDirectory() as git_dir:
            subprocess.run(
                [
                    "git",
                    "--git-dir",
                    git_dir,
                    "--work-tree",
                    str(target),
                    "init",
                    "-q",
                ],
                check=True,
            )
            for relative in REQUIRED_EXPORT_FILES:
                if not (target / relative).is_file():
                    continue
                result = subprocess.run(
                    [
                        "git",
                        "--git-dir",
                        git_dir,
                        "--work-tree",
                        str(target),
                        "check-ignore",
                        "-q",
                        relative,
                    ],
                    check=False,
                )
                if result.returncode == 0:
                    problems.append(
                        f"{relative}: would be ignored by the exported .gitignore"
                    )
    except FileNotFoundError:
        print("warning: git not found; skipping exported .gitignore checks", file=sys.stderr)

    return problems


def scan_export(target: Path) -> list[str]:
    """Return forbidden-pattern hits across every readable file in the export."""
    violations = []
    guard_relative = Path("scripts/test_no_personal_refs.py")
    for file_path in sorted(path for path in target.rglob("*") if path.is_file()):
        relative = file_path.relative_to(target)
        if relative == guard_relative:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="surrogateescape")
        except OSError as exc:
            violations.append(f"{relative}: unreadable: {exc}")
            continue
        for pattern in FORBIDDEN:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                violations.append(f"{relative}:{line_number}: {match.group(0)!r}")
    return violations


def export_template(target: Path, *, force: bool = False) -> Path:
    """Copy the shareable surface, reset private state, and reject any personal-reference leak."""
    target = target.resolve()
    _prepare_target(target, force=force)
    for relative in (*TEMPLATE_DIRS, *EXTRA_DIRS):
        _copy_relative(REPO_ROOT, target, relative)
    for relative in ROOT_FILES:
        _copy_relative(REPO_ROOT, target, relative)
    for relative in EXTRA_FILES:
        _copy_relative(REPO_ROOT, target, relative)
    _write_gitignore(target)
    _reset_runner_state(target)

    required_file_problems = check_required_files(target)
    if required_file_problems:
        raise ValueError(
            "required template files missing or ignored in clean export:\n"
            + "\n".join(required_file_problems)
        )

    violations = scan_export(target)
    if violations:
        raise ValueError(
            "personal references found in clean export:\n" + "\n".join(violations)
        )
    return target


def build_parser() -> argparse.ArgumentParser:
    """Require an export target and make destructive replacement explicit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Clean export directory")
    parser.add_argument(
        "--force", action="store_true", help="Replace contents when target is non-empty"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Export and scan the template, returning one for unsafe targets or leaked references."""
    args = build_parser().parse_args(argv)
    try:
        target = export_template(args.target, force=args.force)
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    file_count = sum(1 for path in target.rglob("*") if path.is_file())
    print(f"Exported {file_count} template files to {target}")
    print("PASS: all required template files present and not ignored")
    print("PASS: full export tree contains no forbidden personal references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
