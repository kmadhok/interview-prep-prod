# Spec: Productionalization v1 (`productionalized_version` branch)

Upstream intent: [docs/intent/productionalization.md](../intent/productionalization.md)
Status: APPROVED — all 7 decisions resolved 2026-07-06; ready for Plan phase
Date: 2026-07-06

## Objective

Rebuild the interview-prep system so a friend can clone it, self-onboard through a
conversational interview, run `jd-to-ready` on a real JD, and debug any output they
dislike by following the trace: output → skill → prompt → source markdown file →
edit it themselves. No Kanu required.

**End goal beneath the workstreams:** every skill has *defined behavior* — an explicit
contract of what artifacts/state a run must produce — verified by deterministic
evaluators. Defined behavior + deterministic evaluation is what makes loop engineering
possible: change a prompt or tool, re-run the eval, see if behavior improved.

Five workstreams:

1. **Trace / work-log contract** — every orchestrator and primitive skill run emits a
   structured log tying each action to a reason and the prompt/file that produced it.
   Extends the existing `jd-to-ready` trace pattern (`trace_step.py`,
   `TRACE_SCHEMA.md`, `.jd-to-ready-trace.jsonl`) into a system-wide standard.
2. **Behavioral evaluation harness** — generalize `two-orchestrator-e2e-test` +
   `verify_artifacts.py` into the system's testing philosophy: every skill declares a
   behavior contract; deterministic verifiers check end-state artifacts; evals run in
   isolated clones. Unit tests exist only for deterministic helpers.
3. **Deterministic tool layer** — for every step a skill currently "figures out" via
   LLM reasoning, ask: can this be a function the skill calls instead? Extract
   repeated probabilistic work into deterministic scripts (the `dedupe.py` /
   `job_parser.py` / `build_resume_pdf.py` pattern, applied systematically).
4. **Infrastructure manifest** — the three undeclared systems (Mac launchd
   `com.kanu.linkedin-mcp`, Claude cloud routine `Application Drip-Runner`, planned
   Windows PC runner) get declared in-repo with setup docs, and every scheduled
   behavior gets a documented manual-invocation equivalent.
5. **Conversational onboarding + template/instance split** — an interview-style
   skill builds a new user's canonical files and walks Gmail + LinkedIn MCP setup
   (LinkedIn is REQUIRED — see Decisions); personal data separated from shareable
   logic under `workspace/`; all hardcoded Kanu paths/names replaced by
   `profile.yaml`.

**Non-goals (v1):** token/internal-reasoning capture; non-Claude harnesses (portability
is architecture discipline only); public GitHub release (clean-history export, later
phase); any change to the live system on `main`.

## Design Principles

1. **Determinism-first.** Before any skill step is implemented as LLM reasoning,
   justify why it can't be a deterministic tool. LLM reasoning is reserved for
   genuinely probabilistic work (judgment, language, ranking); everything mechanical
   (parsing, dedupe, file placement, naming, state markers, verification) is a
   function the skill calls. Fewer decisions per run → more reproducible behavior →
   tighter eval loops.
2. **Defined behavior over defined implementation.** A skill is specified by the
   end-state it must produce (files, markers, state transitions), not by how it gets
   there. The behavior contract is what evals verify and what loop engineering
   iterates against.
3. **Trace is the repair manual.** Every action carries `reason` + `sources` so a
   user can walk from a bad output to the file to edit.
4. **No state database.** State is read from files that already exist (existing
   system invariant — preserved).
5. **Draft, never send.** Every outward action keeps a human gate (existing
   invariant — preserved).

## Decisions (resolved 2026-07-06)

