"""Shared helpers for the eval harness.

ClauseResult is the single verdict unit every verifier returns. run_verifier
discovers and calls evals/<skill>/verify.py by path (importlib) so verifiers
stay standalone modules. format_table renders the human-readable summary.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent


@dataclass
class ClauseResult:
    id: str
    description: str
    passed: bool
    detail: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def run_verifier(skill: str, workspace: Path) -> list[ClauseResult]:
    """Import evals/<skill>/verify.py by path and call its verify(workspace).

    Raises FileNotFoundError if the skill has no verify.py.
    """
    verify_path = EVALS_DIR / skill / "verify.py"
    if not verify_path.exists():
        raise FileNotFoundError(f"No verifier at {verify_path}")

    # Unique module name so repeated imports (different skills) don't collide.
    mod_name = f"evals_{skill.replace('-', '_')}_verify"
    spec = importlib.util.spec_from_file_location(mod_name, verify_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {verify_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    if not hasattr(mod, "verify"):
        raise AttributeError(f"{verify_path} has no verify(workspace) function")
    return mod.verify(Path(workspace))


def discover_skills() -> list[str]:
    """Return sorted list of skill names (dirs under evals/ containing verify.py)."""
    skills = []
    for child in sorted(EVALS_DIR.iterdir()):
        if child.is_dir() and (child / "verify.py").exists():
            skills.append(child.name)
    return skills


def format_table(results: list[ClauseResult]) -> str:
    """Aligned text table: STATUS | id | description | detail (detail shown on fail)."""
    status_w = 6
    id_w = max((len(r.id) for r in results), default=2)
    id_w = max(id_w, 2)
    desc_w = max((len(r.description) for r in results), default=11)
    desc_w = max(desc_w, 11)

    header = f"{'STATUS':<{status_w}}  {'ID':<{id_w}}  {'DESCRIPTION':<{desc_w}}  DETAIL"
    sep = f"{'-' * status_w}  {'-' * id_w}  {'-' * desc_w}  {'-' * 6}"
    lines = [header, sep]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        detail = r.detail if not r.passed else ""
        lines.append(f"{status:<{status_w}}  {r.id:<{id_w}}  {r.description:<{desc_w}}  {detail}")
    return "\n".join(lines)
