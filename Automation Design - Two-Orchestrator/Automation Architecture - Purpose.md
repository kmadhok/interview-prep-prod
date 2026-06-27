# Automation Architecture — Purpose

_The "why" behind the drip-runner / two-orchestrator system. Read this before the topology docs (`Automation Architecture - Two-Orchestrator Split.md`, `… - Diagrams.md`, the two `Spec - Orchestrator …` files) — they describe **how** it's wired; this describes **what it's for** and **what "good" means**, so design changes can be judged against the goal instead of against each other._

## The one-sentence purpose

**Compress Kanu's time-to-applied and time-to-outreach to near zero — so that the only friction left in the job search is the two moments that genuinely require a human (clicking _apply_, and hitting _send_ on a recruiter email) — without babysitting the machine and without burning the LinkedIn account.**

Everything else — filing the JD, tailoring the resume, building the PDF, scraping the recruiter, verifying their email, drafting the outreach — is staged and waiting by the time Kanu looks at it.

## What this system actually is

A **personal job-search conveyor belt**. The top of the funnel is high-volume and low-effort (save lots of jobs on LinkedIn). The bottom is a small number of high-quality, ready-to-fire applications + warm recruiter outreach. The machine's job is to turn the first into the second in the background, across the whole pipeline, while Kanu stays the only sender and the only decision-maker.

It is **not** an autonomous agent that runs the job search. It is leverage: it does the grunt work so Kanu's scarce attention only lands where it has to.

## The design invariants (do not regress these)

These follow from the purpose. Any redesign that breaks one is wrong even if it's simpler or faster.

1. **Human-gated output — never sends.** Drafts only (Gmail drafts + paste-ready LinkedIn text). Every outward action keeps a human gate. The system maximizes Kanu's leverage; it does not act on his behalf. _This is why the machine is allowed to be aggressive everywhere upstream — the send is always the brake._

2. **Protect the LinkedIn channel.** LinkedIn scraping is the scarce, fragile, account-risking resource — rate-limited and flaggable. The system is shaped _around_ rationing it: do the expensive LinkedIn work **only for jobs Kanu actually applies to**, never for the larger pile of saved-but-never-pursued jobs. The binding constraint isn't compute or time; it's this channel.

3. **No babysitting.** It runs on a schedule on an always-on PC + a cloud routine. The two human actions (apply, send) are the _only_ required inputs. Anything that quietly demands Kanu's attention to keep working is a defect, not a feature.

4. **Fail loud, never fail silent.** The worst failure mode for a background system is dropping the highest-value output (warm outreach on a role Kanu cared about) with no error. Silent gaps must be surfaced as a visible nudge in the report, not discovered weeks later.

5. **Truth comes from files that already exist.** State is read from artifacts on disk (resume `.md` = prepped, Pipeline row `Applied`, `STAGED in Gmail` marker = staged) and from Gmail reality — not from a parallel state database that can drift from the truth.

## How "applied" is known — and why it can be near-real-time

The pivot of the whole machine is the **`applied` state**: it gates the expensive, high-value apply-side work (find recruiter → verify email → draft outreach). Getting it right, and getting it _promptly_, is what makes the conveyor belt feel instant instead of laggy.

`applied` has two independent sources of truth, so it does not depend on Kanu's memory:

- **Kanu marks the Pipeline row `Applied`** (the direct signal), and
- **The cloud routine's Gmail sweep marks it from application-acknowledgment mail** (the independent backstop — Gmail is the source of truth, the routine reconciles Pipeline against it).

### The secretary should run often; the drafter should not

The cloud routine today bundles two jobs with very different ideal cadences into one twice-daily run:

| Sub-job | Latency-sensitive? | Ideal cadence | Why |
|---|---|---|---|
| **Gmail sweep → reconcile Pipeline → mark `Applied`** (secretary) | **Yes** | hourly / 30-min | Cheap Gmail reads. It's the trigger for the entire apply-side machine; running it often makes "applied" detection near-real-time. |
| **Stage outreach drafts** (drafter) | No | 2×/day (or move to PC) | Outward-facing, deliberately rate-capped (one role, ≤2 drafts/run). Running it often would flood Drafts. |

**The fix is to decouple them, not to run the whole routine more often.** A frequent (hourly/30-min) **pure-secretary** pass — sweep Gmail, reconcile `Pipeline.md`, mark `Applied`, detect sent drafts, archive rejections, _no drafting_ — makes the `applied` signal nearly live, which lets the PC's hourly outreach poll fire promptly. Keep drafting on its slow, deliberate cadence (or on the PC entirely, per the two-orchestrator split).

This is the **same direction as the orchestrator split**: that design already strips drafting out of the cloud routine and turns it into a pure secretary. A pure secretary has no over-staging risk left, so it _should_ run hourly. "Run the secretary more often" and "split the orchestrators" are one move.

**One guard to keep:** the routine's "if nothing changed, don't commit/push" rule must stay, so frequent no-op runs stay silent and don't churn `main`.

## How to judge a design change

Score any proposed change against the purpose, in this order:

1. Does it keep every outward action human-gated? (invariant 1)
2. Does it spend _less_ LinkedIn budget on jobs Kanu won't apply to? (invariant 2)
3. Does it reduce — never add — required human attention? (invariant 3)
4. Does it make failures _louder_? (invariant 4)
5. Only then: is it simpler? (KISS — but never at the cost of 1–4)

A change that wins on simplicity but loses on 1–4 is a regression. The two-orchestrator split is justified precisely because it wins on 2 and 4 (LinkedIn work deferred to apply-time; trace can't silently straddle the apply gate) while staying flat on 1 and 3.

## Open tension worth naming

The purpose says "no babysitting," yet the apply-side still depends on the `Applied` mark existing. The Gmail backstop covers most of that gap, but application acks are noisy and sometimes absent. The honest mitigations — both consistent with the purpose — are: (a) make marking `Applied` near-zero-effort so it's rarely forgotten, and (b) add the **fail-loud nudge**: a daily report line _"prepped N days ago, resume built, no `Applied` mark — did you apply?"_ That converts the one remaining silent-failure path into a visible reminder, which is the shape the rest of the system already takes.
