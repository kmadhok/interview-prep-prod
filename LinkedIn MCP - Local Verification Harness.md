# LinkedIn MCP — Local Verification Harness

_Created 2026-06-21. How to verify a LinkedIn MCP tool's real behavior against the live authenticated session — without going through the running daemon and without disturbing it. Written while verifying PR #523 (`get_saved_jobs`) on `stickerdaniel/linkedin-mcp-server`._

**Why this exists.** The daemon connected to a Claude session is the *installed* build. A new/changed tool on a PR branch isn't in it, so `mcp__linkedin__*` can't exercise the branch. To test branch code against your real LinkedIn data you drive the branch's own extractor directly. This note is the repeatable recipe.

---

## When to use it
- Verifying a PR/branch that adds or changes a scraping tool (e.g. `get_saved_jobs`, `search_jobs`).
- Confirming a suspected bug empirically (e.g. the saved-jobs pagination stride — see §5).
- Any time mocked unit tests pass but you need "does it actually work against live LinkedIn?".

## The two hard rules (inherited from the `linkedin-mcp-operations` skill)
1. **Sequential only — and the daemon counts.** One browser-driven operation at a time. The harness is a *separate process* but, on this machine, launches Chrome **directly on the same source profile** the daemon uses (`G:\linkedin-mcp\profile`). Interleaving harness runs with daemon `mcp__linkedin__*` calls contends that profile.
2. **Headless + gentle.** Run headless, smallest page count that proves the point. It's a real scrape on the real account.

## ⚠️ Hard-won lesson (2026-06-21) — profile contention is the real trap
Verifying PR #523 I ran: harness `get_saved_jobs` ×2 → daemon `get_job_details` (round-trip) → harness pagination check. The **pagination check launched onto LinkedIn's login page** ("Stored runtime profile is invalid"). Diagnosis:
- The source session was **fine** — a single daemon `get_my_profile` afterward returned the full profile. **Not** expiry, **not** server-side flagging.
- Cause: **profile contention.** Each harness run launches Chrome on the source profile and `close_browser()` left **orphaned `chrome-headless-shell` processes** (the "unclosed transport" warnings are the tell). With the daemon's browser also touching the same dir, a fresh launch saw no valid session.
- **The takeaway:** "don't call daemon tools *during* the run" is **not enough** — orphaned children + the daemon sharing the same profile dir corrupt the launch state across runs. For anything beyond a single one-shot harness call, **use an isolated profile** (below). If you do a one-shot, **verify orphan chromes are gone** (`tasklist | findstr chrome-headless-shell`) before the next launch.

### Isolated-profile mode — VALIDATED 2026-06-21 (use this for multi-run / pagination experiments)
Avoid touching the live daemon profile entirely by forcing the server's **cookie-bridge** path into a throwaway root. This ran clean with the daemon up and orphan chromes present — zero contention:

1. `mkdir -p G:\linkedin-mcp-test\profile`
2. `cp G:\linkedin-mcp\cookies.json G:\linkedin-mcp-test\` and `cp G:\linkedin-mcp\source-state.json G:\linkedin-mcp-test\` (use `cp`, never `cat`/`head` — printing the cookie is a credential leak and gets blocked).
3. `touch G:\linkedin-mcp-test\profile\.keep` — the gate requires a **non-empty** `profile\`.
4. In the copied `source-state.json`, change `"source_runtime_id"` from `windows-amd64-host` to anything else (e.g. `windows-amd64-foreigntest`). This makes `get_or_create_browser` treat the run as a **foreign runtime**, so it **bridges the portable `cookies.json` into a fresh derived profile** instead of launching on the (would-be-shared) source profile. `experimental_persist_derived_runtime()` defaults off → the simple no-checkpoint bridge.
5. Run with the env override: `USER_DATA_DIR='G:\linkedin-mcp-test\profile' uv run python _harness.py`.
6. **Cleanup is mandatory:** `rm -rf G:\linkedin-mcp-test` — it holds a copy of the live session cookie.

Gotchas seen:
- **First saved-jobs nav after the bridge can throw** `Execution context was destroyed … because of a navigation` and return 0 ids. Add a **warm-up `_extract_saved_jobs_page(BASE)`** before the real loop, plus a **one-shot retry on empty**. Second run was clean.
- Orphan `chrome-headless-shell` on the *daemon's* profile don't affect the isolated run (different dir), but still clean them up for RAM.

### When a live run IS worth it (and when it isn't)
Convergent evidence often settles a question without a scrape: PR #523's stride bug was already implied by three signals — Greptile static analysis, the author's "2 pages = 20 IDs," and my `start=0 → 10 IDs`. The lesson is that the **safe** way to get the final airtight proof is *isolated mode*, not another run on the shared profile. The clean isolated run nailed it: `start=0/10/25` each returned 10 ids, all disjoint — proving the stride-25 code skips the 10 saved jobs at offsets 10–19. Decision rule: if you want empirical certainty, pay the ~5 min for isolated mode; **never** reach for a quick contended run on the daemon's profile to save time — that's what corrupted the session earlier.

## Prereqs (verified present 2026-06-21)
- Repo: `G:\projects\linkedin-mcp-server` (check out the PR: `gh pr checkout <N>`).
- `uv` available; `uv sync --dev` once.
- Authenticated source session at `G:\linkedin-mcp` — needs `cookies.json`, `source-state.json`, and a non-empty `profile\`. (Env `USER_DATA_DIR=G:\linkedin-mcp\profile` already points the config here.)
- Daemon idle: it lazily opens Chrome per call, so as long as you don't trigger it, the profile is unlocked.

---

## The recipe

Drive the project's *own* browser bootstrap so the auth/profile path matches the server exactly, then call the extractor method directly. Drop a throwaway script in the **repo root** (not the vault), run it, delete it.

```python
# _live_check.py  (throwaway, in G:\projects\linkedin-mcp-server)
import asyncio, logging
logging.basicConfig(level=logging.INFO)

