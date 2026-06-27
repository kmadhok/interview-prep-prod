# Automation Architecture — Diagrams

_Drafted 2026-06-26, revised to the simple approach. Visual companion to `Automation Architecture - Two-Orchestrator Split.md` and the two `Spec - Orchestrator …` files. Mermaid renders inline in Obsidian._

Legend: 🟧 LinkedIn (daemon-bound, PC only) · 🟥 Gmail (drafts only) · `==>` writes/state · `-.->` reads/trigger.

**The simple model in one line:** both skills run on the PC (because every entry point touches the LinkedIn MCP); the cloud routine stays a pure Gmail secretary; the "apply" trigger is an hourly poll of `Pipeline.md`. **No `role_state.json`** — state is read from files that already exist.

---

## 1 · Current cloud routine ("Application Drip-Runner, 2×/weekday")

What runs today in the cloud (`trig_01Dhy19jRLQM6sggLQ4249rm`): a Gmail-driven Pipeline reconciler + secretary. It already detects "applied" (from Gmail acks) and stages drafts from contacts already in the folder, but cannot do LinkedIn research.

```mermaid
flowchart TD
    cron["⏰ Cron 0 13,21 * * 1-5 UTC<br/>8AM + 4PM CT · Sonnet 4.6 · cloud"] --> read["Read CLAUDE.md + Pipeline.md"]
    read --> g1["1 · GMAIL SWEEP<br/>search job-relevant mail (newer_than:1d)"]
    g1 --> g2["Update Pipeline rows:<br/>· app ack → mark row Applied<br/>· rejection/closed → Active→Closed + git mv to _Archived/<br/>· prepend dated audit note"]
    g2 --> d1["2 · DRAFT CHECK<br/>draft gone from Drafts = sent → log send date"]
    d1 --> d3{"≥4 unsent<br/>drafts?"}
    d3 -->|"yes"| skip["skip staging<br/>(reconcile only)"]
    d3 -->|"no"| a1["3 · ADVANCE ONE ROLE<br/>pick highest-value role whose outreach is due"]
    a1 --> a2{"contacts already<br/>in folder?"}
    a2 -->|"yes"| a3["stage ≤2 Gmail drafts<br/>verify claims vs Pipeline"]
    a2 -->|"no — needs LinkedIn"| a4["write 'contact research<br/>needed (local)' in row"]
    a3 --> c4["4 · render_pipeline.py<br/>commit 'drip-runner:' → push main"]
    a4 --> c4
    skip --> c4
    note["❌ never sends · 🟥 Gmail drafts only · ❌ no LinkedIn research"]
```

> In the simple target (diagram 5) this routine **keeps steps 1, 2, 4** and **drops step 3's drafting** — all drafting moves to the PC's outreach skill, which has the contacts because it just scraped them.

---

## 2 · Current `jd-to-ready` (monolithic orchestrator)

The skill as it exists now: one linear run, **all 7 steps on every saved job** — LinkedIn research and Gmail drafts for roles you may never apply to.

```mermaid
flowchart TD
    save["Saved job / JD shared"] --> i["1 · intake<br/>folder · Job Description.md · Pipeline row · memory"]
    i --> c["2 · classify (subagent)<br/>themes[] + archetype"]
    c --> r["3 · tailor-resume → resume.md"]
    r --> p["3.5 · build PDF + vision verify → resume.pdf"]
    p --> fc["4 · find-contacts → .contacts-ledger.md"]
    fc --> en["4b · enrich-contacts → hooks + extend ledger"]
    en --> ve["4c · verify-emails (EmailFinder) → Verified Emails.md"]
    ve --> wo["5 · write-outreach → Cold Outreach.md + Gmail drafts"]
    wo --> rep["6 · report"]
    rep --> log["7 · log / finish-run"]
    note["⚠ LinkedIn research + Gmail drafts fire on EVERY saved job"]
    classDef linkedin fill:#ffe0b2,stroke:#e65100,color:#000
    classDef gmail fill:#ffcdd2,stroke:#b71c1c,color:#000
    class fc,en linkedin
    class wo gmail
```

---

## 3 · Skill 1 — `jd-to-ready` (prep), save-side

Fires when you save a job on LinkedIn. Runs on the **PC** (its trigger `get_saved_jobs` and JD fetch `get_job_details` are LinkedIn-MCP). Cheap local work, no flag risk, stops at the apply gate. Adds the `.classification.json` hand-off.

```mermaid
flowchart TD
    save["🔗 get_saved_jobs (PC) → new job<br/>get_job_details → JD"] --> i["1 · intake<br/>folder · Job Description.md · Pipeline row (Considering)"]
    i --> c["2 · classify (subagent)<br/>themes[] + archetype"]
    c --> cj["📄 .classification.json (hand-off to Skill 2)"]
    c --> r["3 · tailor-resume → resume.md"]
    r --> p["3.5 · build PDF + vision verify → resume.pdf"]
    p --> rep["6 · report"]
    rep --> log["7 · log / finish-run"]
    log ==> mark["resume.md in folder = PREPPED<br/>saved_seen.json[job_id] = done"]
    note["✅ No outreach · No Gmail · Trace run-type jd-to-ready {1,2,3,3.5,6,7}"]
    classDef linkedin fill:#ffe0b2,stroke:#e65100,color:#000
    class save linkedin
```

