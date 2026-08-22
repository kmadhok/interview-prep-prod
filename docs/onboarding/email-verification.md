# Email verification (optional)

The `verify-emails` skill calls EmailFinder.dev. Verification is optional and never
blocks the pipeline.

## Configure the key

Provide the bearer key through the `Email_Finder_Dev` environment variable:

```bash
export Email_Finder_Dev=<key>
```

Alternatively, add this line to a repo-root `.env` file:

```text
Email_Finder_Dev=<key>
```

The skill checks the environment first, then falls back to `.env`. The `.env` file
is gitignored.

## Without a working key

With no key, or after a 402, 429, or network failure, affected rows degrade to
`INFERRED`. These addresses are synthesized from the ledger's known email pattern
and flagged as unverified. They do not block the pipeline.

Never print the key or commit it to the repository.