| # | Question | Decision |
|---|----------|----------|
| 1 | Public-release path | Branch = dev ground. Public release is a later clean-history export to a fresh repo. No history rewrite of this repo. |
| 2 | LinkedIn MCP at onboarding | **Required.** Everyone fully sets up LinkedIn before using the system. Onboarding must therefore make this setup as guided and verifiable as possible (it is the friend test's riskiest step). |
| 3 | Cloud routine for friends | Documented-optional. Manual invocation is the default; a setup doc exists for those who want their own routine. |
| 4 | `follow-up` / `track-application` | Pull both into the repo; repo becomes self-contained. |
| 5 | Primitive-skill traces | Both: primitives write into the orchestrator's run dir when piped, and get their own run dir when standalone. Everything is always traced. |
| 6 | Eval fixtures vs. live | Fixtures + recorded MCP responses for the per-skill tier; live side effects only in the pipeline e2e tier. |
| 7 | Determinism audit scope | The 8 pipeline skills the friend test exercises (intake, classify, tailor-resume, PDF/apply-packet, find-contacts, enrich-contacts, verify-emails, write-outreach). |

## Tech Stack

- Skills: Claude Code SKILL.md format (markdown, in-repo at `.claude/skills/`)
- Scripts/tools: Python 3.11+ stdlib-first (reportlab for PDF is the existing exception)
- Trace: JSONL (machine) + rendered Markdown run report (human)
- Evals: isolated-clone runs + deterministic artifact verifiers (the
  `verify_artifacts.py` pattern), one behavior contract per skill
- Config: single `profile.yaml` per user instance
- No new runtime dependencies without Ask-First approval

## Commands

```
Run helper unit tests:   python3 -m pytest scripts/ -v
Run a skill eval:        python3 evals/run_eval.py <skill> [--fixture <name>]   (new)
Run full pipeline eval:  two-orchestrator-e2e-test skill (isolated clone)
Trace a step:            python3 scripts/trace_step.py <run-id> <event> [...]
Render run report:       python3 scripts/render_run_report.py <run-dir>        (new)
Verify onboarding:       python3 scripts/verify_setup.py                        (new)
Skill entry points:      /onboard, /jd-to-ready, /stage-outreach (via Claude Code)
```

## Project Structure (target)

```
.claude/skills/        → All skills (canonical source; incl. follow-up,
                          track-application pulled in from global)
scripts/               → Deterministic tool layer + drip_runner
evals/                 → Behavior contracts + verifiers per skill (NEW)
  <skill>/contract.md  →   what a run MUST produce (files, markers, transitions)
  <skill>/verify_*.py  →   deterministic checker (verify_artifacts.py pattern)
  fixtures/            →   fixture JDs, pipeline fixtures, clone scaffolding
infra/                 → Infrastructure manifest (NEW)
  launchd/             →   linkedin-mcp daemon plist template + setup doc
  cloud-routines/      →   Drip-runner routine: prompt, cron, setup + manual-run doc
  pc-runner/           →   Windows Task Scheduler defs (Pass A/B) + setup doc
runs/                  → Trace output, one dir per run (gitignored in template) (NEW)
templates/             → Blank canonical-file templates for new users (NEW)
workspace/             → ALL personal/instance data (gitignored in template) (NEW)
profile.yaml           → User config: name, workspace root, resume filename
                          pattern, timezone (NEW)
docs/intent|spec/      → Intent + this spec
docs/onboarding/       → Human-readable setup guide (mirrors /onboard skill)
```

Migration note: moving `Pipeline.md`, `Roles/` etc. into `workspace/` breaks every
path reference in skills/scripts — lands as one atomic change with all references
updated, this branch only.

## Evaluation Strategy (behavior, not units)

Premise: unit tests are pointless for agent behavior. What matters is whether a run
produces the *end behavior* we want. The system already proves the pattern —
`two-orchestrator-e2e-test` runs one real role through all 8 skills in an isolated
`_jd-to-ready-test/` clone and verifies artifacts deterministically with
`verify_artifacts.py`. v1 generalizes this:

1. **Behavior contract per skill** (`evals/<skill>/contract.md`): the observable
   end-state a successful run must produce. Example (tailor-resume): resume file
   exists at the canonical path; every bullet traces to `Resume Achievements
   Master.md` (canonical-only rule); `gaps[]` returned when a JD requirement has no
   canonical match; no content from `Resume Claims To Verify.md`.
2. **Deterministic verifier per contract** (`evals/<skill>/verify_*.py`): checks the
   end-state mechanically — file existence, schema validity, marker presence, content
   provenance greps, never-sent proofs. Verifiers are the *only* pass/fail authority;
   narrative judgment goes in the report, not the verdict.
3. **Isolation:** evals run in throwaway clones (the `_jd-to-ready-test/` pattern);
   real workspace state is never touched; the isolation audit (`git status` must show
   changes only under the clone) is itself a check.
4. **Tiers:** per-skill evals (one skill, fixture input) → pipeline eval (the
   existing e2e skill, all 8 skills, real LinkedIn/Gmail side effects gated to
   drafts + test Drive remote) → the friend test (human-level eval of onboarding).
5. **The loop-engineering loop:** change a prompt/tool → run the affected skill's
   eval → verifier says whether behavior held/improved → trace explains *why* it
   changed. Metrics tracked per eval run: verifier pass rate per contract clause,
   steps per run, deterministic-tool calls vs. LLM-reasoned actions (from the trace),
   token cost per run (existing `TOKEN_ACCOUNTING.md` pattern), wall-clock.

Unit tests remain only for the deterministic tool layer (existing `test_*.py`
pattern — dedupe, job_parser, verifiers themselves).

## Code Style

Follow existing repo conventions. Reference snippet (trace event, workstream 1):

```python
def trace(run_id: str, skill: str, step: str, action: str, *,
          reason: str, sources: list[str], outputs: list[str] | None = None) -> None:
    """Append one trace event. `sources` are the prompt/markdown files the action
    read — this is the debuggability chain, never omit it."""
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id, "skill": skill, "step": step,
        "action": action, "reason": reason,
        "sources": sources, "outputs": outputs or [],
    }
    with open(run_dir(run_id) / "trace.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")
```

Conventions: snake_case Python, kebab-case skill names, `pathlib` over string paths,
no hardcoded user paths (everything routes through `profile.yaml`), skills state
their sources (which files they read) and their behavior contract in a front-of-file
block.

## Boundaries

- **Always:** work only on `productionalized_version`; run the personal-data guard
  test before every commit; run the affected skill's eval after changing its prompt
  or tools; keep behavior contracts in sync with skill changes; update this spec when
  decisions change
- **Ask first:** adding runtime dependencies; changing the trace schema or eval
  contract format after they land; anything touching `main` or the live workspace at
  `~/Documents/Claude/Projects/Interview Prep/`; history rewrites; publishing anywhere
- **Never:** modify the live launchd job or cloud routine; commit secrets; personal
  data in template-side dirs; delete trace output; let a verifier's pass/fail
  authority be overridden by narrative judgment

## Success Criteria

1. Every `jd-to-ready` / `stage-outreach` run produces `runs/<run-id>/trace.jsonl` +
   `report.md`; every event carries `reason` and `sources`; a user can go from "I
   don't like this email draft" to the exact markdown file to edit.
2. Every pipeline skill has a behavior contract in `evals/` and a deterministic
   verifier; `run_eval.py <skill>` passes for all skills on fixture inputs; the
   pipeline e2e eval passes in an isolated clone.
3. The determinism audit is done: each skill's steps classified
   tool-call vs. LLM-reasoned, with extraction done for the mechanical ones; the
   trace shows the tool/LLM ratio per run so drift is visible.
4. `infra/` declares all three external systems — setup, manual-run, teardown.
   Nothing automated is undeclared.
5. `/onboard` yields `profile.yaml` + canonical files + passing `verify_setup.py`
   **including a live LinkedIn MCP handshake** (required, per Decision 2), zero Kanu
   data involved.
6. Guard test passes: zero personal references in template-side code.
7. **The friend test:** one friend, fresh machine, clones → onboards (incl. full
   LinkedIn setup) → runs jd-to-ready on a real JD → tunes one output via the trace
   chain — without Kanu's help. This is the v1 gate.
8. Live system untouched: `main`, launchd job, and cloud routine keep running as-is.

## Open Questions

None — all resolved into the Decisions table above.
```
