# Domain glossary

Each definition points to the owning contract or implementation, not merely a mention.

- **active role** — A non-archived role represented by a row in `workspace/Pipeline.md` and a folder below `workspace/Roles/`; lifecycle rules are implemented by `scripts/pipeline_row.py`.
- **apply gate** — Mandatory human stop before an application is submitted; the `jd-to-ready` contract and `evals/apply-packet/contract.md` define it.
- **application packet** — Apply-side files and `.apply-packet.json` produced/verified by `evals/apply-packet/verify.py`.
- **behavior clause** — One independently reported requirement from a behavior’s `evals/<behavior>/contract.md`, parsed by `evals/run_eval.py`.
- **behavior trace** — JSONL evidence whose run/step/reason/source contract is defined by `docs/trace/TRACE_SCHEMA.md` and emitted by `scripts/trace_step.py`.
- **canonical master** — Cross-role evidence or reusable answer source under `workspace/`; the nine owned masters are enumerated in `AGENTS.md`.
- **clause failure** — Completed verifier result that violates a contract clause, distinct from verifier crash exit 4 in `evals/run_eval.py`.
- **fixture workspace** — Synthetic, non-personal instance created by `scripts/build_fixture_workspace.py`; all behavior evals should target it.
- **instance** — Root `profile.yaml` plus private `workspace/`, created by `scripts/onboard_workspace.py`; unlike `templates/`, it may contain identity and job-search data.
- **Pipeline row** — Canonical tabular role state mutated through `scripts/pipeline_row.py`, including Considering, Applied, and Gmail staging state.
- **primitive run** — Trace run for one skill rather than the jd-to-ready orchestration; represented by schema-v2 `run_type` in `scripts/trace_step.py`.
- **quarantine** — `workspace/Resume Claims To Verify.md`; claims there are prohibited from outward use until promoted, per `AGENTS.md`.
- **role folder** — Canonically named per-role directory created/refused by collision rules in `scripts/role_folder.py`.
- **STAGED marker** — `STAGED in Gmail <date>` Pipeline state that only `stage-outreach` may append after its deterministic gate; see `.claude/skills/stage-outreach/SKILL.md` and `scripts/pipeline_row.py`.
- **template/instance split** — Blank reusable starters in `templates/` versus personal working files in `workspace/`; enforced by `scripts/test_no_personal_refs.py`.
- **trace repair report** — Human rendering of trace gaps, failures, and abort reasons produced by `scripts/render_run_report.py`.
