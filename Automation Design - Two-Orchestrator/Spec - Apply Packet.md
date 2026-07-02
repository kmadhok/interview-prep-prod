# Spec — Apply Packet (closing the prepped→applied gap)

_Drafted 2026-07-01. Parent: `Automation Architecture - Purpose.md` + `Automation Architecture - Two-Orchestrator Split.md`. Companions: `Spec - Orchestrator 1 (jd-to-ready prep).md` (this spec extends its finish line), `Spec - Applied Detector.md` (owns the nudge this spec's digest delivers)._

## Why this spec exists

The conveyor belt compresses machine latency to near zero, but the **apply gate sits exactly where human friction is highest**: Kanu applies from his iPhone or MacBook, and the tailored resume lives in a git repo — reachable on mobile only via github.com → login → navigate → download → save to Files (~10 taps before the ATS upload even starts). The result is the observed failure mode: **prepped roles sit and are not moved forward.** Prep inventory grows; applications don't.

The fix follows invariant 3's logic (every unit of friction at a human gate is a unit of dropped-output risk, same as the Applied Detector's argument for the `Applied` mark): move *all* remaining preparation across the gate, so the human action at apply-time is as close to one tap as the ATS allows.

**A prepped role's finish line is no longer "PDF in the repo." It is "packet on the phone."**

## What the packet is

A per-role bundle in a Google Drive folder `Apply Queue/`, written by the PC at the end of Pass A (Skill 1), containing:

1. **The tailored resume PDF** — named `<YYYY-MM-DD posted> · <Company> - <Role>.pdf` so the folder name-sorts by true posting freshness (see Freshness below).
2. **An application answers doc** — `<Company> - <Role> - Answers`: the canonical apply link at the top, then copy-paste blocks for the standard ATS questions (why-this-company, salary expectation, work authorization, notice period, location/remote, "describe a relevant project"), plus any custom questions visible on the posting. Content pulled from `Application Profile.md` + the role's `.classification.json` themes — never invented; missing facts stay as `[NUMBER?]`-style placeholders.

On iPhone: ATS "upload resume" → Files → Drive → tap. 3–4 taps, zero pre-work. Answers doc open in a second tab for copy-paste. On MacBook: Drive for Desktop makes the same folder local in Finder.

## `Application Profile.md` (new root reusable)

The apply-side answer source the workspace currently lacks (`Job Search Target Profile.md` is search-side only). One canonical file at root holding: salary expectation by geo band, work authorization, notice period, location/remote preferences, standard short answers in Kanu's voice. Maintained by the `interview-prep-reusables` skill like the other reusables. **Kanu seeds the facts once**; every packet's answers doc is generated from it. Never-invent rule applies — the generator copies or placeholders, it does not compose new claims.

## Freshness — true posted date + repost detection

Reposts game LinkedIn's "posted X days ago," and response rates decay sharply after a posting's first days — so queue order must come from the **ATS-native timestamp**, not LinkedIn's.

