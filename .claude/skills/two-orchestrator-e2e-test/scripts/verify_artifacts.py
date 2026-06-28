"""Deterministic per-skill artifact verifier for the two-orchestrator E2E test.

Pure functions + a thin CLI, same shape as dedupe.py. Stdlib only. Cannot reach
MCP servers — Gmail-draft state and PDF/worklist results are passed in as args.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

# Classification vocab — must match jd-to-ready/SKILL.md (themes ~line 115, archetypes ~118).
THEME_VOCAB = {
    "agents", "RAG", "NL→SQL", "MCP", "LLM-orchestration", "ML-pipeline", "platform",
    "business-translation", "end-to-end", "RPA", "experimentation", "dashboards",
    "consulting", "simplification", "leverage", "cross-functional", "engineering-rigor", "evaluation",
}
ARCHETYPE_VOCAB = {
    "agent-builder", "FDE / client-facing", "consulting / product-builder",
    "platform / ML engineering", "data-engineering / analytics",
}


def check(name: str, ok: bool, detail: str = "", severity: str = "fail") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail, "severity": severity}


def rollup(checks: list[dict]) -> str:
    failed = [c for c in checks if not c["ok"]]
    if any(c["severity"] == "fail" for c in failed):
        return "fail"
    if failed:
        return "warn"
    return "pass"


def skill_result(checks: list[dict], notes: str = "") -> dict:
    return {"status": rollup(checks), "checks": checks, "notes": notes}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def check_intake(clone: Path) -> dict:
    jd = clone / "Job Description.md"
    text = _read(jd)
    return skill_result([
        check("clone-folder-exists", clone.is_dir(), str(clone)),
        check("job-description-present", jd.exists(), str(jd)),
        check("job-description-nonempty", len(text.strip()) > 50, f"{len(text)} chars"),
    ])
