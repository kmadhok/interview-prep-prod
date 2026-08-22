# Manual mode

Schedulers are optional. You can run the complete job-search loop by hand from a
Claude Code session opened at the repository root.

## 1. Save and prepare a role

Paste the job description or posting URL into Claude Code and invoke:

```text
/jd-to-ready
```

Ask it to prepare that job description. The skill files the JD, classifies the role,
tailors the resume, exports the PDF when reportlab is available, and builds the apply
packet. It stops at the human apply gate. Review the artifacts under
`workspace/Roles/<Company - Role>/` and apply through the employer's ATS yourself.

## 2. Record the application

After the ATS confirms submission, move or update the role's row under `## Active`
in `workspace/Pipeline.md` so its stage contains `Applied`. Do not add a `STAGED`
marker. That marker is owned by the outreach skill.

## 3. Stage outreach

In Claude Code, identify the applied role and invoke:

```text
/stage-outreach
```

The skill verifies the apply gate, performs LinkedIn contact research sequentially,
verifies or flags email addresses, writes `Cold Outreach.md`, and creates Gmail
drafts. It never sends them. Review the drafts, attach the resume, choose at most one
cold recipient at a company unless you deliberately space messages out, and click
Send yourself.

Email verification is optional; see [email verification](email-verification.md) for
key setup and fallback behavior.

## 4. Follow the trace when output is wrong

Each orchestrator writes `runs/<run-id>/trace.jsonl` and a rendered `report.md`.
Start with the output you dislike, find the producing step in the report, then follow
its `sources` to the skill prompt or canonical workspace master. Edit the source of
truth and rerun the affected skill.

The repository ships `.claude/settings.json` containing only the jd-to-ready trace
hooks: PostToolUse, SubagentStop, and Stop, registered with
`$CLAUDE_PROJECT_DIR`-relative commands. They no-op unless a jd-to-ready run is active;
during a run they enrich `runs/<run-id>/trace.jsonl` with tool telemetry and block a
silent finish when required steps remain unclosed. Claude Code asks you to approve
project hooks on first use. If you previously registered the same hooks in global
`~/.claude/settings.json`, remove those global entries to avoid duplicate telemetry.

## Optional helpers

- Rebuild the behavior fixture:
  `python3 scripts/build_fixture_workspace.py /tmp/interview-prep-fixture --force`
- Run all local behavior contracts:
  `python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture`
- Recheck onboarding and the live LinkedIn endpoint:
  `python3 scripts/verify_setup.py`

Automation options are documented under `infra/`; every scheduled pass has this
manual loop as its equivalent.
