#!/usr/bin/env python3
"""Eval harness runner.

Usage:
  python3 evals/run_eval.py <skill> --workspace <dir> [--json]
  python3 evals/run_eval.py --list

Exit codes:
  0  all clauses passed
  1  one or more clauses failed
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
    p = argparse.ArgumentParser(
        prog="run_eval.py",
        description="Run a per-skill eval verifier against a workspace.",
    )
    p.add_argument("skill", nargs="?", default=None,
                   help="Skill name (a dir under evals/ with verify.py)")
    p.add_argument("--workspace", default=None,
                   help="Path to the workspace to evaluate")
    p.add_argument("--json", action="store_true", dest="as_json",
                   help="Emit results as a JSON array instead of a text table")
    p.add_argument("--list", action="store_true", dest="list_skills",
                   help="List available skills and exit")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_skills:
        skills = discover_skills()
        if not skills:
            print("(no skills found)")
        for s in skills:
            print(s)
        return 0

    if args.skill is None:
        print("error: <skill> is required (or use --list)", file=sys.stderr)
        return 2

    if args.workspace is None:
        print("error: --workspace <dir> is required", file=sys.stderr)
        return 2

    available = discover_skills()
    if args.skill not in available:
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

    try:
        results = run_verifier(args.skill, workspace)
    except Exception as exc:  # a crashed verifier must be unmistakable vs a clause failure
        print(f"error: verifier for '{args.skill}' crashed: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 4

    if args.as_json:
        print(json.dumps([r.as_dict() for r in results], indent=2))
    else:
        print(format_table(results))
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        print(f"\n{passed}/{total} clauses passed")

    all_passed = all(r.passed for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