from linkedin_mcp_server.drivers.browser import (
    close_browser, ensure_authenticated, get_or_create_browser, set_headless,
)
from linkedin_mcp_server.scraping import LinkedInExtractor

async def main():
    set_headless(True)
    browser = await get_or_create_browser(headless=True)
    await ensure_authenticated()                 # raises if session is stale
    extractor = LinkedInExtractor(browser.page)

    result = await extractor.get_saved_jobs(max_pages=1)   # call the tool under test
    print("job_ids:", len(result["job_ids"]), result["job_ids"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        try: asyncio.run(close_browser())
        except Exception: pass
```

Run: `uv run python _live_check.py`  →  then `rm _live_check.py`.

**Notes**
- `get_config()` reads `USER_DATA_DIR` from env automatically; no CLI args needed.
- The trailing `ValueError: I/O operation on closed pipe` / `unclosed transport` lines on Windows are **asyncio shutdown noise**, not failures — ignore them.
- Same-machine runtime → the harness launches Chrome **directly on the source profile**. That's why rule #1 matters.

---

## §5 — Pattern: confirm a pagination stride

Saved-jobs pages may not use the same page size as job search. To prove the real stride, fetch by explicit `?start=` offset and diff the ID sets — overlap or a gap tells you the stride:

```python
    base = "https://www.linkedin.com/my-items/saved-jobs/"
    for start in (0, 10, 25):
        url = base if start == 0 else f"{base}?start={start}"
        await extractor._extract_saved_jobs_page(url, section_name="saved_jobs")
        ids = await extractor._extract_job_ids()        # reads the current page
        print(f"start={start}: {len(ids)} ids -> {ids}")
        await asyncio.sleep(2)                           # be gentle; stay sequential
```

Interpretation:
- `start=0` returns N ids → that's the page size.
- If `start=10` returns the *next* N with **no overlap** and `start=25` overlaps/gaps → real stride is 10, and code using stride 25 **skips offsets 10–24**.
- This is exactly the PR #523 case: page 1 = 10 ids, but the code paginated with `_PAGE_SIZE = 25` (correct fix: stride 10).

---

## Checklist for a verification pass
- [ ] `gh pr checkout <N>` in `G:\projects\linkedin-mcp-server`; `uv sync --dev`.
- [ ] Run the PR's own tests first (`uv run pytest <suites>`).
- [ ] Confirm no daemon scrape will fire during the run (don't call `mcp__linkedin__*`).
- [ ] Write throwaway harness in repo root, run headless with smallest page count.
- [ ] Capture result; if confirming a bug, use the explicit-`?start=` diff (§5).
- [ ] Delete the harness; `git status` clean except intended files.
- [ ] If round-tripping IDs, hand **one** id to the daemon's `get_job_details` *after* the harness browser is closed (sequential).

## Possible next step (optional)
- Promote the harness into `scripts/` (e.g. `scripts/linkedin_live_check.py` with a `--tool` / `--max-pages` / `--start-offsets` CLI) so it's a permanent verification tool rather than a copy-paste each time. Out of scope until there's a second use.
