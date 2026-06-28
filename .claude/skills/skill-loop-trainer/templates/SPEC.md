<!-- TEMPLATE — skill-loop-trainer. Copy into "{{NAME}} Test/" and fill {{PLACEHOLDERS}}.
     The cohere/distyl/recruiter/em-dash details below are the WORKED write-outreach example —
     replace them with the target skill's real fixtures, gates, and gold-example traits.
     Reference impl: repo-root "Write Outreach Test/". -->

# Write-Outreach Loop-Engineering Spec

**Owner:** Kanu Madhok
**Purpose.** Run the same task — *improve the `{{TARGET_SKILL}}` skill, then generate cold-recruiter emails with it* — across multiple provider models (Codex / Claude / Gemini), each in its own git worktree, and pick the model whose improved skill produces emails closest to a single **gold-standard email**.

This is a benchmark, not a feature. The deliverable of a *winning run* is an improved `{{TARGET_SKILL}}` skill. The deliverable of *this folder* is the harness that decides which run won.

---

## 1. What each model is asked to do (the task contract)

Each model, in its own worktree, performs **both steps in sequence**:

1. **Edit the skill.** Improve `~/.claude/skills/{{TARGET_SKILL}}/SKILL.md` and/or the source-of-truth `Outreach Templates.md` so the emails it produces are closer to the gold email (`fixtures/gold-email.md`). Allowed edits: the skill's process, the 5-beat structure, the hook logic, the format gates, the template prose. **Not allowed:** changing the hard invariants in §4 (draft-only, no fabrication, signature block, banned phrases) — those are constraints, not optimization targets.
2. **Run the improved skill** on each of the 3 fixture roles (§3), in **`drip` mode, recruiter contact only** (one intro email per role — the recruiter top-pick). Write each generated email to `runs/<model>/<role-slug>.md`.

The model is graded **only on the emails from step 2**, but the artifact that gets merged on a win is the **skill diff from step 1**. A model that writes great emails by hand without improving the skill **fails** — the emails must be reproducible by re-running the edited skill.

### Reproducibility check (gate, not scored)
Before judging, the harness re-runs the model's edited skill on one held-out fixture. If the regenerated email differs materially from the submitted one, the run is **disqualified** — it means the email was hand-authored, not skill-produced.

---

## 2. The gold email (acceptance anchor)

`fixtures/gold-email.md` holds **one** cold-recruiter email Kanu loves. It is the single source of truth for "better." Every judge dimension in `RUBRIC.md` is derived from a real trait of this email — when the gold email changes, the rubric is re-tuned to match (not the other way around).

> **STATUS: PLACEHOLDER.** `fixtures/gold-email.md` currently contains a marked placeholder. Drop the real email in before running. Until then the rubric dimensions are provisional, inferred from `Outreach Templates.md` §1, and flagged as such in `RUBRIC.md`.

The gold email is **company-specific** — it was written for one role. The rubric grades **transferable traits** (structure, voice, hook discipline, concreteness, length), not verbatim text. A candidate email for Sierra is not expected to contain Cohere facts; it is expected to *do what the gold email does*.

---

## 3. Test set — 3 recruiter-target fixtures

All three are real roles in `Roles/` with a real recruiter contact and a verified email. Chosen to vary by archetype and hook so the skill is tested across cases, not overfit to one.

| Slug | Role | Recruiter (verified email) | Archetype | Lead theme | Hook case |
|------|------|----------------------------|-----------|-----------|-----------|
| `cohere-fde` | Cohere — Forward Deployed Engineer, Agentic Platform | Michael Pagano · michael.pagano@cohere.com (High) | FDE / client-facing | agents / RAG / end-to-end delivery | **beat 3 LIVE** — tests the gold email's urgency move |
| `distyl-fde` | Distyl — Forward Deployed AI Engineer | Austin Amberg · austin.amberg@distyl.ai (High) | FDE / client-facing | enterprise agent delivery | **beat 3 OMIT** — tests clean live-sourcing |
| `sierra-strategist` | Sierra — Strategist, Agent Development | Greg Marsh · greg@sierra.ai (High) | agent development / product | agent design + customer outcomes | **beat 3 OMIT** — product/strategy hook, not pure-eng |

Each fixture in `fixtures/<slug>.md` carries exactly the inputs the skill needs: role title, company, recruiter name/title, verified email, archetype, lead theme, JD details, and an explicit **beat-3 mode**.

