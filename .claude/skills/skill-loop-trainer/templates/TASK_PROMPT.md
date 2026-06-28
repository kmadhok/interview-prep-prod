<!-- TEMPLATE — skill-loop-trainer. Copy into "{{NAME}} Test/" and fill {{PLACEHOLDERS}}.
     The cohere/distyl/recruiter/em-dash details below are the WORKED write-outreach example —
     replace them with the target skill's real fixtures, gates, and gold-example traits.
     Reference impl: repo-root "Write Outreach Test/". -->

# Task Prompt — handed verbatim to every contestant model

> This is the exact prompt each worktree's model runs. Same prompt for Claude, Codex, Gemini.
> Do not customize per model — that's the point of the benchmark.

---

You are improving the `{{TARGET_SKILL}}` skill at `~/.claude/skills/{{TARGET_SKILL}}/SKILL.md`,
whose source-of-truth spec is `Outreach Templates.md` (section 1 = cold recruiter intro).

**Your goal:** make the cold-recruiter emails this skill produces as close as possible to the
gold-standard email in `{{NAME}} Test/fixtures/gold-email.md`. You are judged on the
emails, but you must achieve the improvement by EDITING THE SKILL, not by hand-writing emails.

## Do exactly this, in order

1. **Read** `fixtures/gold-email.md`, `Outreach Templates.md` (§1), the current
   `{{TARGET_SKILL}}/SKILL.md`, `Resume Achievements Master.md`, and `Demo Portfolio.md`.

2. **Edit the skill.** Improve `SKILL.md` and/or `Outreach Templates.md` §1 so the emails it
   generates match the gold email's traits (voice, hook discipline, structure, concreteness,
   length, CTA). Commit your diff.
   - You MAY change: process steps, the 5-beat guidance, hook-finding logic, the template
     prose, the length target wording, the subject formula.
   - You MUST NOT change the hard invariants: draft-only, no fabrication, the banned-phrase
     list, the body em-dash gate, the exact signature block, "one CTA." (See SPEC §4.)

3. **Generate emails.** Run the improved skill in `drip` mode, **recruiter contact only**, on
   each of the 3 fixtures:
   - `fixtures/cohere-fde.md`
   - `fixtures/distyl-fde.md`
   - `fixtures/sierra-strategist.md`
   Each fixture gives you the role, company, recruiter, verified email, archetype, lead theme,
   and an explicit **beat-3 mode**:
   - If the fixture declares a **LIVE PROCESS PROVIDED** block, USE that competing-process list as
     beat 3 — execute the gold email's paragraph-two move (real process + timeline + "closer match"
     pivot, target never the backup). Use only what the fixture declares; invent nothing beyond it.
   - If the fixture says **OMIT**, source urgency live from `Pipeline.md`, find nothing eligible,
     and omit beat 3 cleanly. Do NOT fabricate or stretch a stale process to fill it.

4. **Write outputs** to `{{NAME}} Test/runs/<your-model-name>/<role-slug>.md`. Each file:
   the subject, the body, the signature, and a one-line note on which hook you used and why.

## Hard rules (violating any = your run is disqualified)
- Every number and hook must be REAL — traceable to `Resume Achievements Master.md` or live
  `Pipeline.md`. Invent nothing.
- Body: zero em dashes (U+2014). 50–125 words. No banned phrases (Outreach Templates §1 line 8).
- Subject < 70 chars, leads with the credential.
- Exact signature block.
- Draft only — never call any send tool.
- The emails must be REPRODUCIBLE by re-running your edited skill. If they can't be
  regenerated from the skill, the run is disqualified.

## What "done" looks like
- A committed skill diff.
- 3 generated email files under `runs/<your-model-name>/`.
- A one-paragraph note (in `runs/<your-model-name>/NOTES.md`) on what you changed in the skill
  and why you believe it moves the emails closer to the gold email.