---

## 4 · Skill 2 — `stage-outreach`, apply-side

Fires when the hourly poll finds a role marked **Applied** with no `STAGED` marker. Runs on the **PC** (LinkedIn). Does the whole research→verify→draft chain on one machine and drops a Gmail draft addressed to the #1 recruiter.

```mermaid
flowchart TD
    trig["🕐 hourly poll: Pipeline row Applied & not STAGED → (PC)"] --> pre["Read folder:<br/>JD · resume · .classification.json"]
    pre --> fc["4 · find-contacts → .contacts-ledger.md<br/>+ Gmail warm-tie check"]
    fc --> en["4b · enrich-contacts → hooks + re-sort ledger"]
    en --> ve["4c · verify-emails (EmailFinder) → Verified Emails.md"]
    ve --> wo["5 · write-outreach (drip)<br/>Cold Outreach.md + Gmail draft (To: #1 recruiter)"]
    wo --> rep["6 · report"]
    rep --> log["7 · log / finish-run"]
    log ==> mark["'STAGED in Gmail date' in folder + Pipeline row = DONE"]
    note["Drafts only · never sends · fulfills 'contact research needed (local)'<br/>Trace run-type stage-outreach {4,4b,4c,5,6,7}"]
    classDef linkedin fill:#ffe0b2,stroke:#e65100,color:#000
    classDef gmail fill:#ffcdd2,stroke:#b71c1c,color:#000
    class fc,en linkedin
    class wo gmail
```

---

## 5 · Suggested simple architecture

Both skills on the PC (the only LinkedIn-capable machine — and every entry point, including *detecting a save*, is a LinkedIn-MCP call). The cloud routine stays the Gmail secretary. The apply trigger is an hourly `Pipeline.md` poll. State lives in files that already exist — **no `role_state.json`, no separate apply-detector.**

```mermaid
flowchart TB
    li["🔗 LinkedIn saved jobs"]
    k_apply["👤 applies on ATS → marks Pipeline row Applied"]
    k_send["👤 reviews Drafts → sends to recruiter"]
    gmail["📧 Gmail: acks · replies · rejections"]

    subgraph pc["🖥 Always-on PC — only LinkedIn-capable machine"]
        passA["Cron Pass A (daily)<br/>get_saved_jobs → get_job_details"]
        s1["Skill 1 · PREP<br/>intake + tailor-resume + PDF"]
        passB["Cron Pass B (hourly)<br/>poll: Applied & not STAGED"]
        s2["Skill 2 · OUTREACH 🟧🟥<br/>find-contacts → enrich → verify<br/>→ write-outreach → Gmail draft"]
        passA --> s1
        passB --> s2
    end

    subgraph cloud["☁ Cloud routine — Gmail secretary (unchanged but drops drafting)"]
        sec["Gmail sweep → reconcile Pipeline<br/>· app ack → mark Applied<br/>· draft gone = sent → log<br/>· rejection → archive"]
    end

    subgraph state["🗃 Shared state (git)"]
        pipe["Pipeline.md (human + Applied / STAGED markers)"]
        folder["role folder: resume · .classification.json<br/>Cold Outreach.md · Verified Emails.md"]
        seen["saved_seen.json (ingestion dedup)"]
    end

    li -.->|"get_saved_jobs"| passA
    s1 ==> folder
    s1 ==> seen
    s1 ==> pipe

    k_apply ==> pipe
    pipe -.->|"reads (git pull)"| passB
    s2 ==> folder
    s2 ==>|"STAGED marker"| pipe
    s2 ==> drafts["🟥 Gmail Drafts (To: recruiter)"]
    drafts --> k_send

    gmail --> sec
    sec ==> pipe
    drafts -.->|"draft gone = sent"| sec
```

### Who owns what

| Actor | Runs where | Owns |
|---|---|---|
| Cron Pass A → Skill 1 (prep) | **PC** | resume + PDF on save; mark `saved_seen` done |
| Cron Pass B → Skill 2 (outreach) | **PC** | find recruiter → verify email → Gmail draft → `STAGED` marker |
| Cloud routine | **cloud** | Gmail→Pipeline reconcile, send-detection, rejection archival |
| You | — | apply (mark row Applied) · review + send the draft |

### State = file markers (no ledger)

| State | How it's read |
|---|---|
| `prepped` | role folder has a tailored resume `.md` |
| `applied` | Pipeline row marked **Applied** (by you, or the cloud routine from an app-ack) |
| `staged` | `STAGED in Gmail <date>` in the folder + Pipeline row |

### One decision baked in

The cloud routine's **step-3 drafting** overlaps Skill 2 — both could draft for applied roles. This diagram **retires cloud step-3 drafting** so there's exactly one drafter (the PC, which has the contacts). The `STAGED` marker is the safety net during any overlap. (Alternative: keep cloud step 3 as a folder-contacts-only fallback.)
