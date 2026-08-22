# Interview Prep

Interview Prep is a human-gated job-search system for Claude Code. It turns a job
description into a filed role, tailored resume, PDF/apply packet, and—only after you
record that you applied—reviewable recruiter outreach. It drafts, never sends: ATS
submission and every outbound message remain explicit human actions.

## Requirements

- macOS for v1 onboarding and the required launchd-supervised LinkedIn daemon;
- Claude Code;
- Python 3.11 or newer, using the standard library;
- a local LinkedIn MCP server at `http://127.0.0.1:8765/mcp` (**required**);
- an EmailFinder.dev API key (optional; without it email verification degrades to
  flagged inferred addresses — see docs/onboarding/email-verification.md);
- an authorized Gmail connector for outreach staging; and
- `reportlab` only if you want PDF export (optional; missing support degrades to
  markdown without breaking the rest of setup).

Schedulers are optional. Manual mode is the supported default.

## Quick start

```bash
git clone <clean-export-repository-url>
cd <repository-directory>
claude
```

Inside Claude Code, run `/onboard`. The conversational setup creates your gitignored
`profile.yaml` and `workspace/`, guides LinkedIn and Gmail setup, and finishes with:

```bash
python3 scripts/verify_setup.py
```

The command exits zero when profile/workspace checks, the required live LinkedIn
reachability check, and the canonical behavior fixture all pass. Use `--skip-live`
only for clearly labeled machine-only validation.

## Behavior tests

Evals are the product's behavior tests. Build the self-contained synthetic workspace,
then run every local contract:

```bash
python3 scripts/build_fixture_workspace.py /tmp/interview-prep-fixture --force
python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture
```

The expected result is exit 0: every local clause is `PASS`; external live-only
clauses are `BLOCKED` by design. Add `--json` for machine-readable output. Pytest is
not part of the product gate; `scripts/test_*.py` files are optional developer
self-tests for deterministic helpers.

## Repository map

| Path | Purpose |
| --- | --- |
| `.claude/skills/` | Agent behavior and orchestration contracts. |
| `scripts/` | Deterministic helpers, verification, and optional runner code. |
| `evals/` | Behavior contracts, verifiers, and synthetic fixtures. |
| `templates/` | Blank canonical starters used by onboarding. Never put personal data here. |
| `infra/` | Required LinkedIn supervisor plus optional cloud/PC schedulers. |
| `docs/onboarding/` | Connector and manual-mode setup guides. |
| `workspace/` | Your instance: Pipeline, canonical evidence, and role folders. Gitignored. |
| `profile.yaml` | Your identity and filename configuration. Gitignored. |
| `runs/` | Per-run trace and human-readable repair reports. Gitignored. |

The repository is a template/instance split: reusable machinery stays at the root;
all personal content stays in `workspace/` and `profile.yaml`.

## Safety model

- **Apply gate:** `jd-to-ready` stops with an apply-ready packet. LinkedIn contact
  research and Gmail drafting do not run until the Pipeline row is marked `Applied`.
- **Draft, never send:** skills may create Gmail drafts or paste-ready text, but never
  send a message or submit an ATS application.
- **One LinkedIn browser:** calls are sequential and use one supervised HTTP daemon;
  stdio and parallel calls are forbidden.
- **No state database:** role folders, Pipeline rows, and deterministic markers are
  the state. Never hand-write a `STAGED` marker.
- **Truthful evidence:** resumes and outreach use canonical verified claims; unknown
  numbers remain `[NUMBER?]` until the user confirms them.

## Running by hand and troubleshooting

Start with [manual mode](docs/onboarding/manual-mode.md). Connector help lives in
[LinkedIn setup](docs/onboarding/linkedin-mcp.md) and
[Gmail setup](docs/onboarding/gmail.md); optional automation is declared in
[`infra/`](infra/README.md).

Trace hooks ship in `.claude/settings.json` and are explained in
[manual mode](docs/onboarding/manual-mode.md).

When output is wrong, use trace as the repair manual. Each orchestrator records why a
step ran and the source files that shaped it. The event contract is documented in
[`docs/trace/TRACE_SCHEMA.md`](docs/trace/TRACE_SCHEMA.md).

Before sharing or publishing, use the clean-export tool and execute
[`docs/release-gate.md`](docs/release-gate.md).

## License

MIT. See [LICENSE](LICENSE).
