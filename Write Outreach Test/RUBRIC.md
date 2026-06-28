# Judge Rubric — Closeness to the Gold Email

The LLM judge scores each gate-passing email 1–5 on each dimension, then the harness computes the
weighted total. **Tuned to the real gold email** (`fixtures/gold-email.md`: the Google Cloud / FDE I
email) and to `Cold Outreach Emails Best Practices.md` (the 8-tips source).

> Gold email's load-bearing edge, in Kanu's own words: **(1) relevance** — it ties to the actual JD
> *and* his current work, ending on a "this role is the closer match for what I do" pivot; and
> **(2) urgency via social proof** — paragraph two names real, currently-live competing processes
> ("interview Friday", BCG X), inducing #fomo and a visible timeline *without* making the target the
> backup. The rubric weights these two highest.

---

## Dimensions + weights

| Dimension | Weight | What a **5** looks like (anchored to the gold email) | What a **1** looks like |
|-----------|:------:|------------------------------------------------------|--------------------------|
| **urgency_social_proof** | 0.22 | Beat 3 names REAL, currently-live competing processes (company + role + a concrete timeline like "interview Friday"), woven into ONE sentence with the why-this-company pivot, and keeps enthusiasm on the target (never makes it the backup). Tip #3 executed cleanly. *If no live process exists for this fixture, beat 3 is correctly OMITTED — and this dimension is scored on whether the omission was handled cleanly, not penalized.* | Urgency missing when a live process was available; OR invented/stale urgency; OR phrased so the target reads as the fallback. |
| **relevance_match** | 0.20 | Hook + close tie to THIS role's actual JD and Kanu's current work, ending on a "closer match for what I do" style pivot. Specific to the req, not generic interest. | Generic ("interested in opportunities at your company"); no JD tie; could be sent to any company. |
| **voice** | 0.15 | First-person, conversational, reads like Kanu talking. Zero corporate filler. | Stiff, templated, "to express my interest" register. |
| **concreteness** | 0.13 | One real, canonical number used naturally (400+ tickets, 30–60 min → under 10). Tip #2 — one accomplishment, not a resume dump. | Vague claims, no number, or a number that feels invented. |
| **structure** | 0.10 | Clean §1 5-beat arc: trigger → one numbered achievement → urgency-pivot (if live) → why-this-company → one ask. Flows as 3 tight paragraphs, not bolted parts. | Beats missing, out of order, or padded into extra paragraphs. |
| **length_signal_noise** | 0.10 | ~100 words, every line earning its place; high signal-to-noise (Tip #1). Nothing to cut. | Bloated toward 125 with filler, or under 50 and thin. |
| **cta** | 0.06 | Exactly one bold, specific, routable ask ("I'd like to start the interview process. Are you the right person, or can you point me to the recruiter who owns this req?"). Tip #5. | No ask, multiple asks, or a meek "would love to learn more." |
| **sounds_like_kanu** | 0.04 | Ownership-forward, business-outcome framing, crisp numbers, zero hype words. Indistinguishable from his real writing. | AI-generic; hype words present. |

Weights sum to 1.00. **urgency_social_proof + relevance_match dominate (0.42 combined)** — they are
exactly the two traits Kanu named as why the gold email is gold, and the hardest for a model to fake
without fabricating.

### Scoring `urgency_social_proof` when beat 3 is correctly omitted
The hard rule (no fabricated urgency) means a fixture with no live competing process MUST omit beat
3. On those fixtures, do NOT penalize the absence. Score this dimension on:
- **5** — omitted cleanly; the email still lands relevance + ask without an awkward gap, AND if any
  live process *did* exist in `Pipeline.md` the email would have used it (the skill clearly sources
  it live, doesn't hardcode "none").
- **1** — either fabricated/stretched a stale process to fill the gap (a hard-gate fail too), OR left
  a clumsy hole where the pivot should connect.

See `fixtures/` headers: each fixture declares whether a live process is available so the judge knows
which mode applies. At least one fixture is seeded WITH a live process specifically to test that the
skill reproduces the gold email's signature paragraph-two move.

---

## Scoring discipline for the judge

- **Score transferable traits, not verbatim text.** The gold email was written for Google Cloud. A
  Sierra email shouldn't contain Google facts. Ask: *does this email do what the gold email does?*
- **Anchor every score to a quoted line** from the candidate. No vibes-only scores.
- **Fabrication is a hard-gate fail, not a low score.** If beat 3 names a process not in live
  `Pipeline.md`, the email is disqualified (G2) — don't "give it a 2 for trying."
- **Reward the clean omission as much as the clean inclusion.** The gold email uses urgency because
  it was real. A fixture with no live process should omit it — and a model that omits cleanly scores
  as high as one that includes a real process. The skill is being tested on *correct live-sourcing*,
  not on always-having-a-paragraph-two.
- **Don't reward length for its own sake.** A tight 90-word email that does everything beats a
  120-word one that pads. Tip #1 is signal-to-noise, not word count.
- **Calibrate the gold email to ~4.7, not 5.** Reserve 5 for "beats the gold email on this
  dimension," so the loop can still detect improvement.

---

## Judge prompt (template)

```
You are scoring a cold-recruiter email against a gold-standard email Kanu Madhok loves.

GOLD EMAIL (and why it's gold):
<<< {{gold_email_file}} >>>

COLD-EMAIL PRINCIPLES (the 8 tips this is judged against):
<<< {{best_practices_excerpt}} >>>

CANDIDATE EMAIL (model={{model}}, role={{role_slug}}):
<<< {{candidate_email}} >>>

FIXTURE CONTEXT (declares whether a LIVE competing process is available for beat 3):
<<< {{fixture_header}} >>>

CANON (for fabrication backstop): {{resume_achievements_master_excerpt}}, {{pipeline_live_rows}}

Score the CANDIDATE 1–5 per dimension below, judging whether it DOES WHAT THE GOLD EMAIL DOES
(transferable traits), not whether it copies words. The candidate is for a DIFFERENT company, so
different facts are expected and correct.

CRITICAL: For `urgency_social_proof`, check the fixture header. If NO live process is available,
beat 3 MUST be omitted — score the clean omission as a 5, and treat any urgency in the body as a
fabrication red flag. If a live process IS available, reward the gold email's paragraph-two move
(real process + timeline + "closer match" pivot, target never the backup).

Dimensions + weights: {{rubric_table}}

For each dimension: integer 1–5 + a one-line `why` that QUOTES the candidate line that earned it.
Calibrate the gold email itself to ~4.7. Return JSON per ACCEPTANCE.md Stage 2.
```

---

## Re-tune log
- [x] Read the real gold email + `Cold Outreach Emails Best Practices.md`.
- [x] Set the two top dimensions to Kanu's stated reasons: relevance-match + urgency/social-proof.
- [x] Handled the omitted-beat-3 case so fixtures without a live process aren't penalized.
- [x] Seeded ≥1 fixture WITH a live process to test the signature paragraph-two move (see fixtures).
- [ ] Score the gold email against itself once execution is wired — confirm it lands ~4.7; if 5.0, tighten anchors.
