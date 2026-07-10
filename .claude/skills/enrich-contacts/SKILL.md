---
name: enrich-contacts
description: Scrape the LinkedIn activity (posts, reposts, comments) of recruiters already found by find-contacts, to surface (a) NEW on-target people the keyword search missed and (b) a real personalized hook per recruiter for outreach. Pipeline step that runs AFTER find-contacts and BEFORE write-outreach. Reads the shared scored-ledger artifact find-contacts wrote, scores new people on find-contacts' published rubric, appends + re-sorts the ledger.
---

# Enrich Contacts

Take the recruiters `find-contacts` already surfaced and **read what they've been doing** — recent posts, reposts, and comments — because a recruiter's *activity* often points at the right person the keyword search couldn't reach. A practice-aligned recruiter who reposts "we're hiring an AI Specialist Leader" has just told you (a) the exact req is live and (b) who the sourcer/author is — a contact a flat title search never returns.

**Why this is a separate skill, not part of find-contacts.** `find-contacts` answers *"given a JD, who are the right people?"* (discovery). This skill answers a different question on a different input: *"given people who already exist, what are they signalling, and who did they amplify?"* (enrichment). Bolting it into `find-contacts` would put two responsibilities in one image.

**How the two skills share work — an artifact, not a callback.** `find-contacts` writes a scored-ledger file (`<role_folder>/.contacts-ledger.md`) with a published rubric (factors + weights + the Practice-evidence lock, defined in find-contacts Sub-step 2). This skill **reads that ledger, applies that same published rubric** to any new person it finds, **appends** them as `Source: enrich` rows, **re-sorts**, and writes the file back. The pipeline stays strictly linear (find-contacts → enrich → write-outreach) with no loop back into find-contacts. Ranking *logic* still lives in exactly one place — find-contacts owns the rubric; this skill only *applies* the published rubric, it never invents its own factors or weights. (If find-contacts changes a weight, this skill inherits it automatically because it reads the rubric from there, not from a copy.)

**Core principle (provenance, never invention).** Everything this skill writes is traceable to a specific piece of scraped activity: "found via Gina Stewart's repost of Matthew Lee, 2mo ago." A hook or an appended contact with no activity citation is a bug, not a result. Same discipline as the find-contacts ledger — every claim quotes its evidence, and every appended score quotes its Practice-evidence exactly as a `search` row must.

**LinkedIn discipline:** call `mcp__linkedin__*` tools directly, one at a time — sequential, never parallel (the scraper is not concurrency-safe). No caps, no delays. See `linkedin-mcp-operations` for the transport invariant and per-op reference. If a call errors, follow that skill (sleep 3, retry once, then stop and diagnose).


## Standalone trace (mandatory when invoked directly)

When this skill runs **standalone** (not as a step inside `jd-to-ready` or `stage-outreach`), it must trace itself. When it runs **inside an orchestrator, skip this section entirely** — the orchestrator's run owns the step events (never open a second run).

```bash
python3 "<repo root>/scripts/trace_step.py" start-run --run-type primitive --skill enrich-contacts --company "<company>" --role "<role>"
python3 "<repo root>/scripts/trace_step.py" begin --step main --primitive enrich-contacts --mode standalone --prediction "<one-line checkable claim>" --reason "<why the user invoked this now>" --sources '[".claude/skills/enrich-contacts/SKILL.md", "<role folder>/.contacts-ledger.md"]'
# ... do the work ...
UNKNOWN_TOKENS='{"input":null,"output":null,"cache_read":null,"cache_write":null,"total":null,"source":null,"notes":"runtime did not expose token counts"}'
python3 "<repo root>/scripts/trace_step.py" end --step main --primitive enrich-contacts --mode standalone --status "ok|partial|failed" --prediction-met "true|false|partial|unknown" --produced '["<files written>"]' --gaps '<gaps or []>' --failure-pattern "" --tokens "$UNKNOWN_TOKENS"
python3 "<repo root>/scripts/trace_step.py" finish-run --status ok --gaps '[]' --files-written '["<files written>"]'
python3 "<repo root>/scripts/render_run_report.py" "<repo root>/runs/<run-id>"
```

