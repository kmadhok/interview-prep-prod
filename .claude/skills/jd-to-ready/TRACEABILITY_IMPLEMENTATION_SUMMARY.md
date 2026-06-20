# jd-to-ready Traceability Implementation Summary

Historical note: this file describes the first traceability implementation pass.
The active contract for future coding agents now lives in:

- `TRACEABILITY.md`
- `TRACE_SCHEMA.md`
- `TOKEN_ACCOUNTING.md`
- `RUNBOOK.md`
- `TRACE_TEST_PLAN.md`

## What Changed

Implemented a traceability harness for the `jd-to-ready` skill so every apply-ready run can be inspected step-by-step instead of only summarized at the end.

## Files Edited

| File | Purpose of edit | What it accomplishes |
|---|---|---|
| `scripts/trace_step.py` | Added deterministic trace helper for `jd-to-ready` runs. | Creates a `run_id`, writes append-only per-step events, records tool/subagent events, checks whether required steps are closed, appends the global summary, and clears active-run state. |
| `hooks/jd-to-ready-post-tool.py` | Added PostToolUse telemetry hook. | During an active `jd-to-ready` run, appends compact tool-use events to the trace so file edits, shell commands, reads/searches, and MCP calls can be correlated to the run. |
| `hooks/jd-to-ready-subagent-stop.py` | Added SubagentStop telemetry hook. | Records subagent completion against the active run, which is especially useful for the JD-classification subagent in Step 2. |
| `hooks/jd-to-ready-stop.py` | Added Stop validation hook. | Prevents silent final completion when an active `jd-to-ready` run has unclosed required steps. |
| `/Users/kanumadhok/.claude/settings.json` | Registered the new hooks globally. | Enables tool telemetry, subagent telemetry, and final trace-completeness checks whenever a `jd-to-ready` run is active. The hooks no-op when no active run exists. |
| `SKILL.md` | Added mandatory trace contract and replaced the old manual final-log instructions. | Future `jd-to-ready` runs now explicitly call `trace_step.py start-run`, `set-role-folder`, `begin`, `end`, and `finish-run` around the orchestrated workflow. |

## Trace Artifacts

Each run now has two trace surfaces:

- `<role folder>/.jd-to-ready-trace.jsonl` — full append-only event log for the specific role.
- `~/.claude/logs/jd-to-ready.jsonl` — compact global summary line per completed run.

The helper also uses:

- `~/.claude/logs/jd-to-ready-active.json` — active-run state used by hooks. This is cleared by `finish-run`.

## How It Tracks Actions

The orchestrator records explicit step contracts:

1. `step_begin` records the primitive, mode, input summary, and a checkable prediction before work starts.
2. `step_end` records status, whether the prediction held, produced artifacts, gaps, failure pattern, and token count if available.
3. `tool_event` records compact telemetry for tool calls during the active run.
4. `subagent_event` records subagent completion during the active run.
5. `run_finish` closes the trace and writes the global summary.

This makes it possible to answer:

- Which step produced a bad artifact?
- Which prediction failed?
- Which primitive generated the gap?
- Which tools or MCP calls were used during the run?
- Was the run stopped before all required steps closed?

## Why This Helps

The implementation applies the observability and decision-trace concepts from the agent harness papers:

- Component boundaries stay clear: `jd-to-ready` remains an orchestrator and each primitive still owns its domain logic.
- Experience becomes inspectable: per-role JSONL traces preserve the execution path and compact tool telemetry.
- Decisions become falsifiable: each step records a prediction before execution and whether it held afterward.
- Maintainability improves: failures can be diagnosed from the trace before rerunning the whole pipeline.

## Operational Notes

- Hooks are defensive telemetry, not the primary source of truth. The orchestrator must still emit explicit `begin` and `end` events.
- If a run is interrupted, close or mark missing steps before final stop, or the Stop hook will report the incomplete trace.
- Do not log full JD text or private message bodies in trace events. Use summaries and file paths.
