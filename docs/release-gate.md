# Release gate

Run this checklist against a clean-history export before publishing or inviting a
friend to test. The machine gate is deterministic except for the required live
LinkedIn handshake. The human gate deliberately retains the ATS and send actions.

## Machine validation (five steps)

### 1. Create, initialize, and clone a clean export

From the private development repository:

```bash
python3 scripts/export_template.py /tmp/interview-prep-release-source --force
git -C /tmp/interview-prep-release-source init
git -C /tmp/interview-prep-release-source add .
git -C /tmp/interview-prep-release-source -c user.name='Release Gate' -c user.email='release-gate@example.invalid' commit -m 'release-gate: clean export'
git clone /tmp/interview-prep-release-source /tmp/interview-prep-release-clone
cd /tmp/interview-prep-release-clone
git status --short
```

**Pass:** the export command reports a clean full-tree scan; the clone succeeds; and
`git status` is empty. The clone contains no `workspace/`, root `profile.yaml`,
`.lavish/`, `.obsidian/`, `runs/`, or private design/history documents. See
`scripts/export_template.py`.

### 2. Confirm runtime requirements

```bash
python3 --version
claude --version
python3 -c 'import importlib.util; print("reportlab optional:", bool(importlib.util.find_spec("reportlab")))'
```

**Pass:** Python is 3.11 or newer and Claude Code launches. Either reportlab result is
valid; `False` means PDF export will warn and degrade gracefully. Complete
[`docs/onboarding/linkedin-mcp.md`](onboarding/linkedin-mcp.md) and
[`docs/onboarding/gmail.md`](onboarding/gmail.md) before the next step.

### 3. Onboard and verify the instance

```bash
claude
```

Inside Claude Code, run `/onboard`. When it finishes, run:

```bash
python3 scripts/verify_setup.py
```

**Pass:** `profile.yaml`, `workspace/Roles/`, and all nine customized masters exist;
the table has no `FAIL` rows. A reportlab `WARN` is acceptable. A LinkedIn `FAIL` is
not. See `.claude/skills/onboard/SKILL.md`.

### 4. Run every fixture behavior contract

```bash
python3 scripts/build_fixture_workspace.py /tmp/interview-prep-fixture --force
python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture
python3 evals/run_eval.py --all --workspace /tmp/interview-prep-fixture --json
```

**Pass:** both eval commands exit 0; all local clauses are `PASS`, live-only clauses
are `BLOCKED`, and the last command emits parseable JSON. Evals—not pytest—are the
product behavior gate.

### 5. Prove the live LinkedIn MCP handshake

```bash
curl -s -o /dev/null -w '%{http_code}\n' -m 5 \
  -X POST http://127.0.0.1:8765/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"release-gate","version":"0.1"}}}'
```

**Pass:** the command prints `200`. If it does not, follow the recovery ladder in
[`docs/onboarding/linkedin-mcp.md`](onboarding/linkedin-mcp.md); do not start a second
daemon by hand or switch to stdio.

## Human validation (five steps)

Use one real role the tester genuinely wants. This section changes the tester's
gitignored instance and may create Gmail drafts, but it must never send anything.

### 1. Prepare one real JD

```bash
claude
```

Paste the real JD and invoke `/jd-to-ready` with apply intent.

**Pass:** one role folder contains `Job Description.md`, `.classification.json`, a
tailored resume markdown, a one-page PDF when reportlab is available, application
answers, and apply-packet state. The Pipeline row remains pre-apply and no contact
research or Gmail draft occurred. See `docs/onboarding/manual-mode.md`.

### 2. Apply through the ATS

Review the packet, submit the application yourself, then edit
`workspace/Pipeline.md` so the role is under Active and its stage contains `Applied`.

**Pass:** the employer confirms submission; the row contains `Applied` and does not
contain `STAGED`. No agent submits the ATS form.

### 3. Stage post-apply outreach

```bash
claude
```

Invoke `/stage-outreach` for the Applied role.

**Pass:** the role folder gains `.contacts-ledger.md`, `Verified Emails.md`, and
`Cold Outreach.md`; Gmail contains reviewable drafts; the deterministic gate—not a
manual edit—writes `STAGED in Gmail <date>` only after successful staging.

### 4. Prove drafts exist and nothing was sent

In Gmail, open Drafts and Sent. Search the exact recipients/subjects recorded in
`Cold Outreach.md`.

**Pass:** each staged message exists in Drafts and no matching message exists in
Sent. Do not click Send during the release gate. Confirm attachments are absent until
the human adds them, as documented in `docs/onboarding/gmail.md`.

### 5. Repair one disliked output through its trace

Open the newest `runs/<run-id>/report.md`, choose one output you dislike, follow that
step's `sources` to the owning skill or canonical workspace master, make one targeted
edit, and rerun only the affected skill.

```bash
python3 scripts/render_run_report.py "runs/<run-id>"
```

**Pass:** the tester can explain the chain—output → step → skill/prompt → source
markdown—make a source-level fix, and observe the improved rerun without assistance
from the original repository owner. The trace schema is documented in
[`docs/trace/TRACE_SCHEMA.md`](trace/TRACE_SCHEMA.md).
