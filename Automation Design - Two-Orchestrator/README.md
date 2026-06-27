# Automation Design — Two-Orchestrator

Design docs for splitting the monolithic `jd-to-ready` automation into two apply-gated skills (prep on save · outreach on apply), keeping all LinkedIn-bound work on the apply side and the cloud routine as a pure Gmail secretary. **Status: design agreed, not yet built.**

These are kept separate from the older `Automation Architecture - *` docs at the repo root (Drip Runner, Runtime, Saved Jobs Ingestion, Skill Sync, Complete Reference), which describe the system as it runs today.

## Read in this order

1. **`Automation Architecture - Purpose.md`** — the *why*: the goal, the design invariants, and how to judge any change. Start here.
2. **`Automation Architecture - Two-Orchestrator Split.md`** — the decision + topology + build list + risks.
3. **`Automation Architecture - Diagrams.md`** — Mermaid diagrams (current routine, current monolith, both new skills, target).
4. **`Spec - Orchestrator 1 (jd-to-ready prep).md`** — save-side skill (intake → resume → PDF, stops at the apply gate).
5. **`Spec - Orchestrator 2 (stage-outreach).md`** — apply-side skill (find recruiter → verify email → Gmail draft).
6. **`Spec - Applied Detector.md`** — the load-bearing seam: how `applied` is detected (Kanu's mark + Gmail ack), the secretary cadence, and the fail-loud nudge.
