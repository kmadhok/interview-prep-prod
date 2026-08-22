#!/usr/bin/env python3
"""Eval harness runner.

Usage:
  python3 evals/run_eval.py <skill> --workspace <dir> [--json]
  python3 evals/run_eval.py --all --workspace <dir> [--json]
  python3 evals/run_eval.py --list

Exit codes:
  0  no local clauses failed (live clauses may be BLOCKED/NOT_RUN)
  1  one or more local clauses failed
  2  bad skill name (or usage error)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Bootstrap evals/ onto sys.path so common.py is importable when run as a script.
EVALS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS_DIR))

from common import ClauseResult, run_verifier, discover_skills, format_table


def build_parser() -> argparse.ArgumentParser:
    """Build the mutually constrained single-skill/all-skills eval CLI."""
    p = argparse.ArgumentParser(
        prog="run_eval.py",
        description="Run a per-skill eval verifier against a workspace.",
    )
    p.add_argument("skill", nargs="?", default=None,
                   help="Skill name (a dir under evals/ with verify.py)")
    p.add_argument("--workspace", default=None,
                   help="Path to the workspace to evaluate")
    p.add_argument("--role", default=None,
                   help="Role folder (absolute or relative to workspace); defaults to sole fixture role")
    p.add_argument("--profile", default=None,
                   help="Profile/config fixture; defaults to <workspace>/profile.yaml when present")
    p.add_argument("--live", action="store_true",
                   help="Evaluate live-only clauses; default records them BLOCKED")
    p.add_argument("--json", action="store_true", dest="as_json",
                   help="Emit results as a JSON array instead of a text table")
    p.add_argument("--list", action="store_true", dest="list_skills",
                   help="List available skills and exit")
    p.add_argument("--all", action="store_true", dest="all_skills",
                   help="Run all authoritative local behavior contracts")
    return p


def main(argv: list[str] | None = None) -> int:
    """Run selected contracts, distinguishing clause failures, usage errors, and crashes."""
    args = build_parser().parse_args(argv)

    if args.list_skills:
        skills = discover_skills()
        if not skills:
            print("(no skills found)")
        for s in skills:
            print(s)
        return 0

    if args.all_skills and args.skill is not None:
        print("error: use either <skill> or --all, not both", file=sys.stderr)
        return 2

    if args.skill is None and not args.all_skills:
        print("error: <skill> is required (or use --list)", file=sys.stderr)
        return 2

    if args.workspace is None:
        print("error: --workspace <dir> is required", file=sys.stderr)
        return 2

    available = discover_skills()
    if not args.all_skills and args.skill not in available:
        print(
            f"error: unknown skill {args.skill!r}. Available skills:",
            file=sys.stderr,
        )
        if available:
            for s in available:
                print(f"  {s}", file=sys.stderr)
        else:
            print("  (none)", file=sys.stderr)
        return 2

    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"error: workspace does not exist: {workspace}", file=sys.stderr)
        return 2

    selected = available if args.all_skills else [args.skill]
    profile = args.profile
    workspace_profile = workspace / "profile.yaml"
    if profile is None and workspace_profile.is_file():
        profile = str(workspace_profile)
    try:
        by_skill = {
            skill: run_verifier(
                skill, workspace, role=args.role, profile=profile, live=args.live
            )
            for skill in selected
        }
    except Exception as exc:  # a crashed verifier must be unmistakable vs a clause failure
        label = "all skills" if args.all_skills else repr(args.skill)
        print(f"error: verifier for {label} crashed: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 4

    if args.as_json:
        if args.all_skills:
            print(json.dumps({
                "skills": {
                    skill: [result.as_dict() for result in results]
                    for skill, results in by_skill.items()
                }
            }, indent=2))
        else:
            print(json.dumps([r.as_dict() for r in by_skill[args.skill]], indent=2))
    else:
        for index, (skill, results) in enumerate(by_skill.items()):
            if args.all_skills:
                if index:
                    print()
                print(f"== {skill} ==")
            print(format_table(results))
            passed = sum(1 for r in results if r.verdict == "PASS")
            total = len(results)
            print(f"\n{passed}/{total} clauses passed")

    all_results = [result for results in by_skill.values() for result in results]
    all_passed = all(r.verdict in {"PASS", "BLOCKED", "NOT_RUN"} for r in all_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
