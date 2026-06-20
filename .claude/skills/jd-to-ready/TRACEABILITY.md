# jd-to-ready Traceability

This is the canonical overview for how `jd-to-ready` runs should be traced.
It exists so a coding agent can inspect the current system, understand the
target contract, and implement deterministic logging without rediscovering the
McKinsey failure mode.

## Why This Exists

`jd-to-ready` is an orchestrator. It calls intake, classification, resume
tailoring, contact research, contact enrichment, outreach drafting, report-back,
and final logging. The trace must make those handoffs inspectable after the
fact.

A healthy trace answers:

- Which step was running?
- What did that step predict before it ran?
- What did it produce?
- Which gaps or failure patterns were recorded?
- How many tokens were used by that step, if the runtime exposed counts?
- Did the run close normally, fail, or abort intentionally?

The trace is not a substitute for the role artifacts. It is the audit trail for
why those artifacts were produced.

## Current Trace Surfaces

- Per-role event log: `<role folder>/.jd-to-ready-trace.jsonl`
- Global summary log: `~/.claude/logs/jd-to-ready.jsonl`
- Active run state: `~/.claude/logs/jd-to-ready-active.json`
- Fallback trace before a role folder is bound:
  `~/.claude/logs/jd-to-ready-runs/<run_id>.jsonl`

Do not log full JD text, private email bodies, or full outreach bodies in trace
events. Log paths, short summaries, counts, and structured gaps.

## Required Lifecycle

Every production run follows this lifecycle:

1. `start-run`
2. `set-role-folder`
3. `begin` and `end` every required step
4. `finish-run`

Required steps:

| Step | Primitive | Required close event |
|---|---|---|
| `1` | `interview-prep-intake` | `step_end` |
| `2` | `jd-classification` | `step_end` |
| `3` | `tailor-resume` | `step_end` |
| `4` | `find-contacts` | `step_end` |
| `4b` | `enrich-contacts` | `step_end` |
| `5` | `write-outreach` | `step_end` |
| `6` | `report-back` | `step_end` |
| `7` | `final-log` | `step_end` |

Hooks may append telemetry and warn about incomplete traces. Hooks must not be
the source of truth for finalization.

## Deterministic Contract

The helper is fail-closed for production runs. `trace_step.py` enforces these
rules:

- One active run at a time.
- One active step at a time.
- `begin` fails if another step is already open.
- `end` fails if the requested step is not the open step.
- `finish-run` computes final status from the event log instead of trusting a
  caller-provided status.
- `finish-run` refuses incomplete production traces.
- Incomplete runs close only through an explicit abort command that records the
  reason, open step, and missing steps.
- Every event has a monotonic `seq` number within the run.
- Active role folders for live roles resolve under the workspace `Roles/`
  directory.
- Invalid JSON fields, invalid enums, and invalid failure patterns fail loudly.

The trace helper is strict because a missing event is a system problem, not an
acceptable summary style.

## Token Trace Scope

Token tracing is per step. This project is not trying to capture the literal
generated token stream.

Each `step_end` should include a `tokens` object. If counts are unavailable, use
the explicit unknown shape from `TOKEN_ACCOUNTING.md` instead of omitting the
field.

Token totals should be attributed to the step that caused the model work. Tool
events and subagent events can carry optional token hints later, but the stable
contract is step-level token accounting.

## McKinsey Anti-Example

The McKinsey run `jdtr-20260607140047-54dd1654` produced useful artifacts, but
the trace was not trustworthy enough:

- The per-role trace closed only steps `1`, `2`, and `3`.
- A `run_finish` event marked the run `partial` while contact research was still
  effectively in progress.
- A later corrected summary said the run completed through step `6`.
- Steps `4`, `4b`, `5`, and `6` never received proper `step_end` events.
- Trace metadata pointed at a non-`Roles/` path while the real folder lived
  under `Roles/`.

The fix is not another corrected summary. The implemented state enforcement now
makes this sequence fail in production.

## Related Docs

- `TRACE_SCHEMA.md` - event shapes and validation rules
- `TOKEN_ACCOUNTING.md` - per-step token accounting contract
- `RUNBOOK.md` - operator commands and recovery guidance
- `TRACE_TEST_PLAN.md` - regression scenarios for hardening the trace helper
- `TRACEABILITY_IMPLEMENTATION_SUMMARY.md` - historical context for the first
  traceability pass
