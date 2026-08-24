# LinkedIn MCP setup

LinkedIn is required by `find-contacts`, `enrich-contacts`, `find-fresh-jobs`,
`linkedin-saved-jobs-intake`, `verify-postings`, and the `write-outreach` hooks.
`jd-to-ready` can file a role, tailor the resume, export the PDF, and build the apply
packet without LinkedIn. LinkedIn calls are sequential, never parallel: use one caller
per logged-in browser.

## Tier 1 — one-line install (default)

Register the upstream
[`stickerdaniel/linkedin-mcp-server`](https://github.com/stickerdaniel/linkedin-mcp-server)
package with Claude Code:

```bash
claude mcp add --scope project linkedin -- uvx mcp-server-linkedin@latest
```

Claude Code spawns the stdio server per session. On the first tool call that needs
authentication, the server opens a LinkedIn login window. To log in ahead of time,
run this once:

```bash
uvx mcp-server-linkedin@latest --login
```

Do not pin a version. LinkedIn's page structure changes often, so pinned versions rot.

For the health check, confirm that `claude mcp get linkedin` shows `Connected`, then
run:

```bash
python3 scripts/verify_setup.py
```

## Tier 2 — supervised HTTP daemon (unattended runners)

Choose Tier 2 for unattended runners, cloud or PC schedulers, or several callers that
must share one logged-in browser. Install the optional launchd supervisor by following
[the launchd runbook](../../infra/launchd/README.md). Once launchd owns the daemon,
never start a second copy by hand and never use `pkill`.

Register `linkedin` as an HTTP server in Claude Code:

```json
{
  "linkedin": {
    "type": "http",
    "url": "http://127.0.0.1:8765/mcp"
  }
}
```

The equivalent CLI command is:

```bash
claude mcp add --transport http linkedin http://127.0.0.1:8765/mcp
```

Confirm the port and perform an MCP initialize handshake:

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
curl -s -o /dev/null -w '%{http_code}\n' -m 5 \
  -X POST http://127.0.0.1:8765/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"setup-check","version":"0.1"}}}'
```

The handshake should return HTTP 200. If it does not:

1. Inspect the stdout/stderr paths configured in your plist.
2. Inspect status with `launchctl print "gui/$(id -u)/com.<your-short-name>.linkedin-mcp"`.
3. Restart the registered job, rather than launching another daemon:

   ```bash
   launchctl kickstart -k "gui/$(id -u)/com.<your-short-name>.linkedin-mcp"
   ```

## Why HTTP was once mandatory

FastMCP 3.3.1 emitted stray `notifications/progress` frames that tore down stdio
transports mid-call. That made stdio unsafe for this server. On 2026-08-24, server
v4.23.1 with FastMCP 3.4.4 ran authenticated profile, job-search, and company scrapes
over stdio with zero transport errors. The invariant that remains is sequential calls,
never parallel.

`python3 scripts/verify_setup.py` reports `PASS` when a `linkedin` MCP server is
registered with Claude Code using either transport or the HTTP daemon answers. It
reports `WARN` (contact research disabled) when neither exists. It reports `FAIL` only
when a registered HTTP endpoint is unreachable.
