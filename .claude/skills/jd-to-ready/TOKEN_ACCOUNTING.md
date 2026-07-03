# jd-to-ready Token Accounting

This document defines the token accounting contract for `jd-to-ready` traces.
The scope is per-step accounting, not literal token-by-token stream capture.

## Scope

Track token usage for each required step of the run's run-type.

`jd-to-ready` (prep half):

- `1` intake
- `2` classification
- `3` resume tailoring
- `3.5` resume export + vision verification
- `3.7` apply packet (posting-date research + application answers + upload)
- `6` report-back
- `7` final logging

`stage-outreach` (apply half) owns steps `4` contact research, `4b` contact
enrichment, `4c` email verification, and `5` outreach drafting, plus its own
`6`/`7`.

If a step delegates to a subagent or primitive, the tokens caused by that
delegation belong to the parent step.

## Standard Shape

Every `step_end` event should include this field:

```json
"tokens": {
  "input": 0,
  "output": 0,
  "cache_read": 0,
  "cache_write": 0,
  "total": 0,
  "source": "runtime",
  "notes": null
}
```

Allowed `source` values:

- `runtime` - reported directly by the model/runtime
- `manual` - entered by the orchestrator from a visible usage report
- `estimated` - derived from a documented estimator
- `null` - unavailable

When counts are unavailable, use:

```json
"tokens": {
  "input": null,
  "output": null,
  "cache_read": null,
  "cache_write": null,
  "total": null,
  "source": null,
  "notes": "runtime did not expose token counts"
}
```

Do not omit `tokens` from `step_end`.

## Field Rules

- `input`, `output`, `cache_read`, `cache_write`, and `total` are non-negative
  integers or `null`.
- If all numeric fields are known, `total` must equal their sum.
- If only `total` is known, keep component fields `null` and explain in
  `notes`.
- `notes` is `null` or a short string. Do not paste prompts, JDs, emails, or
  private content.
- Token counts are diagnostics. They do not determine whether the produced role
  artifacts are correct.

## Attribution Rules

- Step 2 owns classification tokens, including subagent classification calls.
- Step 3 owns resume-tailoring tokens.
- Step 3.5 owns vision-verify subagent tokens. Local PDF rendering
  (`build_resume_pdf.py`, reportlab) uses no model tokens.
- Step 3.7 owns posting-date research (WebFetch reasoning) and
  `Application Answers.md` drafting tokens. The rclone upload uses none.
- Steps 4/4b/4c/5 are `stage-outreach` steps: 4 owns LinkedIn contact research
  reasoning, 4b owns recruiter-activity enrichment, 4c owns email
  verification, 5 owns outreach drafting.
- Step 6 owns the final user-facing report tokens.
- Step 7 should usually have low or unknown token usage; it exists to close the
  audit trail.

## Tool Events

`tool_event` and `subagent_event` may later include optional token hints, but
they are not required for the v1 contract. The stable reporting surface is the
`tokens` object on `step_end`.

## Validation

`trace_step.py` rejects:

- missing `tokens` on `step_end`
- malformed token JSON
- negative token counts
- `total` values that contradict known components
- unrecognized `source` values

If token data cannot be obtained from the runtime, the correct behavior is an
explicit unknown token object, not a fabricated estimate.
