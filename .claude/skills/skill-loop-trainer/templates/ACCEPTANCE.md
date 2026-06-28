<!-- TEMPLATE — skill-loop-trainer. Copy into "{{NAME}} Test/" and fill {{PLACEHOLDERS}}.
     The cohere/distyl/recruiter/em-dash details below are the WORKED write-outreach example —
     replace them with the target skill's real fixtures, gates, and gold-example traits.
     Reference impl: repo-root "Write Outreach Test/". -->

# Acceptance Criteria — Write-Outreach Loop

How a candidate email (one model's output for one fixture role) is accepted and scored. Two stages: **hard gates** (binary, disqualifying) then **judge score** (graded). A run = one model's 3 emails.

---

## Stage 0 — Reproducibility gate (per run, not per email)

Before any email is scored, prove the email came from the *edited skill*, not a human:

- [ ] **R1.** The model committed a diff to `~/.claude/skills/{{TARGET_SKILL}}/SKILL.md` and/or `Outreach Templates.md`. An empty skill diff with non-trivial email changes = **disqualified run**.
- [ ] **R2.** Re-running the edited skill on one held-out fixture reproduces a materially-equivalent email (same beats, same hook, within ±10 words). If it can't be reproduced → **disqualified run**.

A disqualified run scores 0 across all 3 fixtures.

---

## Stage 1 — Hard gates (per email, binary, disqualifying)

Each maps to a SPEC §4 invariant. **Any FAIL → that email scores 0**, reason logged. All must PASS to reach Stage 2.

| ID | Gate | Check | How to verify |
|----|------|-------|---------------|
| G1 | Draft only | No send tool invoked anywhere in the run | Inspect run trace / tool calls |
| G2 | No fabrication | Every number + hook + competing process traces to `Resume Achievements Master.md` or live `Pipeline.md` | Cross-check each numeric claim and hook against canon |
| G3 | No banned phrases | Body contains none of the banned openers / hype words | Case-insensitive substring scan (list below) |
| G4 | Body em-dash gate | Zero `—` (U+2014) in body prose | Char scan of body only (exclude subject) |
| G5 | Length | Body word count in **[50, 125]** | Count words in body (exclude subject + signature) |
| G6 | Subject | < 70 chars AND leads with credential | Length + leading-token check |
| G7 | Signature exact | Full cold/intro block present, literal | Diff against canonical block (below) |
| G8 | One CTA | Exactly one ask, low-friction | Count interrogative/ask sentences in closing |
| G9 | Section match | Recruiter → §1 5-beat structure present | Beats 1,2,4,5 present; 3 only if live process |

### G3 banned list (from `Outreach Templates.md` line 8)
Openers: `I hope this email finds you well`, `I hope you are doing well`, `I hope this message finds you well`, `Just wanted to reach out`, `I wanted to reach out to express my interest`, `I came across your profile`, `I wanted to take a moment to`.
Hype: `leverage`, `leveraged`, `spearhead`, `spearheaded`, `synergize`, `synergy`, `drove`, `passionate`, `rockstar`, `ninja`.
*(Note: "circle back" is NOT banned — intentional in FU2, not used here anyway.)*

### G7 canonical signature block
```
Best,
Kanu

---
Kanu Madhok
madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok
Live demo: [URL from Demo Portfolio.md]
```
The `Live demo:` URL must be a real URL from `Demo Portfolio.md` (not the literal placeholder).

### G5 word-count procedure
Count words in the **body only** — everything between the `Hi [First name],` line and the `Best,` sign-off. Exclude subject line and signature block. Hyperlinked text counts as its visible words.

---

## Stage 2 — Judge score (per email, graded 1–5 per dimension)

Only emails passing **all** Stage-1 gates reach here. The LLM judge scores closeness to `fixtures/gold-email.md` on the weighted dimensions in `RUBRIC.md`. Output schema per email:

```json
{
  "role_slug": "cohere-fde",
  "model": "claude",
  "gates": { "G1": "pass", "...": "pass" },
  "disqualified": false,
  "dimensions": {
    "voice":        { "score": 4, "why": "..." },
    "hook":         { "score": 5, "why": "..." },
    "structure":    { "score": 4, "why": "..." },
    "concreteness": { "score": 5, "why": "..." },
    "length":       { "score": 5, "why": "..." },
    "cta":          { "score": 4, "why": "..." },
    "sounds_like_kanu": { "score": 4, "why": "..." }
  },
  "weighted_total": 4.4
}
```

---

## Scoring math

- Per-email weighted total = Σ(dimension score × weight) / Σ(weights), weights from `RUBRIC.md`. Range 1–5.
- A **disqualified** email (any gate fail OR disqualified run) = **0**, not "excluded."
- **Run score** = mean of the model's 3 per-email totals (with 0s for any disqualified).
- **Winner** = highest run score. Tie-breaks, in order: (1) fewest gate failures across the 3 emails, (2) judge head-to-head preference on `cohere-fde`, (3) shortest mean body length within the valid range (tighter wins).

---

## Definition of done (for the harness itself)

- [ ] All 3 fixtures have complete inputs and a recruiter with a verified email.
- [ ] `gold-email.md` holds the real email (not the placeholder).
- [ ] `RUBRIC.md` dimensions + weights are tuned to the real gold email.
- [ ] Gate checks G1–G9 are each unambiguously decidable by reading one email + one run trace.
- [ ] Judge prompt + output schema are fixed so two judge runs on the same email agree within ±0.3 weighted total.
