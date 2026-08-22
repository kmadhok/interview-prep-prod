# Gmail connector setup

Gmail is used to stage recruiter and hiring-manager messages after you apply. The
system creates drafts only. It does not send email, and the final review/send action
always stays with you.

## Authorize Gmail

1. Sign in to Claude Code with the account that has access to your Claude connectors.
2. In Claude's connector settings, add Gmail and complete Google's authorization
   flow for the mailbox you want the job-search system to use.
3. Return to Claude Code and confirm the Gmail tools are available to the session.
4. Use a harmless read, such as searching for a message you already know, to confirm
   the connection before staging outreach.

If your organization restricts third-party Google access, ask its administrator to
approve the connector or use the role-folder draft manually.

## What staging does

After an application is marked `Applied` in `workspace/Pipeline.md`,
`stage-outreach` may create two Gmail drafts: one for the selected recruiter and one
for the hiring-manager or peer lead. The role folder keeps the source copy in
`Cold Outreach.md`.

Before sending, you must:

- verify the recipient and every claim;
- attach the tailored resume when the message says it is attached;
- honor the same-company double-send warning; and
- click Send yourself.

The skills may call Gmail's draft-creation operation. They must never call a send
operation. A `STAGED in Gmail <date>` marker means drafts were created; it does not
mean an email was sent.

## Troubleshooting

- No Gmail tools: reconnect Gmail in Claude's connector settings, then start a new
  Claude Code session.
- Draft has your own address: email verification degraded safely; replace the
  recipient only after checking `Verified Emails.md`.
- Missing attachment: expected. Draft creation cannot attach the resume, so attach
  it manually before sending.
- Duplicate draft risk: do not write or remove `STAGED` markers by hand. Let
  `stage-outreach` own that state transition.
