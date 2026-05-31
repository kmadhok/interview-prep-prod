# Application Operating System

**Purpose.** Turn filed JDs into shipped applications. This system keeps the workspace from becoming a library of half-ready roles.

**Principle.** A role is not "worked on" until it has a next outbound action with an owner, a date, and a send/apply decision. Prep files are only useful if they move a role to one of these states:

- **Apply today**
- **Send outreach today**
- **Waiting with follow-up date**
- **Blocked by missing JD / location / contact / claim verification**
- **Closed**

---

## Daily Control Loop

Run this once in the morning or before any job-search block:

1. Generate the dashboard:

```bash
python3 scripts/build_application_dashboard.py
```

2. Open `Application Dashboard.html`. `Application Dashboard.md` is also generated as a plain-text companion.

3. Work the queues in this order:

- **Urgent / dated actions** - interviews, thank-yous, follow-ups due today or overdue.
- **Ready to send** - roles with JD + resume + outreach already drafted.
- **Ready to apply** - roles with JD + resume but missing outreach or final send decision.
- **One-step blocked** - roles missing exactly one thing.
- **Filed only** - ignore unless it is a top-fit role.

4. End every session by updating `Pipeline.md` with what actually happened:

- Applied
- Outreach sent
- Thank-you sent
- Waiting until date
- Closed / rejected / deprioritized

---

## Role States

Use these states consistently in `Pipeline.md`.

| State | Meaning | Next action |
|---|---|---|
| `Filed only` | Folder exists but JD/body/prep is incomplete | Capture JD body or close |
| `JD reviewed` | JD is readable and worth considering | Decide apply / skip |
| `Apply-ready` | Resume and outreach exist | Apply + send first outreach |
| `Applied` | Application submitted | Send outreach if not sent |
| `Outreach sent` | First message sent | Set 5-business-day nudge date |
| `Waiting` | Nothing to do until a date or reply | Review on follow-up date |
| `Interview scheduled` | Prep is now the priority | Stop application churn until prep is handled |
| `Closed` | Rejected, withdrawn, or stale | Move to Closed / On hold |

---

## Automation Boundaries

Codex can automate:

- Filing roles into folders.
- Building tailored resumes from `Resume Achievements Master.md`.
- Drafting cold outreach.
- Finding missing artifacts.
- Creating the daily dashboard.
- Preparing a send/apply checklist.
- Updating markdown trackers when you confirm what happened.

Codex should not silently automate:

- Submitting applications.
- Sending emails or LinkedIn messages.
- Using unverified resume claims.
- Running long LinkedIn contact research without your go-ahead.

---

## Standard Commands To Ask Codex

### Morning job-search block

```text
Run my application operating system: refresh the dashboard, identify the top 5 actions for today, and help me execute them one by one.
```

### Clear the ready queue

```text
Find every role that has JD + resume + outreach drafted but is not applied/sent. Give me a send/apply checklist ordered by highest fit.
```

### Convert one role to apply-ready

```text
Get <Company - Role> apply-ready. Use only Resume Achievements Master.md for resume claims and leave [VERIFY: ...] for anything unsupported.
```

### End-of-session cleanup

```text
Update Pipeline.md with what I sent/applied today, set follow-up dates, and regenerate the dashboard.
```

---

## Weekly Cleanup

Once a week:

- Close roles with no reply after 4 weeks unless there is a reason to keep them warm.
- Delete or demote low-fit filed-only roles.
- Pick 5 roles maximum for the next apply sprint.
- Verify any high-value claims in `Resume Claims To Verify.md` that would unlock stronger resumes.

The goal is not more folders. The goal is more finished outbound actions.
