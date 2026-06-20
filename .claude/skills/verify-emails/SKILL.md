---
name: verify-emails
description: Resolve and verify recruiter or contact emails for a role from its contacts ledger, or run jd-to-ready step 4c to write `Verified Emails.md`; runs standalone when pointed at a ledger or as the pipeline step after `enrich-contacts` and before `write-outreach`, and does NOT trigger for finding contacts (`find-contacts`), drafting outreach (`write-outreach`), or checking whether postings are live (`verify-postings`).
---

# Verify Emails

A deterministic, stdlib-only workflow to resolve SMTP-verified recruiter emails for a role. The bundled script calls EmailFinder.dev's `/find-email/person` endpoint, where verified hits cost credits and 404 misses are free, then caches results so re-runs do not re-charge.

## When to use

Use this skill when Kanu wants to resolve or verify emails for contacts already captured in a role's contacts ledger, or when `jd-to-ready` reaches step 4c and needs `Verified Emails.md` written.

Works in two modes:

- Standalone: point the script at any role ledger and resolve the top recruiter emails.
- Pipeline: run after `enrich-contacts` and before `write-outreach` so outreach has a verified email artifact to read.

## When NOT to use

- Kanu needs recruiter or hiring-manager discovery -> use `find-contacts`.
- Kanu wants cold email copy drafted -> use `write-outreach`.
- Kanu wants to know whether job postings are still live -> use `verify-postings`.
- Kanu needs broader interview prep materials -> use the normal role-folder prep workflow.

## How it works

1. Reads the ledger's `**Email pattern:**` line and derives the company domain plus local-part template: `first.last`, `firstlast`, `first`, `flast`, `first_last`, or `last`.
2. Selects the top N `Recruiter` rows by `Rank` from the scored ledger table. Default: 3.
3. Calls EmailFinder.dev:

   ```text
   /api/find-email/person?full_name=&company_name=&domain=
   ```

   The request must include a browser `User-Agent`; Cloudflare returns 403 error 1010 without it. The bearer key comes from env `Email_Finder_Dev`, falling back to the workspace `.env`.

4. Assigns one of four statuses:

   - `VERIFIED` — EmailFinder.dev returned a verified API hit, or the result came from cache.
   - `INFERRED` — 404 miss plus known email pattern; address is synthesized and flagged unverified.
   - `NOT FOUND` — miss with no usable pattern.
   - `SKIPPED` — max credits reached, 402, 429, or network failure.

5. Caches results at `.claude/skills/verify-emails/.email-cache.json`, keyed by `name|company`, so re-runs never re-charge for the same contact.
6. Writes a `## Verified Emails` section back into the ledger and, with `--emails-md-default`, writes standalone `Verified Emails.md` using `| Name | Email | Confidence |` for `write-outreach`.

## Usage

Dry-run parse only, with zero credits:

```bash
python3 "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/.claude/skills/verify-emails/scripts/verify_emails.py" --ledger "Roles/<Company - Role>/.contacts-ledger.md" --dry-run --json
```

Pipeline step 4c:

```bash
python3 "/Users/kanumadhok/Documents/Claude/Projects/Interview Prep/.claude/skills/verify-emails/scripts/verify_emails.py" --ledger "Roles/<Company - Role>/.contacts-ledger.md" --emails-md-default --max-credits 5 --json
```

Flags:

- `--ledger` — required path to the contacts ledger.
- `--max-credits` — verified-hit credit cap. Default: 10.
- `--top` — number of ranked recruiter rows to resolve. Default: 3.
- `--dry-run` — parse and plan only; spend zero credits.
- `--json` — print machine-readable output.
- `--no-write` — do not write ledger or markdown artifacts.
- `--emails-md PATH` — write the standalone email artifact to a specific path.
- `--emails-md-default` — write `Verified Emails.md` next to the ledger.

## Key facts / gotchas

- The request needs a browser `User-Agent`; Cloudflare returns 403 otherwise.
- `company_name` beats raw domain for matching; send both. Misses are free.
- Credits are charged only on a verified hit.
- The cache makes re-runs free for already-resolved contacts.
- `INFERRED` rows are unverified guesses; flag them before sending.
- Missing key, no pattern, 402, 429, and network failures degrade gracefully and should never block the pipeline.

## Files

- `.claude/skills/verify-emails/scripts/verify_emails.py` — stdlib-only resolver and writer.
- `.claude/skills/verify-emails/.email-cache.json` — local cache keyed by `name|company`.
- EmailFinder.dev API reference — uses env var `Email_Finder_Dev`; never print the key value.
