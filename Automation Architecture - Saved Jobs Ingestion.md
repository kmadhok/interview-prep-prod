# Automation Architecture — Saved Jobs Ingestion (improvements spec)

_Created 2026-06-21. Companion to `Automation Architecture - Runtime (Email to Pipeline).md` (the live intake loop), `Automation Architecture - Skill Sync (Mac to PC).md`, and the parent `Automation Architecture - Drip Runner.md`. Verification recipe: `LinkedIn MCP - Local Verification Harness.md`._

**Status: BUILT 2026-06-21, now the default ingestion mode; full-staging smoke test pending (blocked on the draft backlog).** Saving a job on LinkedIn is a lower-friction front door than emailing yourself a `JOB:` URL. Done so far: the stride bug is fixed (saved-jobs-specific `_SAVED_JOBS_PAGE_SIZE = 10`, branch `feature/522-get-saved-jobs`, committed locally + tests green); the daemon was restarted on that branch and **`get_saved_jobs` is verified live** (returned 10 real saved jobs, ~20 pages / ~200 total); the runner adapter is built (`runner-prompt-saved.md`, `saved_jobs_ledger.py` + tests, `run.ps1 -Mode saved` default). The Gmail email queue is kept as the secondary `-Mode email` path for ATS / non-LinkedIn URLs — saved-jobs does **not** delete it. The `>=4 unsent drafts` backpressure guard was **removed 2026-06-21 per Kanu** (he does not want a draft backlog to block processing); the only per-run bound now is one role per run for runtime. Still pending: a full end-to-end staging run.

---

## Why this exists

Today a job enters the pipeline when you email yourself `JOB: <title>` with a URL in the body (filter → `drip-queue` → runner). That works, but the natural moment you decide you're interested in a role is when you're **already on LinkedIn**, where the action is one click: **Save**. This spec captures using your LinkedIn *saved jobs* list as an ingestion source so the friction drops from "compose an email" to "click Save."

**The key insight that makes this cheap:** the runner's downstream is source-agnostic. `job_parser.py` → `dedupe.py` (on `job_id` vs `Pipeline.md`) → `jd-to-ready` doesn't care whether the `job_id` came from an email body or a saved-jobs scrape. So saved-jobs is a **front-end adapter that fills the same queue**, not a rewrite of the pipeline.

---

## Dependency — the tool is branch code, not shipped

