# Foundation: profile.yaml + workspace/ Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate personal data (→ `workspace/`) from shareable template logic, replace every hardcoded Kanu path/name with `profile.yaml` config, and install a guard test that permanently blocks personal references from template-side code.

**Architecture:** All personal/instance data moves under `workspace/` at the repo root (stays tracked on this branch — it's Kanu's instance; the later public export simply excludes it). Template-side code resolves the workspace as `<repo root>/workspace/` — a fixed relative location, no config needed for paths. `profile.yaml` holds user *identity* (name, email, resume filename pattern, timezone) and is read by both Python (via a stdlib-only mini-parser in `scripts/config.py` — no PyYAML, per the no-new-deps boundary) and by skills (the LLM reads the file directly). A grep-based guard test enforces zero personal references in template-side dirs forever.

**Tech Stack:** Python 3.11+ stdlib only, pytest (existing), git mv for history-preserving moves.

**Spec:** `docs/spec/productionalization-v1.md` (workstream 5, Decisions 4; success criteria 4, 6)

**Constraints inherited from spec:** work only on `productionalized_version`; never touch the live workspace at `~/Documents/Claude/Projects/Interview Prep/` (with space — this repo clone is `interview-prep`, no space); no new runtime dependencies.

---

## File Structure

```
profile.yaml                          NEW — user identity config (Kanu's instance values)
templates/profile.yaml                NEW — blank starter copied by onboarding
templates/Resume Achievements Master.md   NEW — blank canonical-file starters
templates/Application Profile.md          NEW
templates/Job Search Target Profile.md    NEW
templates/Outreach Templates.md           NEW
templates/Master Story Bank.md            NEW
templates/Tell Me About Yourself - Master.md  NEW
scripts/config.py                     NEW — profile loader + WORKSPACE path constant
scripts/test_config.py                NEW — unit tests for config loader
scripts/test_no_personal_refs.py      NEW — the guard test
scripts/build_resume_pdf.py           MODIFY — line 31 ROOT + name pattern from config
scripts/build_application_dashboard.py MODIFY — ROOT → WORKSPACE
scripts/render_pipeline.py            MODIFY — ROOT → WORKSPACE
scripts/render_prep_html.py           MODIFY — ROOT → WORKSPACE (verify first; may take args)
scripts/verify_resume.py              MODIFY — ROOT → WORKSPACE
scripts/drip_runner/runner-prompt*.md MODIFY — G:/projects + Mac paths → repo-relative
.claude/skills/*/SKILL.md (8 files)   MODIFY — path refs → workspace-relative + profile
.claude/skills/follow-up/             NEW — copied in from ~/.claude/skills/follow-up
.claude/skills/track-application/     NEW — copied in from ~/.claude/skills/track-application
workspace/                            NEW — all personal data git-mv'd here
CLAUDE.md, AGENTS.md                  MODIFY — folder-layout section reflects new paths
.gitignore                            MODIFY — add runs/
```

---

### Task 1: `profile.yaml` + config loader

**Files:**
- Create: `profile.yaml`
- Create: `scripts/config.py`
- Test: `scripts/test_config.py`

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_config.py`:

```python
"""Tests for scripts/config.py — profile loading and workspace resolution."""
from pathlib import Path

import pytest

import config


def test_repo_root_is_parent_of_scripts():
    assert (config.REPO_ROOT / "scripts" / "config.py").exists()


def test_workspace_is_repo_root_slash_workspace():
    assert config.WORKSPACE == config.REPO_ROOT / "workspace"


def test_load_profile_reads_known_keys():
    profile = config.load_profile()
    assert profile["user_name"], "user_name must be non-empty"
    assert "{company}" in profile["resume_filename_pattern"]
    assert "{name}" in profile["resume_filename_pattern"]


def test_load_profile_from_explicit_path(tmp_path):
    p = tmp_path / "profile.yaml"
    p.write_text(
        "user_name: Test User\n"
        "user_email: test@example.com\n"
        "resume_filename_pattern: \"{name} Resume - {company} {role}\"\n"
        "timezone: America/Chicago\n",
        encoding="utf-8",
    )
    profile = config.load_profile(p)
    assert profile["user_name"] == "Test User"
    assert profile["user_email"] == "test@example.com"


