# LinkedIn MCP setup (required)

LinkedIn access is the only required external infrastructure in v1. The contact
research skills use a local browser-driven MCP daemon. Set it up once, keep it
supervised, and let `verify_setup.py` confirm that the configured endpoint is
reachable.

## 1. Install and sign in

1. Install the
   [`stickerdaniel/linkedin-mcp-server`](https://github.com/stickerdaniel/linkedin-mcp-server)
   server. This template was verified against tag `v4.22.0`; newer tags may work but
   are untested here.

   ```bash
   git clone https://github.com/stickerdaniel/linkedin-mcp-server.git
   cd linkedin-mcp-server
   git checkout v4.22.0
   uv sync
   ```
2. Run its documented interactive login once so the browser profile contains your
   LinkedIn session.
3. Configure the server for streamable HTTP on `127.0.0.1:8765` with the MCP path
   `/mcp`. A typical environment file contains:

   ```text
   TRANSPORT=streamable-http
   HOST=127.0.0.1
   PORT=8765
   HTTP_PATH=/mcp
   HEADLESS=true
   ```

Do not use stdio. The server's FastMCP layer can emit `notifications/progress` frames
for already-completed progress tokens; on stdio the MCP client treats that as a
protocol violation, tears down the transport, and kills in-flight calls. On
streamable HTTP each tool call is a fresh request, so the same condition becomes a
transient retry.

## 2. Install the launchd supervisor

Copy [the plist template](../../infra/launchd/com.example.linkedin-mcp.plist) to
`~/Library/LaunchAgents/`, replace every `__PLACEHOLDER__`, and give the file a label
such as `com.<your-short-name>.linkedin-mcp`. Then bootstrap it:

```bash
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.<your-short-name>.linkedin-mcp.plist"
launchctl enable "gui/$(id -u)/com.<your-short-name>.linkedin-mcp"
launchctl kickstart -k "gui/$(id -u)/com.<your-short-name>.linkedin-mcp"
```

Once launchd owns the daemon, do not start the server by hand. Two processes can
fight over the same port and browser profile. The complete lifecycle and rollback
steps live in [the launchd runbook](../../infra/launchd/README.md).

## 3. Register the MCP endpoint

In your Claude Code MCP configuration, register `linkedin` as an HTTP server:

```json
{
  "linkedin": {
    "type": "http",
    "url": "http://127.0.0.1:8765/mcp"
  }
}
```

Keep LinkedIn calls sequential. The scraper drives one browser profile and is not
safe for parallel requests.

## 4. Health check and recovery

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

Finally run `python3 scripts/verify_setup.py`. It checks the endpoint from the
optional `linkedin_mcp_endpoint` profile key, defaulting to
`http://127.0.0.1:8765/mcp`. `--skip-live` is only for machine-only validation; a
complete onboarding must pass the live check.
