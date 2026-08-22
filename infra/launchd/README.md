# LinkedIn MCP launchd service

This is the required v1 infrastructure for macOS. It keeps exactly one LinkedIn MCP
daemon alive at `http://127.0.0.1:8765/mcp`.

## Install

1. Complete the server install and interactive login in
   [the onboarding guide](../../docs/onboarding/linkedin-mcp.md).
2. Copy `com.example.linkedin-mcp.plist` to a temporary file and replace:

   | Placeholder | Value |
   | --- | --- |
   | `__LABEL__` | A unique label, for example `com.<short-name>.linkedin-mcp` |
   | `__UV_PATH__` | Absolute output of `command -v uv` |
   | `__SERVER_REPO__` | Absolute LinkedIn MCP server checkout |
   | `__PATH__` | Minimal PATH containing `uv`, Python, and system binaries |
   | `__LOG_DIR__` | Existing user-owned log directory |

3. Validate and install it:

   ```bash
   plutil -lint /path/to/com.<short-name>.linkedin-mcp.plist
   mkdir -p "$HOME/Library/LaunchAgents"
   cp /path/to/com.<short-name>.linkedin-mcp.plist "$HOME/Library/LaunchAgents/"
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
   launchctl enable "gui/$(id -u)/com.<short-name>.linkedin-mcp"
   launchctl kickstart -k "gui/$(id -u)/com.<short-name>.linkedin-mcp"
   ```

After bootstrap, launchd owns the process. Never start another copy by hand, use
`pkill`, or switch the Claude MCP entry to stdio.

## Health

```bash
launchctl print "gui/$(id -u)/com.<short-name>.linkedin-mcp"
lsof -nP -iTCP:8765 -sTCP:LISTEN
python3 scripts/verify_setup.py
```

If the service is registered but unhealthy, inspect the configured logs and use:

```bash
launchctl kickstart -k "gui/$(id -u)/com.<short-name>.linkedin-mcp"
```

## Roll back a plist change

Keep the previously working plist beside the edited copy until the health check
passes. To restore it:

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
cp /path/to/known-good.plist "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
```

## Teardown

Teardown disables LinkedIn-dependent contact research until reinstalled:

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
rm "$HOME/Library/LaunchAgents/com.<short-name>.linkedin-mcp.plist"
```

This removes only the supervisor definition. It does not remove the server checkout
or its logged-in browser profile.
