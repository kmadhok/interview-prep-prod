---
name: linkedin-mcp-operations
description: Use this skill BEFORE invoking any mcp__linkedin__* tool, when a LinkedIn MCP call fails or times out, or when diagnosing the linkedin MCP server. The single source of truth for how to use the LinkedIn MCP — the transport tiers (stdio default, HTTP daemon for unattended runners), the sequential-only rule (never parallel), the per-operation reference, and the diagnostic ladder for the launchd-supervised daemon (com.<user>.linkedin-mcp on 127.0.0.1:8765). Trigger phrases - "linkedin mcp", "scrape linkedin", "find contacts", "linkedin handshake", "mcp__linkedin", "transport error".
---

# LinkedIn MCP Operations

The one skill for using the LinkedIn MCP. Two things matter: the **transport must match how this instance was set up** (stdio by default; the HTTP daemon when one is installed — never both), and **calls must be sequential, never parallel** (the upstream scraper is not concurrency-safe). There are no usage caps, no delays, no cool-downs — use it as much as you want, one call at a time.

## The only two rules

1. **Do not change the registered transport mid-run.** If `linkedin` is registered as `"type": "http"` at `http://127.0.0.1:8765/mcp`, keep it — a launchd daemon owns that browser. If it is registered as stdio (`uvx mcp-server-linkedin@latest`), keep that — do not also start a daemon. (History: FastMCP 3.3.1 emitted stray `notifications/progress` frames that killed stdio; verified fixed 2026-08-24 on v4.23.1 / FastMCP 3.4.4.)
2. **Sequential only, never parallel.** One `mcp__linkedin__*` call in flight at a time: issue a call, await its result, then issue the next. Never put two LinkedIn calls in the same tool batch. The upstream scraper drives a real browser and is not concurrency-safe — parallel calls corrupt each other mechanically, independent of any rate-limit concern. **There is no limit on sequential volume.**

## How callers use this

Any skill needing LinkedIn data (e.g. `find-contacts`, `jd-to-ready`) may call `mcp__linkedin__*` tools **directly** — this skill is the reference for *how*, not a wrapper you must route every call through. The non-negotiable constraint callers inherit: **keep calls sequential.** Never fan out.

## Operations reference

The MCP is a browser-driven scraper, not an API client. Verify exact parameter names against the live tool on first use; when unsure, confirm params with the user rather than trial-and-erroring.

**Read ops:**
- `mcp__linkedin__search_people` — find people by company / title / school / keywords. Params: `keywords`, `current_company`, `school`, `connection_degree`, pagination. Use for discovery lists; don't use to verify a known person (use `get_person_profile` with their URL). Cap results ~25/call to keep page loads light.
- `mcp__linkedin__get_person_profile` — deep profile for a known URL. Visible to the target.
- `mcp__linkedin__get_inbox` — paged read of recent conversations.
- `mcp__linkedin__get_conversation` — full thread for one contact.
- `mcp__linkedin__get_company_profile` / `get_company_employees` / `get_company_posts` — company-level lookups.

**Write ops (confirm with the user before sending):**
- `mcp__linkedin__send_message` — DM a contact. Params: recipient/participant URL + message body. Only after the user has reviewed the draft and said "send."
- `mcp__linkedin__connect_with_person` — connection request. Confirm before sending.

**Multi-step runs:** search → drill into the top N profiles is a common pattern. Run it as a sequential chain (search, await, then each `get_person_profile` one at a time), never as a parallel batch.

## Retry policy

On any transport-level error (connection refused, 5xx, timeout):
1. `sleep 3`
2. Retry the same tool call exactly once.
3. If it fails again, STOP. Run the diagnostic ladder below and surface its output. Do not retry a third time and do not silently fall back.

## Diagnostic ladder

Run in order, stop at the first that explains the failure:

a. **Daemon log tail** — `tail -n 40 ~/.claude/logs/linkedin-mcp-daemon.log`
b. **Supervisor log tail** — `tail -n 20 ~/.claude/logs/linkedin-mcp-supervisor.log`
c. **Handshake** — see Common commands below; expect HTTP 200.
d. **launchctl status** — `launchctl list | grep 'linkedin-mcp'` (last column 0 = healthy, non-zero = crashed)
e. **Ask the user** — only after a–d are inconclusive, ask before running `launchctl kickstart -k gui/$(id -u)/com.<user>.linkedin-mcp`.

## Common commands

```bash
# Is the port listening?
lsof -nP -iTCP:8765 -sTCP:LISTEN

# MCP initialize handshake (expect 200)
curl -s -o /dev/null -w '%{http_code}\n' -m 5 -X POST http://127.0.0.1:8765/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"0.1"}}}'

# Job status
launchctl list | grep 'linkedin-mcp'

# Restart (only after diagnostic ladder a–d, with user confirmation)
launchctl kickstart -k gui/$(id -u)/com.<user>.linkedin-mcp
```

## What NOT to do

- Do not flip `linkedin` between `http` and `stdio` in `~/.claude.json` "just to test"; two transports mean two browsers fighting over one profile.
- Do not run two `mcp__linkedin__*` calls in the same tool batch.
- Do not `pkill -f linkedin` or `pkill -f streamable-http`. The daemon is owned by launchd; killing it manually causes a respawn race.
- Do not `launchctl unload` then re-`load` — use `kickstart -k` to preserve the agent registration.
- Do not bump the pinned `linkedin-scraper-mcp` version in the supervisor without first confirming upstream shipped a fix for the progress-token bug.
