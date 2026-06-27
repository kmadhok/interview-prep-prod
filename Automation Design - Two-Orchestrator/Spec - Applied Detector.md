# Spec — Applied Detector (the `applied` state)

_Drafted 2026-06-27. The missing seam. Parent: `Automation Architecture - Purpose.md` + `Automation Architecture - Two-Orchestrator Split.md`. Companions: `Spec - Orchestrator 1 (jd-to-ready prep).md`, `Spec - Orchestrator 2 (stage-outreach).md`._

## Why this spec exists

`applied` is the **pivot of the whole machine**: it gates everything expensive and high-value on the apply-side (find recruiter → verify email → draft outreach). The two orchestrator specs both *depend* on it and neither *defines* it — Skill 2's trigger is "a Pipeline row marked Applied," but nothing says **how that mark gets there, how reliably, or how fast.** That under-specification is the design's real weak seam (not "Kanu's memory" — that's only one of the two sources). This spec pins down the detector so the seam is owned, the latency is bounded, and the one silent-failure path is made loud.

## What `applied` means

A role is `applied` when **Kanu has submitted an application on the employer's ATS.** That real-world event is observed through two independent channels — neither is allowed to be the sole source of truth:

| Source | Signal | Owner | Confidence |
|---|---|---|---|
| **Direct** | Kanu edits the Pipeline row → `Applied` | Kanu | High (intentional) |
| **Backstop** | Cloud routine's Gmail sweep finds an application-acknowledgment → marks the row `Applied` | cloud secretary | Medium (ack mail is noisy / sometimes absent) |

Either channel sets the state. The point of two channels is that **`applied` never depends on Kanu remembering** — the Gmail sweep catches what he forgets, and Kanu's direct mark catches applications that send no ack. The detector's job is to make these two agree with reality, promptly and without false positives.

## Channel 1 — Gmail-ack detection (the backstop, specified)

Runs inside the cloud secretary's Gmail sweep (step 1 of the routine). Today this is described only as "app ack → mark row Applied"; this section makes it a rule.

### What counts as an application acknowledgment

A thread is an ack **iff all** of:
1. **From the employer or its ATS** (greenhouse / lever / workday / icims / ashby / smartrecruiters / myworkdayjobs, or the company's own ATS domain), **not** a staffing agency or job-board alert.
2. **Body matches an ack pattern**, e.g. _"thank you for applying / your application has been received / we've received your application / a member of our recruiting team will review."_
3. **Maps to a tracked role** — the company (and, when present, the req title/ID) matches an existing Pipeline row.

### What is explicitly NOT an ack (guard against false positives)

- LinkedIn / Indeed / job-board **"your application was sent" alerts** for jobs not in the pipeline (these are the top of funnel, not a tracked apply).
- Staffing-agency / off-platform recruiter mail (suspicious links, non-employer domains) — same exclusion the routine already applies.
- Newsletters, promos, resident/digest mail.
- An ack whose company **doesn't match any Pipeline row** → do **not** auto-create a role from an ack. Instead flag in the audit note: _"ack from <company> — no tracked role; intake via interview-prep-intake if wanted."_ (This is the existing NBA/Greg-Smith handling, made a rule.)

### Action on a confirmed ack

1. Set the role's Pipeline row to `Applied` (keep any existing stage detail; don't downgrade a row already past `applied`, e.g. one in interview).
2. Prepend a dated audit note on `_Last updated:` (the existing chained, `(Gmail-verified)` format) recording the ack: source, date, req if present.
3. Record the ack date in the role folder (so Channel-2 reconciliation and Skill 2's urgency line can read it).
4. **Never** stage outreach from this pass — detection only. Drafting is the drafter's job (Skill 2 / the slow drafting cadence), never the secretary's.

## Channel 2 — Kanu's direct mark (specified)

Kanu edits the Pipeline row to `Applied`. To honor invariant 3 ("no babysitting"), this action must be **near-zero-effort**, because every unit of friction here is a unit of forgotten-apply risk.

- The mark is a single, unambiguous token in the row (`Applied`) the worklist readers already key on. Keep it one token — no free-text variants the poll can miss.
- If Kanu marks `Applied` **before** any ack arrives, the direct mark wins immediately; a later ack is reconciled as confirmation, not a second state change.
- If an ack arrives **before** Kanu marks it, Channel 1 sets `applied` and Kanu's later edit is a no-op. Idempotent either way.

## Cadence — the secretary runs often; the drafter does not

This is the core operational decision the orchestrator specs leave implicit. The cloud routine today bundles two sub-jobs of **different latency classes** into one twice-daily run:

| Sub-job | Latency-sensitive? | Cadence | Rationale |
|---|---|---|---|
| **Sweep → reconcile → mark `applied`** (this detector) | **Yes** | **hourly / 30-min** | Cheap Gmail reads; it's the trigger for the entire apply-side. Frequent runs make `applied` near-real-time, so Skill 2's hourly poll fires promptly end-to-end. |
| **Stage outreach drafts** | No | 2×/day (or PC) | Outward-facing, rate-capped (one role, ≤2 drafts). Frequent runs would flood Drafts — a regression on invariant 1's spirit. |

**Decision: split the cloud routine into a frequent pure-secretary pass and a slow drafting pass** (or move drafting to the PC entirely, per the two-orchestrator split). The frequent pass does sweep + reconcile + mark + send-detect + rejection-archive, and **no drafting**. Once drafting leaves the cloud routine there is no over-staging risk, so the secretary is free to run hourly.

**Latency budget:** `applied` should be reflected in `Pipeline.md` within **one secretary interval** of the ack arriving (≤1h target). End-to-end (ack → outreach drafted) is bounded by secretary interval + PC poll interval (~≤2h with both hourly).

**No-op guard (mandatory):** the secretary keeps the routine's existing "if nothing changed, don't commit/push" rule, so hourly no-op runs stay silent and don't churn `main`.

## Reconciliation rules (keeping the two channels honest)

- **Direct mark with no ack ever** → fine; many ATSes send no ack. State stays `applied`. No nagging.
- **Ack with no role** → never auto-create; flag for intake (above).
- **Ack contradicts a downgrade** → never downgrade a row that's already past `applied` (interview/offer) just because an old ack is re-swept. State is monotonic forward through the funnel until a rejection/closed event.
- **Rejection event** (employer "we won't be moving forward") → existing flow: move Active→Closed, `git mv` folder to `_Archived/`, dated audit note. A rejection supersedes `applied`.

## Fail-loud: the one silent path, made visible (invariant 4)

The remaining silent-failure path is **prepped-but-never-applied**: Kanu applied (or meant to), no ack arrived, and he forgot the direct mark — so Skill 2 never fires and the warm outreach (the highest-value output) is silently dropped on a role he cared about.

**Requirement:** the secretary (or the daily report) emits a **visible nudge** for any role that is `prepped` (resume `.md` in folder) but **not** `applied`, after a staleness threshold (default **3 days** since prep):

> _"<Company> — <Role>: resume built <N> days ago, no `Applied` mark and no ack seen. Did you apply? Mark the row to auto-stage outreach."_

This converts the only remaining silent gap into the same shape as the rest of the system: the machine reminds, Kanu decides. The threshold and channel (audit note line vs. a dedicated nudge block) are tunable; the requirement that the gap be **loud, not silent,** is not.

## State table (read from files that already exist — invariant 5)

| State | How it's read | Set by |
|---|---|---|
| `prepped` | role folder has a tailored resume `.md` | Skill 1 |
| `applied` | Pipeline row token `Applied` | Kanu (direct) **or** secretary (from ack) |
| `staged` | `STAGED in Gmail <date>` in folder + Pipeline row | Skill 2 |
| `closed` | row in Closed section + folder under `_Archived/` | secretary (from rejection) |

No `role_state.json`. The detector reads and writes only `Pipeline.md`, the role folder, and Gmail — nothing new persists.

## What this detector does NOT do

- Does **not** draft or send anything (detection + reconciliation only).
- Does **not** do LinkedIn research (that's Skill 2, PC-only).
- Does **not** create roles from acks (flags for intake instead).
- Does **not** decide `applied` from a job-board "application sent" alert — only from an employer/ATS ack or Kanu's direct mark.

## Build delta (on top of the two-orchestrator build list)

1. **Secretary cadence split** — separate the cloud routine's sweep/reconcile/mark (frequent) from its drafting (slow or retired). Keep the no-op guard.
2. **Ack ruleset** — encode the ack include/exclude patterns + "no role → flag, don't create" in the secretary prompt.
3. **Fail-loud nudge** — add the prepped-but-not-applied staleness check to the secretary/report.
4. **Monotonic-state guard** — never downgrade a row past `applied` from a re-swept old ack.
