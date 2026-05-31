# Refactor the job-application skills to a docker-compose model

## Context

The job-application skill suite has accumulated **structural duplication**: `jd-to-ready` (549 lines) reimplements the domain logic of the primitive skills inline instead of calling them. The primitives (`find-contacts`, `write-outreach`, `tailor-resume`) are thin 24–30 line stubs — the *good* logic lives inside the orchestrator, and the standalone primitives are weaker, stale forks. This is the root cause behind the "two places that find contacts" and "two definitions of cold outreach" confusion already surfaced this session.

**The mental model (user's, adopted):** `jd-to-ready` = a `docker-compose.yml` (pure orchestration, zero domain logic). The primitive skills = container images (own all domain logic, runnable standalone, explicit I/O contracts). A compose file references images and wires them; it never reimplements nginx inside itself.

**The principle this enforces:** *Any step in `jd-to-ready` that does the work must be a call to a primitive, not an inline reimplementation. Authoritative logic lives in the primitive (or its source-of-truth file); the orchestrator only wires inputs to outputs.*

**Decisions already locked:**
- Primitives use **one parameterized image** with a `mode` param (e.g. `find-contacts(mode: shortlist|full)`), not separate skills.
- Plan-first; no edits until this plan is approved.

**Intended outcome:** `jd-to-ready` drops from 549 → ~120–160 lines of pure orchestration. Each capability has exactly one authoritative definition. The Process Map in `Skills.md` becomes true ("compose calls these images") instead of half-true.

## Key finding that shapes the approach

`Outreach Templates.md` **already contains the entire step-5 outreach spec** — verified: 5-beat body structure (line 47), 50–125 word range, subject formula, the full 4-email drip with 3–4/4–5 day cadence (sections 1a/4a), Hail Mary, and the "never fabricate urgency" rule (line 51). `jd-to-ready` step 5's 256 lines are a near-verbatim duplicate of that file.

**Therefore the fix is "point at the file," not "move logic into the skill."** Moving inline rules *into* `write-outreach`'s SKILL.md would just relocate the duplication. The layering target:

```
Cold Outreach Emails Best Practices.md  = the research (why)
Outreach Templates.md                   = the spec/copy (what to write)  ← source of truth
write-outreach/SKILL.md                 = the executor (how to run it) → references both
jd-to-ready/SKILL.md                    = the orchestrator → just calls write-outreach
```
Same pattern for resume: `Resume Achievements Master.md` stays canonical; `tailor-resume` references it; `jd-to-ready` calls `tailor-resume`.

## The I/O contract block (the written interface)

These skills have no enforced interface, so the written contract IS the interface. Add this block to each primitive, right after the H1 title:

```markdown
## Contract

**Modes:** `shortlist` | `full`   (omit for track-application / follow-up)

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| company | yes | The real employer; disambiguate vendor/subsidiary. |
| ... | ... | ... |

**Outputs**
| What | When | Where |
|------|------|-------|
| Ranked table(s) | always | returned to chat |
| gaps[] | always | returned for the caller's report |

**Standalone:** `find-contacts(company, role_title, mode: shortlist)`
**Pipeline:** `find-contacts(company, role_title, jd_region, archetype, mode: full, role_folder)`
```
`gaps[]` as an explicit output is what lets `jd-to-ready` steps 6/7 report without re-deriving anything. Default mode is always the **light** one so a casual standalone call never triggers a 13-call LinkedIn sweep or an 8-email drip.

## Per-primitive target design

### `find-contacts` — absorbs step 4 (lines 166–207)
- **Modes:** `shortlist` (1 ranked table, no emails/confidence — upgraded stub) · `full` (5 recruiters + 5 HM/peer-IC, 5-factor ranking, email inference + confidence).
- **Moves in from jd-to-ready:** `search_people` strategy (176–181), the 5-factor ranking rubric — location/title-specificity/tenure/seniority/excludes (183–192), profile drilldown (194–196), email-pattern inference + high/med/low confidence + "never fabricate / InMail only" (198–207).
- **Stub fix:** replace `get_company_employees` (line 13) with `search_people`. Keep the sequential-call rule as a pointer to `linkedin-mcp-operations` — do not re-document it.
- **Inputs:** company, role_title, jd_region, archetype?, mode, role_folder?. **Outputs:** ranked table(s) + `gaps[]`.

### `write-outreach` — absorbs step 5 *execution*, references the spec
- **Modes:** `single` (one message, one contact) · `drip` (the 4-email sequence for top recruiter + top HM).
- **References, does NOT copy:** `Outreach Templates.md` sections 1/1a/4/4a for the 5-beat body, length, subject formula, drip cadence; `Cold Outreach Emails Best Practices.md` for rationale.
- **Gains its own hook-finding** (today it expects a hook supplied). Precedence: (1) `lead_theme` → matching canonical achievement = beat 2; (2) JD-specific detail → beat 4; (3) trigger line = beat 1 from context (applied / job-board / cold).
- **Owns:** mode handling, hook-finding, channel choice (email vs InMail), the `Cold Outreach.md` output structure (jd-to-ready 321–464), and the hard rule "never fabricate urgency."
- **Inputs:** contacts, role_title, company, archetype, lead_theme, urgency (or `none`), channel_confidence, mode, role_folder?. **Outputs:** message(s) / `Cold Outreach.md` + `gaps[]`.

### `tailor-resume` — closest to done; small delta
- **Modes:** `standalone` (extracts its own themes from JD) · `pipeline` (accepts `themes[]` + `archetype` from jd-to-ready step 2).
- **Gaps to close:** add theme/archetype input contract; add the A1-anchor rule + F1/U1 conditional inclusion (jd-to-ready 139–140); **fix the output filename** to `Kanu Madhok Resume - <Company> <Short Role>.md` (matches existing role folders; the stub's `Resume - [Company] [Role].md` is wrong); port the self-check (159–164).
- Already correct: canonical-only rule, `Resume Claims To Verify.md` scrub, `[VERIFY]` rule, no-hype rule.

### `track-application` + `follow-up` — Contract block only
- Functionally fine. Add the `## Contract` block, no `mode`. Keep `follow-up` separate from `write-outreach` (distinct trigger surface + distinct templates, sections 2/3/5/6) — do not over-parameterize one image.

## Target shape of `jd-to-ready` (pure orchestration)

| Step | Now | Becomes |
|------|-----|---------|
| 1 — Intake (35–46) | calls `interview-prep-intake` | **KEEP** as-is |
| 2 — Classify (48–128) | subagent → `themes[]`+`archetype` | **KEEP, trim.** Legit compose-layer logic: it feeds 3 downstream primitives. ~40 lines. |
| 3 — Resume (130–164) | inline tailoring | **GUT** → `tailor-resume(mode: pipeline, role_folder, themes[], archetype)`; wire gaps → step 6. ~5 lines |
| 4 — Contacts (166–207) | inline LinkedIn research | **GUT** → `find-contacts(mode: full, company, role_title, jd_region, archetype, role_folder)`; wire top-1 picks → step 5. ~5 lines |
| 5 — Outreach (209–464) | 256 inline lines | **GUT** → `write-outreach(mode: drip, contacts=top-1 picks, role_title, company, archetype, lead_theme, urgency, role_folder)`. ~6 lines |
| 6 — Report (466–477) | recap | **KEEP** — aggregates `gaps[]` from 3/4/5 |
| 7 — Log (479–549) | JSONL audit | **KEEP** — reads per-step metadata the primitives now return |

**Delete line 211** ("inline rules supersede Outreach Templates if anything conflicts"). This clause is what makes the duplication structural; after the refactor `Outreach Templates.md` is the source of truth.

## Observability layer (from the AHE paper)

Source: `Skill_Best_Practices/Agentic Harness Engineering- Observability-Driven Automatic Evolution of Coding-Agent Harnesses.pdf`. Its thesis: harness quality is *"bottlenecked by observability, not agent capability"* (p.2). It defines three pillars; the refactor already satisfies the first, and this section adds the other two plus token accounting. Goal: **observability, traceability, and understanding what each token/step does.**

**Pillar 1 — Component observability (already covered by the refactor).** Every primitive is a file with an explicit I/O contract; every edit is one git commit (free diffs + file-granular rollback); primitives are loosely coupled so "each failure pattern maps to a single component class." The containerization plan above *is* this pillar. No extra work — just confirm: one commit per primitive edit, never bundle two primitives in one commit.

**Pillar 2 — Experience observability (upgrade step 7).** The paper distills raw traces into a *layered, named* evidence record rather than raw logs. Upgrade the step-7 JSONL log to a per-run **evidence record** with these fields per primitive call:
- `primitive` (name), `mode`, `status` (ok | partial | failed)
- `produced` (file paths written), `gaps[]` (the `[VERIFY:]` / missing-theme / no-hook items the primitive returns)
- `tokens` (prompt + completion for that call) ← see Pillar 4
- `failure_pattern` (tagged from the taxonomy below, or null)
- `prediction` + `prediction_met` (bool) ← see Pillar 3

**Pillar 3 — Decision observability (falsifiable per-step contract).** The paper's core traceability move: every edit ships a prediction, verified next round, turning "rationale" into "a measurable contract." Apply per step: before each primitive runs, the orchestrator declares a one-line, checkable prediction; after, it's scored into the evidence record. Examples:
- `tailor-resume`: "resume covers ≥4 of the 5 JD themes with zero `[VERIFY:]` placeholders"
- `find-contacts(full)`: "surfaces 5+5 with ≥3 high-confidence inferred emails"
- `write-outreach(drip)`: "8 drafts, all 50–125 words, zero banned phrases, a real (non-fabricated) hook on each"

This converts a run from "ran 7 steps" into "7 contracts, N met" — each outcome attributable to one step.

**Pillar 4 — Token accounting.** The paper logs prompt+completion tokens per component and reports `Succ/Mtok`; AHE saved 12% by *"avoiding per-call re-derivation."* Concretely: the JD is currently re-read by step 3, step 4, and step 5. The orchestrator should pass the parsed JD + `themes[]` once (it already classifies them in step 2) so primitives don't each re-derive. Record per-primitive token cost in the evidence record; flag any primitive that re-reads an input the orchestrator already holds.

**Failure-pattern taxonomy (names make the corpus useful).** The AHE evidence corpus works because failures get recurring *names*. Seed a small taxonomy the evidence record tags against, so over many runs you learn *which primitive systematically underperforms*:
`generic-resume-language` · `verify-placeholder-leak` · `non-decision-maker-contact` · `low-confidence-emails` · `fabricated-hook` · `thin-jd-stub` · `theme-unmatched`.

**Regression discipline (the paper's honest caveat).** AHE's self-attribution is reliable for fixes but near-random for *regressions* (~11% precision) — its stated lesson is *"don't trust the agent to foresee breakage; use explicit tests."* This is exactly the verify-before-gut gating below. Formalize it: keep a **golden set** of already-prepped roles (e.g. Morningstar, BCG X) with known-good outputs; after any primitive edit, re-run and diff against the golden output before trusting the change. Never rely on a predicted-regression to catch a break.

**Where this lands in the build:** Pillar 1 is confirmed during Phase 0. Pillars 2–4 (evidence record + predictions + token fields) are built in **Phase 5** when the orchestrator is reassembled — each gutted primitive's `## Contract` must already declare its `gaps[]` and prediction shape (added in Phases 1–3) so the Phase-5 evidence record can read them. The golden-set regression check runs in every phase's "verify before gut" step.

## Execution order (verify each primitive standalone BEFORE gutting its step)

The orchestrator stays fully functional (inline) until each replacement is proven. **Capture a baseline `jd-to-ready` run on a fresh JD before Phase 1** for end-to-end diffing.

- **Phase 0** — Confirm `~/.claude/skills/jd-to-ready/SKILL.md` is the loaded file (the root `jd-to-ready.skill` is a stale stub). Confirm plugin manifest points the primitive names at the top-level stubs, not the `js-*` set.
- **Phase 1 — `tailor-resume`** (lowest risk). Add contract + mode + theme input + A1/F1/U1 rules + filename fix + self-check. Verify standalone on an already-prepped role (e.g. `Morningstar - Product AI Engineer`), diff against committed resume. Then gut step 3; re-run; diff unchanged.
- **Phase 2 — `find-contacts`** (LinkedIn, isolated). Upgrade to `search_people` + ranking + email inference + split + mode + contract. Verify `shortlist` then `full` standalone (watch the sequential-call invariant). Then gut step 4; diff contact tables.
- **Phase 3 — `write-outreach`** (highest blast radius). Rewrite to reference `Outreach Templates.md` 1/1a/4/4a, add hook-finding + mode + `Cold Outreach.md` output + contract. Remove line-211 supersede clause. Verify `single` then `drip` standalone, diff `Cold Outreach.md` against a prior generated one. Then gut step 5.
- **Phase 4 — `track-application` + `follow-up`** — contract blocks only. Anytime.
- **Phase 5 — Orchestrator + docs.** End-to-end `jd-to-ready` run on a fresh JD; compare all three output files against the Phase-0 baseline. Confirm step 6 report + step 7 JSONL still populate (none null). Update `Skills.md` Process Map to reflect compose-calls-images + add the I/O contracts.

## Risks

1. **Duplication relocates instead of resolving** — mitigated by reference-don't-restate (the Templates file is already the home).
2. **Line-211 clause survives** → permanent authority fight. Explicit delete in Phase 3.
3. **Lossy gut** — inline step 5 is richer than the old stub (hook-finding, drip). Never gut a step before its primitive reaches parity; diff against baseline.
4. **`gaps[]` plumbing** — steps 6/7 read data computed inline today; primitives must *return* gaps/metadata or the JSONL log goes null. Explicit `gaps[]` output in every contract.
5. **Mode default drift** — standalone callers must default to light mode.
6. **Wrong-file edit** (root `.skill` vs SKILL.md) — Phase 0 guards this.
7. **`js-*` cross-contamination** — leave the Projects/Job set untouched; use it only as a contract-format reference.

## Critical files
- `~/.claude/skills/jd-to-ready/SKILL.md` — gut steps 3/4/5, delete line 211
- `~/.claude/skills/find-contacts/SKILL.md` — absorb step 4, add mode + contract
- `~/.claude/skills/write-outreach/SKILL.md` — absorb step-5 execution, reference Templates, add hook-finding + mode + contract
- `~/.claude/skills/tailor-resume/SKILL.md` — add mode + theme input + A1/F1/U1 + filename fix + self-check + contract
- `~/.claude/skills/track-application/SKILL.md`, `follow-up/SKILL.md` — contract block only
- `Skills.md` (workspace) — update Process Map + add I/O contracts

Read-only references (do not edit): `Outreach Templates.md`, `Resume Achievements Master.md`, `Cold Outreach Emails Best Practices.md`, `job-search/js-*` (format reference only).

## Verification
- `jd-to-ready` line count ~120–160; steps 1/6/7 byte-identical to before.
- End-to-end run on a fresh JD produces the same three files (`Job Description.md`, `Kanu Madhok Resume - …md`, `Cold Outreach.md`) matching the pre-refactor baseline structure.
- Each primitive runs standalone in light mode without dragging in pipeline machinery.
- `Cold Outreach.md`: 50–125 word bodies, zero banned filler/hype, correct subject formula, full 4-email drip for both picks, Notes block intact.
- Resume: canonical-only (no `Resume Claims To Verify.md` leakage), correct filename, `[VERIFY]` gaps surfaced in step-6 report.
- Step-7 JSONL: valid one-line JSON, all fields populated.
- No primitive issues parallel LinkedIn calls (sequential invariant holds).
