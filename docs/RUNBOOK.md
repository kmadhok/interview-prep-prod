# Operations runbook

## Scope and safe posture

Human-gated job-search workspace. Validate against a generated fixture; never use the live `workspace/` for a smoke test.

## Safe setup / verification

```bash
python3 scripts/build_fixture_workspace.py /tmp/interview-prep-fixture --force
python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture
python3 scripts/test_no_personal_refs.py
```

Always inspect `git status --short` before and after. Stop on authentication, checkpoint/challenge, rate limit, unexpected writes, or malformed queue/state. Preserve logs and exact exit status; do not reset, clean, stash, or retry a live action as “verification.”

## External credentials and permissions

| Credential / permission | Exact consumer | Missing behavior / safe default |
|---|---|---|
| LinkedIn session | the registered `linkedin` MCP server (stdio by default; HTTP daemon at `127.0.0.1:8765/mcp` for runners) | Live contact/search steps block; fixture evals do not need it. |
| Gmail OAuth | external Gmail/Claude integration | Draft/search operations block; never store tokens here. |
| `BQ_PROXY_TOKEN` | `scripts/drip_runner/apply_digest.py` | Optional dashboard proxy call fails; local file processing remains available. |
| `CUBEJS_API_SECRET` | `scripts/drip_runner/apply_digest.py` | Same optional proxy path. |
| `APPLY_PACKET_REMOTE_DIR` | `scripts/drip_runner/apply_packet.py` | Remote packet copy is unavailable; keep output local. |
| `CLAUDE_CODE_SESSION_ID` | hooks under `.claude/skills/jd-to-ready/hooks/` | Trace attribution lacks harness session id; hooks use their fallback. |

## Environment variables read by first-party runtime code

| Variable | Read at | Missing behavior / safe default |
|---|---|---|
| `APPLY_PACKET_REMOTE_DIR` | `scripts/drip_runner/apply_packet.py:34` | Optional override; the source-defined default applies. |
| `CLAUDE_CODE_SESSION_ID` | `scripts/trace_step.py:102` | Optional override; the source-defined default applies. |
| `CLAUDE_SUBAGENT_NAME` | `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py:46` | Optional override; the source-defined default applies. |
| `CLAUDE_TOOL_INPUT` | `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py:67` | Optional override; the source-defined default applies. |
| `CLAUDE_TOOL_NAME` | `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py:64` | Optional override; the source-defined default applies. |
| `E` | `.claude/skills/verify-emails/scripts/verify_emails.py:240` | Optional override; the source-defined default applies. |
| `SUBAGENT_NAME` | `.claude/skills/jd-to-ready/hooks/jd-to-ready-subagent-stop.py:47` | Optional override; the source-defined default applies. |
| `TOOL_NAME` | `.claude/skills/jd-to-ready/hooks/jd-to-ready-post-tool.py:63` | Optional override; the source-defined default applies. |
| `TRACE_RUNS_DIR` | `scripts/trace_step.py:68` | Optional override; the source-defined default applies. |

## Command-line flags

