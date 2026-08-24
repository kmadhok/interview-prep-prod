# Infrastructure manifest

The system is manual-mode-first. One local service is required; schedulers are
optional conveniences.

| Component | Requirement | Purpose | Manual equivalent |
| --- | --- | --- | --- |
| [LinkedIn MCP launchd service](launchd/README.md) | Optional (Tier 2) | Shares one supervised HTTP endpoint across unattended runners; manual mode uses the one-line stdio install instead. | Register the stdio server: `claude mcp add --scope project linkedin -- uvx mcp-server-linkedin@latest`. |
| [Gmail secretary cloud routine](cloud-routines/README.md) | Optional | Reconciles application acknowledgements, sent drafts, and rejections into the Pipeline. | Run the reconciliation prompt in an interactive Claude Code session. |
| [PC runner](pc-runner/README.md) | Optional | Runs prep Pass A daily and outreach Pass B hourly. | Invoke each pass through `scripts/drip_runner/run.ps1`. |

Without either scheduler, follow [manual mode](../docs/onboarding/manual-mode.md):
run `jd-to-ready`, apply yourself, mark the Pipeline row `Applied`, then run
`stage-outreach`. Every outward action remains draft-only until a human sends it.

The root `Automation Architecture - *.md` files are historical design records. This
directory is the portable infrastructure contract for new installations.