`get_saved_jobs` is a real, registered MCP tool — `mcp__linkedin__get_saved_jobs` — but it lives on branch **`feature/522-get-saved-jobs`** (issue #522 / PR #523) of `stickerdaniel/linkedin-mcp-server`. It is **not merged upstream** and the **running daemon predates it** (daemon started 2026-06-19; the branch was checked out 2026-06-21). So the installed daemon does **not** expose it yet.

Implementation present on the branch (verified 2026-06-21):
- `linkedin_mcp_server/tools/job.py` — `get_saved_jobs(max_pages: int[1..10] = 3)` registered as an MCP tool.
- `linkedin_mcp_server/scraping/extractor.py:3347` — `get_saved_jobs()` extractor: navigates `/my-items/saved-jobs/`, extracts innerText + `job_id`s per page, paginates by `?start=` offset. Returns `{url, sections:{saved_jobs:text}, job_ids:[str]}`. Has graceful rate-limit handling (`_RATE_LIMITED_MSG`) and reads LinkedIn's reported total page count to stop early.

## The blocker bug — pagination stride (must fix before multi-page use)

`extractor.py` paginates with `start = page_num * _PAGE_SIZE`, and `_PAGE_SIZE = 25` (line 59). But the **real saved-jobs page size is 10** — established empirically in `LinkedIn MCP - Local Verification Harness.md` §5 (the `?start=` diff method). With stride 25 the fetch jumps `start=0 → start=25 → start=50`, **silently skipping your saved jobs at offsets 10–24, 35–49, …**

- `max_pages=1` is **safe** today (only page 0 / offset 0 is read).
- `max_pages>1` (and the **default is 3**) **loses jobs**.
- **Fix:** `_PAGE_SIZE = 10`. Re-confirm with the harness §5 `?start=` diff after the change.

---

## Design — a saved-jobs adapter in the runner

Slot saved-jobs in as an alternate/primary **ingestion mode**; everything after `job_id` resolution is the existing pipeline.

```
get_saved_jobs(max_pages=N)  ──▶ [job_id, ...]
        │  (sequential, single daemon — see linkedin-mcp-operations)
        ▼
for each job_id (oldest-interest first):
   dedupe.py --job-id <id> --pipeline Pipeline.md     # already-processed → skip
        │ NEW
        ▼
   get_job_details(job_id) ──▶ JD text  ──▶ jd-to-ready (drafts only, never send)
        │
        ▼
   Pipeline row + "STAGED in Gmail <date>"; commit drip-runner: ; push
```

Concrete changes:
- **`runner-prompt.md`:** add an ingestion-mode switch. Either (a) a pre-step that lists saved jobs and builds the worklist, or (b) a separate `runner-prompt-saved.ps1`/prompt. Until the stride bug is fixed, hard-cap `max_pages=1` in the prompt and log that the cap is in force (no silent truncation — see the master plan's "no silent caps" rule).
- **Reuse `dedupe.py` as-is** — it already keys on the LinkedIn `job_id`, which is exactly what `get_saved_jobs` returns. No new dedupe logic.
- **Reuse `jd-to-ready`** unchanged — it receives JD text from `get_job_details`, same as the email path's LinkedIn branch.

## Idempotency — the one real difference from the email queue

The email queue carries per-job *state* in Gmail labels (`drip-queue/processing/done/error`). A saved-jobs list is a **flat set with no per-job state** — re-scanned in full every run. Consequences and the model:

- **"Already done" is handled** by `dedupe.py`: any `job_id` already in `Pipeline.md` is skipped. So re-scanning is harmless for completed roles. Mental model: **saving a job = consent to process it; once processed it lands in Pipeline and dedupes out.**
- **Gap — failed/parked jobs have no `drip-error` equivalent.** A saved job that errors stays saved and will be **retried every run**, with no visible "parked" state. Options (pick in §Open decisions):
  1. **Accept the retry** (simplest; transient failures self-heal, but a permanently-bad posting retries forever and burns a scrape each run).
  2. **A processed-ledger file** (e.g. `scripts/drip_runner/saved_seen.json` of `job_id`s attempted) so failures are remembered and skipped, mirroring `drip-done/error`.
  3. **Unsave after processing** via LinkedIn — *not recommended*: mutation = added flag risk, the MCP may not support it, and it destroys your own saved list.

## Coverage — LinkedIn-only, so it's additive not a replacement

Saved-jobs only covers **LinkedIn-native postings**. ATS postings (Greenhouse / Lever / Workday) have no "save to LinkedIn." Therefore:

- **Keep the email queue** as the catch-all for ATS / any-URL jobs.
- Saved-jobs becomes the **primary LinkedIn front door**; email stays the escape hatch. This is *more* surface area, accepted deliberately for the friction win on the LinkedIn-heavy majority.

## Branch-pin tradeoff

Using this means running the daemon off an **unmerged feature branch** (or your own fork carrying the stride fix) until PR #523 lands upstream. That's an ongoing maintenance commitment: re-pin/rebase on upstream changes, re-verify after each daemon update. Decision: **pin now** (move fast) vs **wait for upstream merge** (less maintenance). Recommendation: pin a fork with the one-line stride fix; revert to upstream once #523 merges with the fix.

---

## Verification plan (use `LinkedIn MCP - Local Verification Harness.md`)

The two hard rules carry over: **sequential only** (one browser op at a time — do not call `mcp__linkedin__*` on the daemon while the harness runs; both use `G:\linkedin-mcp\profile`) and **headless + gentle**.

1. `gh pr checkout 523` in `G:\projects\linkedin-mcp-server`; `uv sync --dev`; run the PR's own tests.
2. Harness, `max_pages=1`: confirm `get_saved_jobs` returns your real saved `job_id`s (expect ~10 on page 1).
3. Harness §5 `?start=` diff at offsets 0/10/25: confirm the stride-10 reality and that current code (stride 25) skips 10–24.
4. Apply `_PAGE_SIZE = 10`; re-run §5 to confirm offsets 0/10/20 tile with no gap/overlap.
5. Restart the daemon **on the fixed branch** (retire the hand-started one first — single-daemon rule). Then via the live MCP tool, round-trip **one** `job_id` through `get_job_details` *after* the harness browser is closed (sequential).
6. Add the adapter to the runner; smoke-test: save one LinkedIn job → run `run.ps1` (saved-jobs mode) → verify draft staged + Pipeline row + dedupe on a second run.

## Build checklist
- [ ] Fork + one-line stride fix (`_PAGE_SIZE` 25 → 10); re-verify via harness §5.
- [ ] Decide idempotency model (accept-retry vs processed-ledger vs unsave) — §Idempotency.
- [ ] Restart daemon on the fixed branch; retire the prior daemon (single-daemon rule).
- [ ] Add saved-jobs ingestion mode to `runner-prompt.md` (cap `max_pages` + log the cap until fix is confirmed live).
- [ ] Keep email queue as the ATS / any-URL path.
- [ ] Smoke-test the full saved-jobs path end-to-end; confirm dedupe on re-run.

## Open decisions
1. **Idempotency for failures:** accept-retry, processed-ledger, or unsave? (Recommend: processed-ledger — cheap, mirrors `drip-error`, no mutation/flag risk.)
2. **Branch strategy:** pin a fork now vs wait for upstream PR #523 merge.
3. **Ingestion-mode shape:** one runner prompt with a mode switch, or a separate saved-jobs prompt/entrypoint.
4. **Cadence interaction:** saved-jobs can surface many roles at once; the one-role-per-run bound keeps runtime sane. (The draft-backlog staging pause was removed 2026-06-21 per Kanu.)
