"""Shared helpers for the eval harness.

ClauseResult is the single verdict unit every verifier returns. run_verifier
discovers and calls evals/<skill>/verify.py by path (importlib) so verifiers
stay standalone modules. format_table renders the human-readable summary.
"""
from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
THEME_VOCAB = {
    "agents", "RAG", "NL→SQL", "MCP", "LLM-orchestration", "ML-pipeline", "platform",
    "business-translation", "end-to-end", "RPA", "experimentation", "dashboards",
    "consulting", "simplification", "leverage", "cross-functional",
    "engineering-rigor", "evaluation",
}
ARCHETYPE_VOCAB = {
    "agent-builder", "FDE / client-facing", "consulting / product-builder",
    "platform / ML engineering", "data-engineering / analytics",
}


@dataclass
class ClauseResult:
    id: str
    description: str
    passed: bool = False
    detail: str = ""
    status: str = ""
    tier: str = "local"

    def as_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.verdict
        return data

    @property
    def verdict(self) -> str:
        return self.status.upper() if self.status else ("PASS" if self.passed else "FAIL")


@dataclass(frozen=True)
class EvalContext:
    workspace: Path
    role: Path
    profile: Path | None = None
    live: bool = False


def resolve_role(workspace: Path, role: str | Path | None = None) -> Path:
    """Resolve an explicit role or the sole role in an isolated fixture."""
    workspace = Path(workspace)
    if role:
        candidate = Path(role)
        if not candidate.is_absolute():
            candidate = workspace / candidate
        return candidate.resolve()
    roles = workspace / "Roles"
    found = sorted(path for path in roles.iterdir() if path.is_dir()) if roles.is_dir() else []
    if len(found) != 1:
        raise ValueError(f"expected exactly one fixture role under {roles}; found {len(found)}")
    return found[0]


def contract_clause_ids(skill: str) -> list[str]:
    text = (EVALS_DIR / skill / "contract.md").read_text(encoding="utf-8")
    return re.findall(r"^###\s+([A-Za-z0-9._-]+):", text, re.MULTILINE)


def run_verifier(
    skill: str,
    workspace: Path,
    *,
    role: str | Path | None = None,
    profile: str | Path | None = None,
    live: bool = False,
) -> list[ClauseResult]:
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
    context = EvalContext(
        workspace=Path(workspace),
        role=resolve_role(Path(workspace), role),
        profile=Path(profile).resolve() if profile else None,
        live=live,
    )
    verify = mod.verify
    results = verify(context) if "context" in inspect.signature(verify).parameters else verify(Path(workspace))
    expected = contract_clause_ids(skill)
    actual = [result.id for result in results]
    if expected != actual:
        raise ValueError(f"{skill} verifier clauses {actual} do not match authoritative contract {expected}")
    return results


def discover_skills() -> list[str]:
    """Return sorted list of skill names (dirs under evals/ containing verify.py)."""
    skills = []
    for child in sorted(EVALS_DIR.iterdir()):
        if child.is_dir() and (child / "verify.py").exists():
            skills.append(child.name)
    return skills


def format_table(results: list[ClauseResult]) -> str:
    """Aligned text table: STATUS | id | description | detail (detail shown on fail)."""
    status_w = 8
    id_w = max((len(r.id) for r in results), default=2)
    id_w = max(id_w, 2)
    desc_w = max((len(r.description) for r in results), default=11)
    desc_w = max(desc_w, 11)

    header = f"{'STATUS':<{status_w}}  {'ID':<{id_w}}  {'DESCRIPTION':<{desc_w}}  DETAIL"
    sep = f"{'-' * status_w}  {'-' * id_w}  {'-' * desc_w}  {'-' * 6}"
    lines = [header, sep]
    for r in results:
        status = r.verdict
        detail = r.detail if status != "PASS" else ""
        lines.append(f"{status:<{status_w}}  {r.id:<{id_w}}  {r.description:<{desc_w}}  {detail}")
    return "\n".join(lines)
