# Task 8 Report — e2e test integration for apply packet

## What was implemented / tested
- Added `check_packet(clone: Path) -> dict` to `verify_artifacts.py` (after `check_pdf`), using the module's existing `check`/`skill_result` helpers. It asserts: `.apply-packet.json` present, parses, `state == "queued"`, `remote_dir` contains `_test` (load-bearing guard), and `Application Answers.md` present.
- Wired `"apply-packet": check_packet(clone)` into `run_all`'s `skills` dict, right after `"pdf"` and before `"apply-gate"` (prep-side placement, mirroring how `check_pdf` is keyed/collected).
- Appended the brief's two tests to `test_verify_artifacts.py`, adapting the import spelling from `verify_artifacts.check_packet` to the file's actual `import verify_artifacts as va` → `va.check_packet`.
- Because `run_all` now includes the packet check, three existing full-pipeline `run_all` fixtures (`test_run_all_two_drafts_list_pass`, `test_run_all_full_fixture_overall_pass`, `test_run_all_blocked_apply_marks_apply_skills_blocked`) needed the packet artifacts to stay green. Added a shared `_PACKET_OK` / `_PACKET_FILES` constant and spread `**_PACKET_FILES` into those three fixtures (they represent complete prep-side runs, so they should include the packet).
- Added the apply-packet step to `SKILL.md` as `## Step 3.7 — apply-packet (main loop)` immediately after the PDF step (verbatim text from the brief), forcing `APPLY_PACKET_REMOTE_DIR="gdrive:_test/Apply Queue e2e"` and recording the `rclone purge` cleanup line.

## TDD Evidence
- RED: after appending tests, `py -3 -m pytest .../test_verify_artifacts.py -q` → `2 failed, 27 passed`, failure `AttributeError: module 'verify_artifacts' has no attribute 'check_packet'`.
- After implementing + wiring: 3 pre-existing run_all tests broke (fixtures lacked packet artifacts, e.g. `AssertionError: assert 'fail' != 'fail'`) — expected consequence of adding a required prep-side check.
- GREEN: after updating the three fixtures → `29 passed`.

## How check_packet was wired into the flow
In `run_all`, the `skills` dict now has `"apply-packet": check_packet(clone)` between `"pdf"` and `"apply-gate"`. It flows through the same `statuses`/`summary` rollup as every other prep-side skill (fail dominates, then warn, then blocked). It is a prep-side check, so it is NOT in the `--blocked-apply` override list (which only blanks the four apply-side skills).

## Test results
- `py -3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -q` → 29 passed.
- Fuller sweep `py -3 -m pytest scripts/drip_runner .claude/skills/jd-to-ready ".claude/skills/two-orchestrator-e2e-test/scripts" -q` → 137 passed.

## Files changed
- `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` — added `check_packet`, wired into `run_all`.
- `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py` — two new tests + `_PACKET_OK`/`_PACKET_FILES` fixture constant spread into three run_all fixtures.
- `.claude/skills/two-orchestrator-e2e-test/SKILL.md` — new Step 3.7 apply-packet section.

Commit: `0904555` — "e2e-test: verify apply packet artifacts; force _test remote".

## Self-review
- Completeness: all 6 brief steps done; check implemented, wired, tested, doc updated, committed.
- Quality/Discipline: reused existing helpers and checker/report patterns; no new abstractions (YAGNI). Adapted import to the file's real style as instructed.
- Testing: the `_test`-remote guard is asserted in BOTH directions — positive (`test_check_packet_passes_on_test_remote` asserts all checks ok, including `packet-remote-is-test`) and negative (`test_check_packet_fails_on_real_remote` asserts `packet-remote-is-test` present and not ok on a real `gdrive:Apply Queue`). Real behavior, no mocks, no real rclone.
- Pristine output: full suite green (137).

## Concerns
- Doc numbering: the new section is labeled `Step 3.7` but sits before the test-only `Step 3.6` (simulated apply gate). This matches the brief's naming (jd-to-ready Step 3.7) and the instruction to place it right after the PDF step; the non-monotonic 3.7→3.6 sequence is cosmetic. Flagging in case strict numeric order is preferred.

## Fix wave

**Issue:** After commit 0904555, `SKILL.md` had two `## Step 3.7` headers — the new apply-packet section (inserted between 3.5 PDF and 3.6 apply gate) and the pre-existing LinkedIn preflight section.

**Change:** Renamed only the new apply-packet header from `## Step 3.7 — apply-packet (main loop)` to `## Step 3.5b — apply-packet (main loop)`. The body's cross-reference `(jd-to-ready Step 3.7)` was left intact so the pointer to jd-to-ready's step 3.7 survives. No e2e-sequence self-references to 3.7 existed in the body, so none were changed. The pre-existing `## Step 3.7 — LinkedIn preflight` section and all bullet body text were untouched.

**Verification 1** — `grep -n "Step 3\." SKILL.md`:
```
39:## Step 3.5 — PDF (main loop)
45:## Step 3.5b — apply-packet (main loop)
46:- **apply-packet** (jd-to-ready Step 3.7) → ...
48:## Step 3.6 — Simulated apply gate (main loop)
55:## Step 3.7 — LinkedIn preflight (main loop)
```
Written order 3.5 → 3.5b → 3.6 → 3.7; exactly one `Step 3.7` (LinkedIn preflight).

**Verification 2** — `py -3 -m pytest test_verify_artifacts.py -q`:
```
29 passed in 0.34s
```