def test_load_profile_ignores_comments_and_blanks(tmp_path):
    p = tmp_path / "profile.yaml"
    p.write_text("# a comment\n\nuser_name: X\n", encoding="utf-8")
    assert config.load_profile(p)["user_name"] == "X"


def test_load_profile_missing_file_raises_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError) as exc:
        config.load_profile(tmp_path / "nope.yaml")
    assert "onboard" in str(exc.value).lower()


def test_resume_filename():
    profile = {"user_name": "Test User",
               "resume_filename_pattern": "{name} Resume - {company} {role}"}
    assert (config.resume_filename(profile, "Acme", "Data PM")
            == "Test User Resume - Acme Data PM")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest scripts/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Write `scripts/config.py`**

```python
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
```

- [ ] **Step 4: Create `profile.yaml`** (Kanu's instance values — root of repo)

```yaml
# User profile — read by scripts/config.py and by skills at run time.
# Flat key: value only. Created for each user by the /onboard skill.
user_name: Kanu Madhok
user_email: madhok.kanu@gmail.com
resume_filename_pattern: "{name} Resume - {company} {role}"
timezone: America/Chicago
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest scripts/test_config.py -v`
Expected: 7 PASS. (`test_load_profile_reads_known_keys` reads the real `profile.yaml`; the workspace test passes because `WORKSPACE` is a computed Path — the dir itself is created in Task 3.)

- [ ] **Step 6: Commit**

```bash
git add profile.yaml scripts/config.py scripts/test_config.py
git commit -m "feat: add profile.yaml and stdlib config loader"
```

---

### Task 2: Guard test (red until migration completes)

The guard test is written BEFORE the migration — it is the failing test the rest of this plan turns green. It scans template-side dirs for personal references.

**Files:**
- Test: `scripts/test_no_personal_refs.py`

- [ ] **Step 1: Write the guard test**

```python
"""Guard: template-side code must contain zero personal references.

This is the regression stopper for the template/instance split
(spec: docs/spec/productionalization-v1.md, success criterion 6).
It goes green when the workspace/ migration (Tasks 3-6) completes,
and must stay green forever after.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Dirs that ship in the template. workspace/ and docs/intent|spec|superpowers
# are instance/history material and exempt.
TEMPLATE_DIRS = ["scripts", ".claude/skills", "templates", "evals", "infra",
                 "docs/onboarding"]

SCAN_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".ps1", ".sh", ".txt"}

FORBIDDEN = [
    re.compile(r"kanumadhok", re.IGNORECASE),
    re.compile(r"madhok\.kanu"),
    re.compile(r"Kanu Madhok"),
    re.compile(r"/Users/[A-Za-z]"),          # absolute Mac home paths
    re.compile(r"G:[/\\]projects"),           # Kanu's PC drive layout
    re.compile(r"Documents/Claude/Projects"), # any form of the live workspace path
]

# profile.yaml at repo root is instance data by design; templates/profile.yaml
# must stay blank and IS scanned.
EXEMPT_FILES = set()


def iter_template_files():
    for d in TEMPLATE_DIRS:
        base = REPO_ROOT / d
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.is_file() and f.suffix in SCAN_SUFFIXES and f not in EXEMPT_FILES:
                yield f


def test_no_personal_refs_in_template_dirs():
    violations = []
    for f in iter_template_files():
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN:
            for m in pattern.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(f"{f.relative_to(REPO_ROOT)}:{line_no}: {m.group(0)!r}")
    assert not violations, (
        "Personal references found in template-side files:\n" + "\n".join(violations)
    )
```

- [ ] **Step 2: Run it and record the failure list**

Run: `python3 -m pytest scripts/test_no_personal_refs.py -v 2>&1 | tail -40`
Expected: FAIL, listing ~21+ violations across `scripts/build_resume_pdf.py`, `scripts/drip_runner/runner-prompt*.md`, and 8 SKILL.md files. Save this list — it is the work queue for Tasks 4–5.

- [ ] **Step 3: Commit (red is expected and intentional)**

```bash
git add scripts/test_no_personal_refs.py
git commit -m "test: add personal-refs guard (red until workspace migration lands)"
```

Note: from here until Task 7, run other tests with `--deselect scripts/test_no_personal_refs.py::test_no_personal_refs_in_template_dirs` when a green suite is needed.

---

### Task 3: `workspace/` migration (atomic move)

**Files:** `git mv` of all personal data into `workspace/`. No content edits in this task — moves only, so the diff is pure renames.

- [ ] **Step 1: Create the dir and move personal files**

```bash
mkdir -p workspace
# Pipeline state
git mv "Pipeline.md" "Pipeline.html" workspace/ 2>/dev/null; true
git mv "Application Dashboard.md" "Application Dashboard.html" workspace/ 2>/dev/null; true
git mv "Saved Jobs Export.md" workspace/
# Role data
git mv "Roles" "_Archived" "Work Artifacts" "_jd-to-ready-test" workspace/
# Canonical masters (personal content; blank templates ship in templates/)
git mv "Resume Achievements Master.md" "Resume Claims To Verify.md" workspace/
git mv "Master Story Bank.md" "Demo Portfolio.md" workspace/
git mv "Tell Me About Yourself - Master.md" "AI Build Walkthrough - Master.md" workspace/
git mv "Application Profile.md" "Job Search Target Profile.md" workspace/
git mv "Outreach Templates.md" workspace/
# Personal misc
git mv "bcg interview.md" "Thursday Combined Prep - BCG + Walmart (Fri 6-19).md" workspace/
git mv "Data Agent Startup Shortlist.md" "LinkedIn About Section.txt" workspace/
git mv "Website Project Content.md" "Untitled.md" "articles" workspace/
git mv "Recruiter Contacts.html" workspace/ 2>/dev/null; true
git mv "Write Outreach Test" workspace/ 2>/dev/null; true
```

Files that STAY at root (template-side): `CLAUDE.md`, `AGENTS.md`, `Skills.md`, `Application Operating System.md`, `Cold Outreach Emails Best Practices.md`, all `Automation Architecture - *.md`, `Automation Design - Two-Orchestrator/`, `Spec - Telegram JD Trigger (PC Runner).md`, `LinkedIn MCP - Local Verification Harness.md`, `Skill_Best_Practices/`, `interview-prep-intake.skill` (legacy bundle), `docs/`, `scripts/`, `.claude/`, `.obsidian/`. (Some still contain personal refs — the guard only scans the dirs in `TEMPLATE_DIRS`; root-level doc cleanup is scoped to the later infra-manifest and onboarding plans.)

The `2>/dev/null; true` guards cover files that may not exist in this clone (e.g. generated HTML) — verify with Step 2 that nothing silently vanished.

- [ ] **Step 2: Verify the move is complete and pure**

```bash
git status --porcelain | grep -v "^R" | head    # expect: empty (renames only)
ls workspace/ | wc -l                            # expect: ~25 entries
ls | grep -c "Roles\|Pipeline.md"                # expect: 0
```

- [ ] **Step 3: Add `runs/` to .gitignore**

Append to `.gitignore` (create if missing):

```
# Trace output — one dir per run, instance data, never committed
runs/
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: move all personal/instance data under workspace/"
```

---

### Task 4: Point scripts at `workspace/` via config

**Files:**
- Modify: `scripts/build_resume_pdf.py:31` (+ name-pattern uses)
- Modify: `scripts/build_application_dashboard.py:14-15`
- Modify: `scripts/render_pipeline.py`, `scripts/render_prep_html.py`, `scripts/verify_resume.py:20`
- Modify: `scripts/drip_runner/runner-prompt.md`, `runner-prompt-saved.md`, `runner-prompt-outreach.md`

- [ ] **Step 1: Fix `build_resume_pdf.py`**

Replace line 31:

```python
# OLD
ROOT = Path("/Users/kanumadhok/Documents/Claude/Projects/Interview Prep")
# NEW
from config import WORKSPACE as ROOT  # noqa: E402  (place with other imports)
```

Then grep the file for any literal `Kanu Madhok` (resume title/name handling):
`grep -n "Kanu" scripts/build_resume_pdf.py`
For each hit, route through the profile instead:

```python
from config import load_profile
PROFILE = load_profile()
# e.g. replace: name = "Kanu Madhok"
name = PROFILE["user_name"]
```

- [ ] **Step 2: Fix the repo-relative ROOTs**

`build_application_dashboard.py` line 14, `verify_resume.py` line 20, and the equivalent in `render_pipeline.py` / `render_prep_html.py` currently use `ROOT = Path(__file__).resolve().parents[1]` and then `ROOT / "Pipeline.md"`, `ROOT / "Roles"`. Change each to:

```python
from config import WORKSPACE as ROOT
```

(All `ROOT / "Pipeline.md"`-style joins keep working because those files now live in `workspace/`.) In `render_prep_html.py`, first check how it resolves inputs (`grep -n "ROOT\|Path(" scripts/render_prep_html.py`); if it takes explicit CLI paths, only its default needs the change.

- [ ] **Step 3: Fix the drip-runner prompt files**

In `scripts/drip_runner/runner-prompt.md`, `runner-prompt-saved.md`, `runner-prompt-outreach.md`:
`grep -n "G:/projects\|kanumadhok\|Interview Prep" scripts/drip_runner/runner-prompt*.md`
Replace every absolute path (`G:/projects/interview-prep`, `/Users/kanumadhok/...`) with `<repo root>` (the runner already `cd`s into the repo before invoking claude), and every `Pipeline.md` / `Roles/` reference with `workspace/Pipeline.md` / `workspace/Roles/`.

- [ ] **Step 4: Run scripts against the migrated layout**

```bash
python3 scripts/build_application_dashboard.py     # expect: dashboard written under workspace/
python3 -m pytest scripts/ -v --deselect scripts/test_no_personal_refs.py::test_no_personal_refs_in_template_dirs
```
Expected: dashboard regenerates; all drip_runner `test_*.py` still pass (they take explicit paths).

- [ ] **Step 5: Commit**

```bash
git add scripts/
git commit -m "refactor: scripts resolve workspace/ via config, drop hardcoded paths"
```

---

### Task 5: Update SKILL.md path references (8 files)

**Files (violation counts from the Task 2 red run):**
- Modify: `.claude/skills/jd-to-ready/SKILL.md` (5), `recruiter-contact-tracker/SKILL.md` (6), `verify-emails/SKILL.md` (2), `interview-prep-reusables/SKILL.md` (2), `interview-prep-intake/SKILL.md` (2), `find-fresh-jobs/SKILL.md` (2), `linkedin-saved-jobs-intake/SKILL.md` (1), `jd-to-ready/TRACEABILITY_IMPLEMENTATION_SUMMARY.md` (1)

- [ ] **Step 1: Apply the replacement rules to every hit**

For each file, `grep -n "kanumadhok\|G:/projects\|Kanu Madhok\|Documents/Claude/Projects" <file>` and rewrite each hit with these rules:

| Old reference | New reference |
|---|---|
| `/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/` | `<repo root>/workspace/` |
| `G:/projects/interview-prep` | `<repo root>` |
| `Kanu Madhok Resume - <Company> <Short Role>` | `<user_name from profile.yaml> Resume - <Company> <Short Role>` |
| `Kanu Madhok` (prose: "Kanu's resume", "Kanu wants") | `the user` |
| `madhok.kanu@gmail.com` | `<user_email from profile.yaml>` |

Where a skill needs the workspace root, state it as: *"`<repo root>` = the directory containing `profile.yaml` (the cwd for repo sessions); all workspace files live under `<repo root>/workspace/`."* Add this line once near the top of each edited SKILL.md if not already present.

- [ ] **Step 2: Re-run the guard to watch the count drop**

Run: `python3 -m pytest scripts/test_no_personal_refs.py -v 2>&1 | tail -20`
Expected: violations only in `.claude/skills/follow-up` / `track-application` if already copied (they aren't yet) — otherwise PASS. If any stragglers remain, fix them now.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/
git commit -m "refactor: skills reference workspace/ + profile.yaml, no personal paths"
```

---

### Task 6: Pull `follow-up` and `track-application` into the repo (Decision 4)

**Files:**
- Create: `.claude/skills/follow-up/` (copy from `~/.claude/skills/follow-up/`)
- Create: `.claude/skills/track-application/` (copy from `~/.claude/skills/track-application/`)

- [ ] **Step 1: Copy them in**

```bash
cp -R ~/.claude/skills/follow-up .claude/skills/follow-up
cp -R ~/.claude/skills/track-application .claude/skills/track-application
```

(Do NOT touch the global `~/.claude/skills/` copies or symlinks — they serve the live system.)

- [ ] **Step 2: De-personalize them**

Run: `grep -rn "kanumadhok\|Kanu\|Documents/Claude" .claude/skills/follow-up .claude/skills/track-application`
Apply the Task 5 replacement table to every hit (e.g. `Pipeline.md` → `workspace/Pipeline.md`, "Kanu" → "the user").

- [ ] **Step 3: Run the guard**

Run: `python3 -m pytest scripts/test_no_personal_refs.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/follow-up .claude/skills/track-application
git commit -m "feat: vendor follow-up and track-application skills into repo"
```

---

### Task 7: Blank templates + CLAUDE.md/AGENTS.md layout update + final green

**Files:**
- Create: `templates/profile.yaml`, `templates/Resume Achievements Master.md`, `templates/Application Profile.md`, `templates/Job Search Target Profile.md`, `templates/Outreach Templates.md`, `templates/Master Story Bank.md`, `templates/Tell Me About Yourself - Master.md`
- Modify: `CLAUDE.md`, `AGENTS.md` (folder-layout section)

- [ ] **Step 1: Create `templates/profile.yaml`**

```yaml
# Your profile — created by the /onboard skill. Flat key: value only.
user_name:
user_email:
resume_filename_pattern: "{name} Resume - {company} {role}"
timezone:
```

- [ ] **Step 2: Create the six blank canonical templates**

Each template = the section skeleton of Kanu's file with content removed and one HTML comment explaining what the onboarding interview fills in. Derive headings from the now-`workspace/` originals (`grep "^#" "workspace/<file>"`). Example — `templates/Resume Achievements Master.md`:

```markdown
# Resume Achievements Master

<!-- Canonical library of every resume-worthy achievement. Built by the
/onboard interview; extended over time. Every resume bullet must trace back
to an entry here — nothing outward-facing is invented. -->

## Theme Index

<!-- theme → achievement anchors, filled as achievements accumulate -->

## Achievements by Role

### <Employer — Title (dates)>

**<Achievement name>**
- Canonical bullet:
- Phrasing variants:
- Proof points / numbers:
- Themes:
```

Repeat the pattern for the other five (headings from each original, one explanatory comment, empty scaffolding). Keep each under ~40 lines.

- [ ] **Step 3: Update `CLAUDE.md` and `AGENTS.md`**

In both files' folder-layout section: every reference to root-level `Pipeline.md`, `Roles/`, `_Archived/`, `Work Artifacts/`, and the canonical masters gains the `workspace/` prefix; add two lines introducing `profile.yaml` (user identity, read by scripts and skills) and `templates/` (blank starters used by onboarding). Keep the two files in sync (existing convention).

- [ ] **Step 4: Full suite green**

```bash
python3 -m pytest scripts/ -v
```
Expected: ALL PASS, including the guard.

- [ ] **Step 5: Regenerate + smoke-check one real flow**

```bash
python3 scripts/build_application_dashboard.py
python3 scripts/build_resume_pdf.py --check 2>/dev/null || python3 scripts/build_resume_pdf.py --help
```
Expected: dashboard reads `workspace/Pipeline.md` and writes into `workspace/`; resume script starts and resolves config without error.

- [ ] **Step 6: Commit**

```bash
git add templates/ CLAUDE.md AGENTS.md
git commit -m "feat: blank canonical templates + workspace-aware agent guides"
```

---

## Self-Review Notes

- **Spec coverage:** workstream 5's split half + Decision 4 fully covered; guard = success criterion 6; `/onboard`, `verify_setup.py`, `evals/`, `infra/`, trace changes are explicitly OTHER plans (2–5 in the series).
- **Known judgment calls surfaced:** `Application Operating System.md` and the Automation Architecture docs stay at root with personal refs — guard-exempt by dir scoping; they get cleaned in the infra-manifest plan. `interview-prep-intake.skill` legacy bundle left untouched.
- **Live-system safety:** every step operates on this clone (`interview-prep`, no space); global `~/.claude/skills/` and the live workspace are read-only sources (`cp -R` only).
- **Type consistency:** `config.REPO_ROOT` / `config.WORKSPACE` / `load_profile()` / `resume_filename()` used identically in Tasks 1, 4; guard test's `TEMPLATE_DIRS` matches the target structure dirs that exist after this plan (evals/, infra/, docs/onboarding/ entries are no-ops until later plans create them — `iter_template_files` skips missing dirs).
```