Adjust `--sources` to the files actually read this run; the ones above are this skill's canonical inputs. Mention the rendered report path in your summary.

## Contract

**Pipeline only.** This skill does not run standalone — it consumes `find-contacts(full)` output. (If you want to scrape one arbitrary person's activity ad-hoc, call `mcp__linkedin__get_person_profile` with `sections: "posts"` directly per `linkedin-mcp-operations`; you don't need this skill for a one-off.)

**Inputs**
| Name | Required | Notes |
|------|----------|-------|
| `role_folder` | yes | Where `find-contacts` wrote `.contacts-ledger.md`. This skill reads it, appends, and writes it back here. |
| `team` | yes | The `{team, parent_practice, function}` map from `find-contacts` Sub-step 0. Used to judge whether a scraped post is on-target (an AI-practice req vs. a generic culture post), and to score appended rows' Practice factor. |
| `role_title` | yes | The target role — to judge hook relevance and whether a surfaced person is a plausible new contact. |
| `jd_region` | yes | The JD's cities/locations — needed to score appended people's Loc factor on the published rubric (without it, location scoring degrades, as a real run showed). |

(The recruiter list to scrape is read from the ledger's recruiter rows — not passed separately. **All recruiter rows are scraped**, not just the top pick — a Gina-style repost can come from any of them.)

**Outputs**
| What | When | Where |
|------|------|-------|
| Updated `.contacts-ledger.md` | always | The same `<role_folder>/.contacts-ledger.md`, now with activity-surfaced people appended as `Source: enrich` rows (scored on the published rubric, with Provenance) and the whole ledger re-sorted by Total (gated on practice-match). This is the authoritative ranking write-outreach reads. |
| `hooks[]` | always | One per recruiter where a usable signal was found: `{recruiter, hook_text, source, date, url}` — a real recent post/repost to reference in outreach beat 1. Forwarded to `write-outreach`. Empty `[]` if a recruiter had no usable activity. |
| `gaps[]` | always | Cross-skill schema `{source: "enrich", kind, detail}`. Kinds: `no-activity` (recruiter's feed empty/inaccessible), `stale-activity` (newest post >12mo old — no fresh hook), `surfaced-via-activity` (a new person was appended — names who + provenance so step-7 logs it). Empty `[]` if none. |

**Pipeline (from jd-to-ready, after find-contacts(full) has written the ledger):**
`enrich-contacts(role_folder, team, role_title, jd_region)`
→ updates `.contacts-ledger.md` in place; `hooks[]` forward into `write-outreach`.

## Process

**Sub-step 0 — Read the ledger.** Open `<role_folder>/.contacts-ledger.md` (written by `find-contacts(full)`). Read the rubric header (factors, weights, the Practice-evidence lock, the schema) — you will *apply* this rubric to any new people, never invent your own. The recruiter rows are your scrape list. If the file is missing, that's a `gaps[]` `{source:"enrich", kind:"no-ledger", detail:"find-contacts ledger not found; nothing to enrich"}` — stop cleanly, don't fabricate one.

**Sub-step 1 — Scrape each recruiter's activity (sequential).** For every recruiter row in the ledger, one at a time:

```
mcp__linkedin__get_person_profile(linkedin_username, sections: "posts", max_scrolls: 15)
```

`sections: "posts"` is the activity feed (authored posts, reposts, sometimes comments). `max_scrolls: 15` pages deep enough to reach an on-target repost that isn't the newest item. **One call per recruiter, awaited before the next** — never batch. Reposts are the most reliably-visible activity; likes/reactions are often hidden by LinkedIn and may not appear — that's a scraper limit, not a miss, note it as `no-activity` if a feed returns nothing.

**Sub-step 2 — Triage each activity item against the team map.** For each post/repost in a recruiter's feed, classify:

- **On-target req** — names a role in the role's `parent_practice` / `team` / `function`, or an adjacent hiring post (e.g. for the Deloitte S&T AI role: "SFL Scientific hiring AI Specialist Leader", "S&T Analytics hiring a Senior Manager"). **This is the high-value signal.** A repost of a hiring post is the recruiter telling you the req is live.
- **Hook-worthy but not a req** — a practice-relevant post (a thought-leadership share about the practice, a team milestone) usable as a personalized opener even though it names no role.
- **Noise** — generic culture/DEI/return-to-work posts, years-old items, unrelated practices. Skip.

Judge relevance against `team` — an "Insurance Cost Transformation" repost is noise for an *AI & Analytics* role even though the same recruiter posted it.

**Sub-step 3 — Extract two things from on-target / hook-worthy items:**

1. **A hook** → `hooks[]`. Quote the specific item so `write-outreach` can reference it honestly in beat 1: *"I saw you recently reposted the SFL Scientific AI Specialist Leader opening."* Record `source` (who authored it), `date`, `url`. Prefer the **most recent on-target** item; fall back to the most recent hook-worthy one. One hook per recruiter max — the freshest, most on-target.

2. **New people.** From an on-target req repost, the **post author** and any **sourcer/recruiter named in the body** ("DM me", "reach out to <name>") are new contacts the keyword search missed. Capture name + `linkedin_username` (from the post author reference) + their title as shown + `provenance` citing the activity. If the repost alone is thin on title/location, you MAY do ONE sequential `get_person_profile` per new person to confirm (sequential, never batched).

**Sub-step 4 — Score the new people on the published rubric, then append + re-sort the ledger.**

For each new person, **apply find-contacts' rubric** (read from the ledger header — you apply it, you don't redefine it): score Practice (0-3, with a quoted Practice-evidence string — same anti-intuition lock as a `search` row), Loc (0-2 vs `jd_region`), Title (0-2), Tenure (0-1), Snr (0-1); compute Total. A repost-surfaced person earns **no bonus for how they were found** — score on merits exactly like a search row (this is the discipline a real run validated: an activity-surfaced sourcer who is RI-based and not practice-named correctly scored *below* the practice-aligned recruiters, not above).

Then write the ledger back to `<role_folder>/.contacts-ledger.md`:
- **Append** each new person as a row with `Source: enrich`, the quoted Provenance, and the full scored row.
- **Re-sort** the whole ledger by Total within each category (gated on practice-match per find-contacts' completeness gate).
- Leave all `search` rows intact; you only add and re-order.

The re-sorted ledger is the authoritative ranking. `write-outreach` reads its top rows — there is no separate "top_picks" to re-capture, and no stale-pick risk, because there is one file and one sort.

`hooks[]` → return to the caller, forwarded to `write-outreach` as the beat-1 trigger line per its hook-finding precedence.

## Hard rules
- **Sequential LinkedIn calls only** — one `get_person_profile` in flight at a time, never parallel (see `linkedin-mcp-operations`).
- **Never invent a hook or a contact.** Every hook and every appended row must cite a real scraped activity item (author, date, text). No citation → it doesn't exist. A recruiter with an empty/inaccessible feed yields `{source:"enrich", kind:"no-activity"}`, not a fabricated opener.
- **Apply find-contacts' rubric; never redefine it.** This skill *scores* appended people, but only with the factors/weights/Practice-evidence lock published in the ledger header. It owns no scoring logic of its own — if it can't read the rubric from the ledger, it stops (`no-ledger` gap), it does not improvise one. This is what keeps ranking logic in one place even though two skills write the file.
- **No bonus for activity-surfaced people.** An appended row is scored exactly like a search row — being found via a repost is provenance, not a score factor.
- **Relevance is judged against the `team` map**, not keyword overlap — a recruiter who recruits for five practices will post about all five; only the on-target practice's activity counts.
- Profile scrapes are visible to the target (profile-view logged). That's acceptable for cold-outreach prep, but don't scrape beyond the recruiters in the ledger + the new people they surface.
