# Scoreboard — Write-Outreach Loop, Run 1

**Date:** 2026-06-28 · **Models (strongest per provider):** claude-opus-4-8 · gpt-5.5 (codex) · gemini-2.5-pro
**Anchor:** `fixtures/gold-email.md` (Google Cloud / FDE I). **Judge:** in-harness rubric pass (single, not yet two-judge cross-family — see caveat).

> Caveat: this first judge pass was run by the orchestrating Claude model. Per `RUNNER.md`, a decisive
> run should use a **blinded, cross-family two-judge average** so the judge isn't a sibling of a
> contestant (claude-opus is a sibling of the claude contestant). Treat the standings as strong-signal,
> not final, until re-judged blind. The mechanical gates (G1–G9) below are model-agnostic and final.

---

## Stage 0 — Reproducibility (R1/R2)
| Model | Skill edit | Files touched | Verdict |
|-------|-----------|---------------|---------|
| claude | ✅ 2 commits | `SKILL.md` (+4) + `Outreach Templates.md` (+21) | PASS — most substantial edit |
| codex | ✅ 1 commit | `SKILL.md` (+24) | PASS — focused on the skill itself |
| gemini | ✅ 1 commit | `Outreach Templates.md` (2 lines) | PASS — lightest touch |

All three: emails follow from committed skill/template rules, not hand-authoring. No disqualifications.

## Stage 1 — Hard gates (G1–G9), mechanical, model-agnostic
**All 9 emails PASS.** subjects 49–69 chars (credential-first), bodies 62–118 words, zero em-dashes
(gemini's `30–60` is an en-dash, not the banned em-dash), no banned phrases, exact signature, one CTA.
No disqualifications. (Script: `/tmp/gate_check.py`.)

## Stage 2 — Judge (rubric dimensions; gold-email traits weighted highest)

Per-email weighted total (1–5). Top weights: urgency_social_proof 0.22, relevance_match 0.20.

| Email | claude | codex | gemini | Why the spread |
|-------|:------:|:-----:|:------:|----------------|
| cohere-fde (LIVE) | **4.7** | 4.6 | 4.5 | All 3 use the seeded live process correctly. Claude's pivot is richest ("production agents on North in customer environments"); gemini's is slightly wordier ("work on its North enterprise platform"). |
| distyl-fde (OMIT) | **4.6** | 4.5 | **3.3** | claude/codex both: number + JD "closer match" pivot, clean omission. **Gemini dropped beat 4 entirely** — number, then straight to the ask. No why-this-company, no pivot. Structure + relevance miss. |
| sierra-strategist (OMIT) | **4.7** | 4.5 | **3.6** | claude/codex pick the strategist-flavored A1 achievement WITH the 67-table metric + Product/DS spec line. **Gemini's sierra email has NO number** (concreteness fail vs. the gold email's core move). |
| **Mean** | **4.67** | **4.53** | **3.80** | |

### Tie-break ladder (not needed — clear separation)
1. Fewest gate failures: all tied at 0.
2. Head-to-head on cohere-fde: claude > codex > gemini.

---

## Result: **Claude (claude-opus-4-8) wins Run 1**, codex a close second.

- **Claude** — highest fidelity to the gold email on both load-bearing traits, on all 3 roles. Richest
  relevance pivots, carried the canonical number every time, even added correct extra proof (11,000
  queries / MCP-RAG on distyl). Made the most substantial skill edit (SKILL.md + templates). Tiny knock:
  bodies run long (117/100/118) — top of the 50–125 range vs. codex's leaner 105/80/88.
- **Codex** — nearly tied. Tightest signal-to-noise (shortest valid bodies), self-validated its own
  gates, edited SKILL.md directly. Pivots slightly more generic than claude's ("closer match for what
  I do next" vs. a role-specific clause). Would likely win on a brevity-weighted rubric.
- **Gemini** — strong on cohere (matched the gold opener + full pivot) but **inconsistent across roles**:
  dropped beat 4 on distyl and the beat-2 number on sierra. Its skill edit was the lightest (2 template
  lines), which under-specified the per-role behavior, and the emails show it. Lowest mean.

## What this says about the SKILL edits (the actual deliverable)
- The winning artifact is **claude's branch** (`wo-test/claude`): `SKILL.md` + `Outreach Templates.md`
  changes that made the relevance pivot load-bearing in both beat-3 modes.
- **Codex's SKILL.md edit is worth grafting** — its explicit live-vs-omit handling and subject
  compression are cleaner than claude's. Best-of-both: merge claude's branch, cherry-pick codex's
  subject-compression + beat-3 rule.
- **Lesson:** the depth of the skill edit predicted email consistency. Gemini's 2-line edit → most
  variance across roles. The benchmark rewarded editing the skill substantively, exactly as intended.

## Next
- [ ] Re-judge **blind + cross-family** (e.g. a Gemini judge + a non-Anthropic judge) before promoting,
      to remove same-family bias on claude's score.
- [ ] If standings hold: merge `wo-test/claude` skill diff → `main`, cherry-pick codex's beat-3/subject
      rule, then sync to global `~/.claude/skills/write-outreach/`.
- [ ] Tear down worktrees + `wo-test/*` branches.