**Why the beat-3 split matters.** The gold email's load-bearing trait (Kanu's own words) is paragraph two: real, live competing processes + a "closer match" pivot that induces #fomo without making the target the backup. So the harness MUST test that move. But the no-fabrication rule means beat 3 only appears when a real live process exists. As of the build date, nothing in `Pipeline.md` survives the freshness filter, so a naive "source it live" run would omit beat 3 on all three fixtures and never exercise the signature move. The fix:
- **`cohere-fde` is seeded with a declared, clearly-labeled live-process list** (mirroring the gold email's own) so the urgency move is tested. The seed is a *fixture test input*, not the skill inventing anything — the skill still only ever uses what it's handed.
- **`distyl-fde` and `sierra-strategist` carry no live process** — they test that the skill sources live, finds nothing, and **omits beat 3 cleanly**. Per RUBRIC, a clean omission scores as high as a clean inclusion; the skill is graded on correct live-sourcing, not on always emitting a paragraph two.

---

## 4. Hard invariants (constraints — failing any one disqualifies the run)

These are inherited from `Outreach Templates.md` and the skill's hard rules. They are **pass/fail gates**, checked before any scoring. A candidate email that violates one is disqualified regardless of how good it reads.

- **G1 — Draft only.** No send tool ever called. (Skill-level; verified by inspecting the run, not the email.)
- **G2 — No fabrication.** Every number, hook, and competing process is real and canonical (from `Resume Achievements Master.md` / live `Pipeline.md`). No invented metrics, no invented urgency.
- **G3 — Banned phrases.** None of the banned openers or hype words from `Outreach Templates.md` line 8 ("I hope this email finds you well", "Just wanted to reach out", "I came across your profile", "leverage", "spearhead", "synergy", "drove", "passionate", "rockstar", "ninja", …).
- **G4 — Body em-dash gate.** Zero ` — ` / U+2014 in the email **body prose**. Subject may use a template-prescribed em-dash form only.
- **G5 — Length.** Body 50–125 words (target ~100). Counted.
- **G6 — Subject < 70 chars**, leads with the credential.
- **G7 — Signature block exact.** The full cold/intro block (name · email · linkedin · github + Live demo line) copied literally from the template — not paraphrased or reordered.
- **G8 — One CTA.** Exactly one clear, low-friction ask.
- **G9 — Section match.** Recruiter target → `Outreach Templates.md` §1 beats/voice.

Gates are defined as a machine-checkable checklist in `ACCEPTANCE.md`.

---

## 5. Scoring (after gates pass)

Two-stage, per `ACCEPTANCE.md`:

1. **Hard gates (G1–G9)** — binary. Any fail → email disqualified (score 0, reason logged).
2. **LLM judge** — for emails that pass all gates, an LLM judge scores closeness to the gold email on the weighted dimensions in `RUBRIC.md` (voice, hook specificity, structure adherence, concreteness/numbers, length discipline, CTA quality, "sounds like Kanu"). Output: per-dimension 1–5 + weighted total + a one-line rationale per dimension.

A model's run score = mean of its 3 emails' judge totals, with **any disqualified email scored 0** (a model can't win by acing 2 roles and failing the 3rd).

**Winner:** highest mean across the 3 fixtures, tie-broken by fewest gate failures, then by judge's head-to-head preference on `cohere-fde`.

---

## 6. Worktree / model matrix (execution wired later)

Worktrees are **created and isolation-proven**; CLI invocations are **verified**. Full mechanics in `RUNNER.md`.

| Worktree (in `.claude/worktrees/`) | Branch | Provider | Model | CLI |
|-----------------------------------|--------|----------|-------|-----|
| `{{SLUG_BASE}}-claude` | `{{SLUG_BASE}}-test/claude` | Anthropic | claude-opus-4-8 | claude |
| `{{SLUG_BASE}}-codex` | `{{SLUG_BASE}}-test/codex` | OpenAI | (latest Codex) | codex |
| `{{SLUG_BASE}}-gemini` | `{{SLUG_BASE}}-test/gemini` | Google | (latest Gemini) | gemini |

The skill is **vendored in-repo** at `.claude/skills/{{TARGET_SKILL}}/` (git-tracked), so each worktree gets its own isolated copy of it for free — no separate `skill-under-test/` copy needed. Proven: an edit in `{{SLUG_BASE}}-claude` is invisible to `{{SLUG_BASE}}-codex` and `main`. Each worktree runs the **same task prompt** (`fixtures/TASK_PROMPT.md`) and writes emails to the shared `runs/<model>/` (outputs are collected centrally; only the *skill edits* need isolation). The judge runs once, centrally, over all `runs/*/`.

> Run-time guard (from `RUNNER.md`): a model session may also see the GLOBAL skill at `~/.claude/skills/{{TARGET_SKILL}}/`. Each model must edit and be judged on the **in-worktree** copy only — never the global one — or edits leak across worktrees.

---

## 7. Folder layout

```
{{NAME}} Test/
├── SPEC.md            ← this file (the what + why)
├── ACCEPTANCE.md      ← machine-checkable gates + scoring procedure
├── RUBRIC.md          ← judge dimensions + weights, derived from the gold email
├── RUNNER.md          ← (stub) worktree + model execution mechanics, wired later
├── fixtures/
│   ├── gold-email.md      ← THE anchor (placeholder until Kanu drops it in)
│   ├── TASK_PROMPT.md     ← the exact prompt handed to every model
│   ├── cohere-fde.md      ← role fixture (inputs the skill needs)
│   ├── distyl-fde.md
│   └── sierra-strategist.md
└── runs/
    └── <model>/<role-slug>.md   ← generated emails land here (one dir per model)
```

---

## 8. Open decisions (resolve before first real run)

- [x] **Gold email dropped in** (Google Cloud / FDE I) and `RUBRIC.md` tuned to its two load-bearing traits (relevance-match + urgency/social-proof).
- [x] **3 fixtures confirmed** (Cohere / Distyl / Sierra), with the beat-3 split (Cohere LIVE, Distyl + Sierra OMIT).
- [ ] Decide the **judge model** (recommend a strong, neutral model not in the contestant matrix to avoid self-preference bias).
- [ ] Wire `RUNNER.md` (worktree creation, per-CLI invocation, output collection).
- [ ] Decide **global-skill vs repo-local `skill-under-test/` copy** so worktrees actually isolate the skill edits (see `RUNNER.md` caveat).
