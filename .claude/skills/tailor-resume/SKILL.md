---
name: tailor-resume
description: Tailor Kanu's resume for a specific role. Use when he wants to customize bullets, reorder sections, or adjust emphasis for a particular JD. Pulls only from canonical Resume Achievements Master.md. Runs standalone or as a step inside jd-to-ready.
---

# Tailor Resume

Customize Kanu's resume for a specific role and JD, pulling only from canonical, verified achievements. This is the single authoritative definition of resume tailoring — `jd-to-ready` calls this skill rather than reimplementing it.

## Contract

**Modes:** `standalone` (default) | `pipeline`

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `role_folder` | yes | e.g. `Morningstar - Product AI Engineer`. Output is written here. |
| `jd` | **both modes** | The JD text or file. Needed in BOTH modes: standalone extracts themes from it; pipeline still needs it for the "JD wants a number not in proof points → leave out" check (step 8) and for JD-driven bullet trimming. |
| `themes[]` | pipeline mode | Pre-classified theme tags from jd-to-ready step 2. In `pipeline`, use these instead of extracting. |
| `archetype` | pipeline mode | The role archetype (drives F1/U1 inclusion). In `standalone`, infer from the JD. |
| `mode` | yes | `standalone` (extract themes from JD) or `pipeline` (themes/archetype supplied, but `jd` still passed). Default `standalone`. |

**Outputs**
| What | When | Where |
|------|------|-------|
| Tailored resume `.md` | always | `<role_folder>/Kanu Madhok Resume - <Company> <Short Role>.md` |
| `gaps[]` | always | **Returned to the caller** using the **cross-skill gap schema** (shared by all primitives): list of `{source: "resume", kind, detail}` objects — `kind` is `"no-canonical-match"` or `"needs-stronger-claim"`; `detail` carries the theme + the `[VERIFY: ...]` note, e.g. `{source: "resume", kind: "no-canonical-match", detail: "JD wants Kubernetes depth; not in master; [VERIFY: ...]"}`. The shared `source` field lets jd-to-ready merge resume-gaps + contact-gaps into one step-6 report / step-7 log. If no gaps, return `[]` explicitly. |

**Standalone:** `tailor-resume(role_folder, jd, mode: standalone)`
**Pipeline (from jd-to-ready):** `tailor-resume(role_folder, jd, themes[], archetype, mode: pipeline)`

**"Short Role" derivation (for the filename):** the JD title trimmed of trailing qualifiers to ≤4 words — e.g. "AVP AI Engineer, Innovation" → "AVP AI Engineer"; "Product AI Engineer" → "Product AI Engineer". Match an existing `Kanu Madhok Resume - <Company> ...md` in the role folder if one is already there.

## Process

**HARD RULE: canonical only.** `Resume Achievements Master.md` contains only resume-safe achievements. It is the only source for tailored resume claims. The separate `Resume Claims To Verify.md` file is a private verification queue, not source material. Until Kanu explicitly verifies a claim and it is promoted into `Resume Achievements Master.md`, it does not exist for resume purposes. If a JD theme appears to need something from the verification queue, do NOT silently substitute — lead with the closest canonical match and record the gap in `gaps[]`.

1. **Get themes.**
   - `standalone` mode: read the JD and extract the top 5 themes/requirements; infer the role archetype.
   - `pipeline` mode: use the supplied `themes[]` and `archetype` — do not re-derive.
2. Open `Resume Achievements Master.md`. Read the `Resume Tailoring Contract`, `# Canonical Achievements`, and `# Canonical Skills` block. Treat `Resume Claims To Verify.md` as off-limits for drafting.
3. For each theme, pull the canonical achievements tagged with it. **Anchor every resume with A1** (self-service analytics agent — strongest end-to-end + eval story) and at least one of **A3, A4, or A5**.
4. Select 4–6 Walmart achievements total from {A1, A2, A3, A4, A5, A6, A7}. Include **I1** (Innovare) for the early-career experience line, **F1** if the role is consulting / client-facing / FDE-flavored, and **U1** if the role values experimentation / multi-LLM / research. (Archetype drives F1/U1.)
5. For each canonical achievement, start from its canonical bullet and apply ONLY the master's **allowed transformations** (reorder, shorten/lengthen without changing facts, swap vocabulary for an equivalent claim, use a subset of verified proof points). JD-driven trimming toward the role's lead themes is expected and allowed — that is how the existing tailored resumes were produced. Do NOT add facts, numbers, or status upgrades outside the canonical "verified proof points." (Do not treat "verbatim canonical" as a requirement; the master contract explicitly permits trimming.)
6. **Skills section:** start from the `Canonical Skills` block; reorder the groups to match JD priority and trim to JD-relevant items. You may surface a canonical skill under a JD-aligned group label. Do NOT add any skill that is not in the Canonical Skills block or a verified project entry (no items from `Resume Claims To Verify.md` or older tailored resumes). If the JD names a tool that is genuinely demonstrated by a canonical achievement, it's fine; otherwise record it in `gaps[]`.
7. Keep the contact block + selected-project line from the canonical header. The live demo URL is canonical — use it.
8. Quantified outcomes only as they appear in the canonical "verified proof points" list. If a JD wants a number not in that list, leave it out — never invent.

## Rules
- Don't rewrite bullets from scratch — pull from the master library. Older tailored resumes are outputs, not evidence.
- Never use anything from `Resume Claims To Verify.md` unless promoted to canonical. Before saving, scan the draft against it and remove any matching unverified claim.
- No hype words: no "leveraged," "spearheaded," "synergy," "drove."
- One page unless the JD signals otherwise.

## Format
Match the Deloitte FDE GPS resume's structure (`# Kanu Madhok` header, `## PROFESSIONAL EXPERIENCE`, `## SELECTED PROJECT`, `## SKILLS`, `## EDUCATION`). Bullets, not paragraphs. Sub-headings for company + role + dates as in the Deloitte resume.

**Canonical-only exception — fixed biographical blocks.** The contact/header block, the EDUCATION block (degrees + GPAs), and the dates/titles are stable biographical facts not stored as achievement entries in the master. Copy them from the master's `Header - Contact Block` where present, and from the gold Deloitte FDE GPS resume for Education. These fixed blocks are the ONE exception to "older resumes are outputs not evidence" — they are biographical constants, not claims. Everything else (every bullet, every skill) follows the canonical-only rule.

## Output filename

`<role_folder>/Kanu Madhok Resume - <Company> <Short Role>.md` — match existing folders:
- `Kanu Madhok Resume - Morningstar Product AI Engineer.md`
- `Kanu Madhok Resume - Harrison Street AVP AI Engineer.md`
- `Kanu Madhok Resume - Deloitte FDE GPS.md` (gold reference — match its format)

Do NOT generate `.docx` or `.pdf` automatically. Mention in the output that those can be regenerated on request.

## Self-check before declaring done
- [ ] Every bullet derives from a canonical A/U/F/I entry, using only the master's allowed transformations (no new facts/numbers/status upgrades).
- [ ] Every skill in the Skills section traces to the `Canonical Skills` block or a verified project entry (reordering/trimming OK; no non-canonical additions).
- [ ] No number written that isn't in a canonical "verified proof points" list.
- [ ] A1 is present and at least one of A3/A4/A5.
- [ ] Fixed blocks (contact header, EDUCATION) copied per the canonical-only exception, not invented.
- [ ] Every unmatched JD theme is captured in the returned `gaps[]` as a structured object (empty list `[]` if none).
- [ ] Filename matches `Kanu Madhok Resume - <Company> <Short Role>.md` per the Short-Role rule.