| Command source | Flag | Defined/read at | Safe behavior |
|---|---|---|---|
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--blocked-apply` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:414` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--clone` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:404` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--company` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:405` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--draft-json` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:409` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--expected-lead-recipient` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:412` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--expected-recipient` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:410` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--pages` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:407` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--title-leak` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:408` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--trace-runs-dir` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:416` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | `--worklist-out` | `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py:406` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--dry-run` | `.claude/skills/verify-emails/scripts/verify_emails.py:669` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--emails-md` | `.claude/skills/verify-emails/scripts/verify_emails.py:684` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--emails-md-default` | `.claude/skills/verify-emails/scripts/verify_emails.py:688` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--json` | `.claude/skills/verify-emails/scripts/verify_emails.py:674` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--ledger` | `.claude/skills/verify-emails/scripts/verify_emails.py:652` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--max-credits` | `.claude/skills/verify-emails/scripts/verify_emails.py:657` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--no-write` | `.claude/skills/verify-emails/scripts/verify_emails.py:679` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-emails/scripts/verify_emails.py` | `--top` | `.claude/skills/verify-emails/scripts/verify_emails.py:663` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `.claude/skills/verify-postings/scripts/verify_postings.py` | `--json` | `.claude/skills/verify-postings/scripts/verify_postings.py:449` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--all` | `evals/run_eval.py:48` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--json` | `evals/run_eval.py:44` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--list` | `evals/run_eval.py:46` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--live` | `evals/run_eval.py:42` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--profile` | `evals/run_eval.py:40` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--role` | `evals/run_eval.py:38` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/run_eval.py` | `--workspace` | `evals/run_eval.py:36` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/verify_behavior_traces.py` | `--json` | `evals/verify_behavior_traces.py:177` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `evals/verify_behavior_traces.py` | `--runs-dir` | `evals/verify_behavior_traces.py:176` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/build_fixture_workspace.py` | `--force` | `scripts/build_fixture_workspace.py:170` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/build_resume_pdf.py` | `--all` | `scripts/build_resume_pdf.py:559` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/build_resume_pdf.py` | `--out` | `scripts/build_resume_pdf.py:560` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/apply_digest.py` | `--repo-root` | `scripts/drip_runner/apply_digest.py:67` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/apply_digest.py` | `--send` | `scripts/drip_runner/apply_digest.py:68` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/apply_packet.py` | `--commit` | `scripts/drip_runner/apply_packet.py:319` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/apply_packet.py` | `--remote-dir` | `scripts/drip_runner/apply_packet.py:313` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/apply_packet.py` | `--repo-root` | `scripts/drip_runner/apply_packet.py:316` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/dedupe.py` | `--company` | `scripts/drip_runner/dedupe.py:36` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/dedupe.py` | `--job-id` | `scripts/drip_runner/dedupe.py:37` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/dedupe.py` | `--pipeline` | `scripts/drip_runner/dedupe.py:38` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/job_parser.py` | `--body` | `scripts/drip_runner/job_parser.py:48` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/job_parser.py` | `--subject` | `scripts/drip_runner/job_parser.py:47` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/outreach_worklist.py` | `--pipeline` | `scripts/drip_runner/outreach_worklist.py:79` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/prepped_not_applied.py` | `--pipeline` | `scripts/drip_runner/prepped_not_applied.py:115` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/prepped_not_applied.py` | `--roles-dir` | `scripts/drip_runner/prepped_not_applied.py:114` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/prepped_not_applied.py` | `--threshold-days` | `scripts/drip_runner/prepped_not_applied.py:116` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/saved_jobs_ledger.py` | `--job-id` | `scripts/drip_runner/saved_jobs_ledger.py:70` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/saved_jobs_ledger.py` | `--ledger` | `scripts/drip_runner/saved_jobs_ledger.py:71` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/saved_jobs_ledger.py` | `--note` | `scripts/drip_runner/saved_jobs_ledger.py:76` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/saved_jobs_ledger.py` | `--status` | `scripts/drip_runner/saved_jobs_ledger.py:75` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/saved_jobs_ledger.py` | `--ts` | `scripts/drip_runner/saved_jobs_ledger.py:77` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/watchdog.py` | `--check` | `scripts/drip_runner/watchdog.py:223` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/watchdog.py` | `--heartbeat` | `scripts/drip_runner/watchdog.py:222` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/watchdog.py` | `--last-alert` | `scripts/drip_runner/watchdog.py:227` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/drip_runner/watchdog.py` | `--now` | `scripts/drip_runner/watchdog.py:226` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/export_template.py` | `--force` | `scripts/export_template.py:145` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/onboard_workspace.py` | `--answers` | `scripts/onboard_workspace.py:148` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/onboard_workspace.py` | `--refresh` | `scripts/onboard_workspace.py:149` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/onboard_workspace.py` | `--repo-root` | `scripts/onboard_workspace.py:147` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--company` | `scripts/pipeline_row.py:344` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--contacts` | `scripts/pipeline_row.py:349` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--date` | `scripts/pipeline_row.py:347` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--folder` | `scripts/pipeline_row.py:346` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--next-action` | `scripts/pipeline_row.py:348` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--pipeline` | `scripts/pipeline_row.py:340` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--role` | `scripts/pipeline_row.py:345` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/pipeline_row.py` | `--via` | `scripts/pipeline_row.py:356` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/role_folder.py` | `--company` | `scripts/role_folder.py:80` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/role_folder.py` | `--role` | `scripts/role_folder.py:81` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/role_folder.py` | `--workspace` | `scripts/role_folder.py:84` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--agent-name` | `scripts/trace_step.py:772` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--clause-results` | `scripts/trace_step.py:761` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--company` | `scripts/trace_step.py:722` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--contract-clauses` | `scripts/trace_step.py:747` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--failure-pattern` | `scripts/trace_step.py:759` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--files-written` | `scripts/trace_step.py:784` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--gaps` | `scripts/trace_step.py:758` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--inputs-summary` | `scripts/trace_step.py:746` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--mode` | `scripts/trace_step.py:742` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--prediction` | `scripts/trace_step.py:743` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--prediction-met` | `scripts/trace_step.py:756` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--primitive` | `scripts/trace_step.py:741` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--produced` | `scripts/trace_step.py:757` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--reason` | `scripts/trace_step.py:744` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--role` | `scripts/trace_step.py:723` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--role-folder` | `scripts/trace_step.py:724` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--run-id` | `scripts/trace_step.py:721` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--run-type` | `scripts/trace_step.py:729` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--skill` | `scripts/trace_step.py:726` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--sources` | `scripts/trace_step.py:745` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--status` | `scripts/trace_step.py:755` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--step` | `scripts/trace_step.py:740` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--strict` | `scripts/trace_step.py:778` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--summary` | `scripts/trace_step.py:768` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--test-run` | `scripts/trace_step.py:725` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--tokens` | `scripts/trace_step.py:760` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/trace_step.py` | `--tool-name` | `scripts/trace_step.py:766` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/verify_resume.py` | `--out-dir` | `scripts/verify_resume.py:227` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/verify_resume.py` | `--reference` | `scripts/verify_resume.py:231` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/verify_setup.py` | `--repo-root` | `scripts/verify_setup.py:166` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |
| `scripts/verify_setup.py` | `--skip-live` | `scripts/verify_setup.py:169` | Read its help before use; flags named `--dry-run`, `--check`, `--status`, or `--help` are the safe inspection modes. |

## Configuration fields

| Field | Current template/default | Defined at | Missing/invalid behavior |
|---|---|---|---|
| `user_name` | `(blank)` | `templates/profile.yaml:3` | Consumer raises/fails when required; otherwise this default is used. |
| `user_email` | `(blank)` | `templates/profile.yaml:4` | Consumer raises/fails when required; otherwise this default is used. |
| `user_linkedin` | `(blank)` | `templates/profile.yaml:5` | Consumer raises/fails when required; otherwise this default is used. |
| `user_github` | `(blank)` | `templates/profile.yaml:6` | Consumer raises/fails when required; otherwise this default is used. |
| `resume_filename_pattern` | `"{name} Resume - {company} {role}"` | `templates/profile.yaml:7` | Consumer raises/fails when required; otherwise this default is used. |
| `timezone` | `(blank)` | `templates/profile.yaml:8` | Consumer raises/fails when required; otherwise this default is used. |

## Scheduled and long-lived jobs

- **Pass A / saved-jobs drip:** task definitions under `infra/` invoke preparation and stop at the apply gate.
- **Pass B / outreach:** polls only rows already marked `Applied`; only `stage-outreach` may append the Gmail staged marker.
- **LinkedIn MCP:** the registered `linkedin` MCP server (stdio by default; HTTP daemon at `127.0.0.1:8765/mcp` for runners); sequential calls only. Manual mode is the default.

## Recovery

Remove only artifacts produced by the command you just ran and only after checking status. Never delete user workspaces, queues, browser profiles, cookies/sessions, credentials, `data/`, or `state/` as a recovery shortcut.
