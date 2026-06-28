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


def check_classify(clone: Path) -> dict:
    f = clone / ".classification.json"
    if not f.exists():
        return skill_result([check("classification-present", False, str(f))])
    try:
        data = json.loads(_read(f))
    except ValueError as exc:
        return skill_result([check("classification-parses", False, str(exc))])
    themes = data.get("themes", []) if isinstance(data.get("themes"), list) else []
    tags = [t.get("tag") for t in themes if isinstance(t, dict)]
    off = [t for t in tags if t not in THEME_VOCAB]
    no_ev = [t for t in themes if isinstance(t, dict) and not str(t.get("evidence", "")).strip()]
    return skill_result([
        check("classification-parses", True),
        check("theme-count-4-6", 4 <= len(tags) <= 6, f"{len(tags)} themes"),
        check("themes-in-vocab", not off, f"off-vocab: {off}"),
        check("archetype-in-vocab", data.get("archetype") in ARCHETYPE_VOCAB, str(data.get("archetype"))),
        check("evidence-present", not no_ev, f"{len(no_ev)} theme(s) missing evidence"),
        check("classified-ts-present", bool(str(data.get("classified_ts", "")).strip())),
    ])


def find_resume(clone: Path) -> Path | None:
    matches = sorted(clone.glob("Kanu Madhok Resume - *.md"))
    return matches[0] if matches else None


def check_tailor_resume(clone: Path) -> dict:
    r = find_resume(clone)
    if r is None:
        return skill_result([check("resume-md-present", False, "glob: Kanu Madhok Resume - *.md")])
    text = _read(r)
    leaks = re.findall(r"\[VERIFY|\[NUMBER\?", text)
    return skill_result([
        check("resume-md-present", True, r.name),
        check("resume-nontrivial", len(text.strip()) > 400, f"{len(text)} chars"),
        check("no-verify-leak", not leaks, f"{len(leaks)} leak(s)"),
        check("contact-header-present", "madhok.kanu@gmail.com" in text),
    ])