- **At intake (Skill 1):** resolve the canonical ATS posting (Greenhouse/Ashby/Lever public JSON endpoints where available; the LinkedIn posting's outbound link otherwise) and record `posted_date` + `canonical_url` in `.classification.json` and the Pipeline row.
- **Repost detection:** fuzzy-match company + title + JD text against the existing corpus (all `Job Description.md` under `Roles/` and `_Archived/`). A re-appearing JD keeps its *original* date as true age and gets a `repost` flag (repost correlates with ghost/evergreen postings — deprioritize, don't drop).
- **Queue order:** the date-prefixed filenames make `Apply Queue/` self-sorting; the digest lists roles newest-first.

## Lifecycle — Drive is a mirror, never truth (invariant 5)

`Pipeline.md` + role folders remain the only source of truth. The Drive folder is a **projection**, reconciled by the machine; **Kanu never files, moves, or deletes anything in Drive** (invariant 3).

| Event (truth changes) | Packet action (mirror follows) |
|---|---|
| Skill 1 finishes prep | Packet uploaded to `Apply Queue/`; `.apply-packet.json` written in role folder |
| Resume re-tailored (PDF hash ≠ recorded hash) | Packet PDF replaced in place (same Drive file ID — no duplicates) |
| Row marked `Applied` (either Applied Detector channel) | Packet moved to `Apply Queue/Applied/` |
| `verify-postings` grades the role DEAD | Packet removed; noted in digest |
| Role closed/rejected (folder → `_Archived/`) | Packet removed |

`.apply-packet.json` (per role folder, committed): Drive file IDs, uploaded PDF hash, upload timestamp, `posted_date`, `repost` flag, `easy_apply` flag. This is what makes the mirror reconcilable and re-runs idempotent — and, because it's in git, both machines read the same packet state after a pull.

**Reconcile pass:** runs on the PC (end of the hourly Pass B run, or its own light cron) — diff `Pipeline.md` + `.apply-packet.json` files against the Drive folder, apply the table above. Keeps the no-op guard: nothing changed → no writes, no commit.

## The digest (delivery for the Applied Detector's nudge — do not build twice)

`Spec - Applied Detector.md` already mandates the fail-loud nudge ("resume built N days ago, no `Applied` mark — did you apply?"). This spec supplies its **delivery channel** and widens it into the daily digest. One digest, one owner (PC, end of the daily Pass A run):

> **Apply Queue: 3 ready** (newest: Scribd, posted 2d) · oldest 6d — did you apply? · **2 outreach drafts unsent** · 1 posting died (removed)

- **Channel: ntfy.sh push** to a private topic; free iOS app; one `curl` from the PC cron. Glanceable, zero inbox involvement, and works around the Gmail MCP having no send capability.
- Contents: ready-count + newest/oldest ages, the Applied Detector's prepped-but-not-applied nudges, unsent staged drafts, dead postings cleaned, and (once follow-up cadence lands) overdue nudges. Link to the Drive folder.
- The Applied Detector's nudge requirement is **satisfied by** this digest; the secretary/report keeps only its audit-note form.

## Two-machine rules (PC + MacBook both push/pull this repo)

1. **The PC is the sole packet writer** (it owns Pass A/B). The MacBook never uploads/reconciles packets — even if a skill is run there manually, the packet step is PC-gated (hostname check or config flag). Two writers = duplicate uploads.
2. **All packet state lives in committed files** (`.apply-packet.json`, Pipeline row fields) — never machine-local. A MacBook session that pulls sees identical state.
3. **Repo-relative paths only** in the new skill steps and this spec's tooling. (Existing skill descriptions still carry `/Users/kanumadhok/...` absolute paths — fix opportunistically.)
4. Existing rule unchanged: `git pull` before editing `Pipeline.md`; the reconcile pass pulls before diffing.

## Invariant scorecard (per Purpose §"How to judge a design change")

1. **Human-gated output** — unchanged: the packet stages, Kanu still clicks apply. Drive uploads are to Kanu's own account, not outward. ✔
2. **LinkedIn budget** — zero LinkedIn calls added (ATS endpoints are public JSON). ✔
3. **Less human attention** — the point of the spec: ~10 taps → ~3, answers pre-drafted, queue self-cleaning, digest pushed instead of pulled. ✔
4. **Fail loud** — digest surfaces the nudge daily; stale-PDF and dead-posting states become visible events instead of silent drift. ✔
5. **Simpler?** — adds one mirror + reconcile pass; paid for by deleting the manual github.com retrieval path entirely.

Rejected on these grounds: **WIP cap on Pass A** (throttling prep regresses "compress time-to-applied"; freshness sort + dead-posting expiry achieves the small-live-queue effect without it) and **Gmail-draft delivery of packets** (clutters Drafts alongside staged outreach; one fat-thumb from an accidental send — invariant 1's spirit).

## What this spec does NOT do

- Does **not** submit applications or fill ATS forms (a possible later MacBook `batch-apply` skill is out of scope — revisit only if Mac apply-sprints become a habit).
- Does **not** touch LinkedIn.
- Does **not** create a state database — `.apply-packet.json` is a per-role artifact file, same pattern as `.classification.json`.
- Does **not** let the e2e test write to the real queue: `two-orchestrator-e2e-test` runs must target a `_test/Apply Queue/` Drive folder or skip the upload step.

## Resolved decisions (2026-07-01)

1. **Delivery: Drive MCP** — Drive for Desktop is not installed on the PC. Known liability, observed same day: the connector token expires and requires interactive re-authorization (a Drive search failed with exactly this during spec work). Build requirements that follow: (a) **headless-cron verification is build step 0**; (b) an upload/reconcile failure must surface as a digest line (_"Drive upload failed — reauthorize the connector"_), never a silent skip (invariant 4); (c) if expiry proves chronic, revisit installing Drive for Desktop — a synced-folder file copy has no auth to expire.
2. **`Application Profile.md` seeded** — salary $130k+ base, U.S. citizen (no sponsorship required), 2-week notice. Phone / LinkedIn URL / location preference remain as placeholders for Kanu to fill.
3. **ntfy topic: `job-auto`, with a random suffix added at setup** (e.g. `job-auto-x7k2m9`). ntfy topics are unauthenticated — the topic name *is* the password, and a short guessable one lets anyone read the digest or push to the phone. Only the iPhone app and the PC cron need to know the suffixed name.
4. **Easy Apply flag: in v1** — recorded at intake in `.apply-packet.json`, surfaced in the digest so phone sessions can target Easy Apply roles.

## Build delta

1. **Skill 1 finish line** (`jd-to-ready`): + resolve canonical ATS URL & `posted_date` (+ repost fuzzy-match) → `.classification.json`; + generate answers doc from `Application Profile.md`; + upload packet; + write `.apply-packet.json`.
2. **New root reusable**: `Application Profile.md` (seeded by Kanu via `interview-prep-reusables`).
3. **Reconcile pass** (PC): mirror table above; hangs off the hourly Pass B run.
4. **Digest** (PC, daily): counts + nudges + ntfy push; absorbs the Applied Detector's nudge delivery.
5. **e2e test**: packet step test-mode.
6. Later, separate spec if wanted: follow-up cadence (nudge-after-silence timing) feeding the same digest.
