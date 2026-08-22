# Optional Gmail secretary routine

The cloud routine is a convenience, not a prerequisite. It reconciles Gmail state
into `workspace/Pipeline.md` twice on weekdays. It does not use LinkedIn and does not
draft or send outreach; the local `stage-outreach` path is the only drafter.

## Scheduled behavior

Recommended cron shape: `0 13,21 * * 1-5` UTC. That is twice each weekday; local
wall-clock time shifts with daylight saving time. Each run:

1. pulls the repository before reading Pipeline state;
2. finds application acknowledgements and marks matching roles `Applied`;
3. finds sent staged messages and records the observable sent state;
4. finds rejections and moves or marks the role closed according to Pipeline rules;
5. commits only real changes, using an attributable automation prefix; and
6. never creates a Gmail draft, sends mail, researches LinkedIn, or writes a
   `STAGED` marker.

The last restriction prevents two independent drafters. Historical architecture
notes that describe cloud-side drafting predate the two-orchestrator split and are
not the v1 target behavior.

## Set up your own

1. Authorize Gmail as described in [Gmail onboarding](../../docs/onboarding/gmail.md).
2. Give the routine access to the clean repository and Gmail connector.
3. Use [prompt.md](prompt.md) as its complete prompt.
4. Schedule it twice on weekdays or choose a lower cadence.
5. Run it once manually and confirm a no-op produces no commit.
6. Test one synthetic or already-known acknowledgement before relying on it.

## Manual equivalent

Open an interactive Claude Code session in the repository and paste the exact prompt
from `prompt.md`. Review the proposed Pipeline diff before allowing the commit. This
performs the same Gmail reconciliation without any scheduler.

## Disable or remove

Pause or delete the routine in Claude's routine-management UI. No repository cleanup
is required because state lives in `workspace/Pipeline.md`, not in a routine database.
