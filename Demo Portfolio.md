# Demo Portfolio

**Purpose.** Single source of truth for the live demos and shippable artifacts I point to across resumes, outreach, and interviews. When I link a "Live Demo" line on a resume or paste a URL into a cold email, it comes from this file — so the description, link, and talking points stay consistent everywhere.

**How to use.**

1. When tailoring a resume, copy the **header line** from the demo that best matches the role into the resume contact block (replaces the default "Live Demo: NL-to-SQL Copilot" line).
2. When sending an outreach email, link the **demo URL** and use the **one-sentence pitch** as the value-prop hook.
3. Before any interview, re-read the **canonical talking points** for whatever demo I've put in front of the panel. They will click the link — don't get caught not remembering the version that's live.
4. Update the **last-verified date** every time I refresh or redeploy. Stale demos are worse than no demos.

---

# Demo 1 — NL-to-SQL Copilot (default)

**Header line (drop-in for resume contact block):**

```
Live Demo: NL-to-SQL Copilot — Dockerized Streamlit on GCP Cloud Run
```

**Demo URL:** https://sql-rag-frontend-simple-481433773942.us-central1.run.app/

**Repo / source:** [TO ADD — github.com/kmadhok/... if public, or "private repo, available on request" if not]

**Last verified live:** 2026-05-22

### One-sentence pitch

A natural-language analytics copilot — type a question in English, get SQL and the answer back, grounded in a 12K-query historical corpus and a structured context layer over BigQuery. The same architecture I deployed inside Walmart Data Ventures, stripped to a public-facing demo.

### Canonical talking points (for interviews where this gets pulled)

- **What it does.** Takes a natural-language question, retrieves relevant context from a structured knowledge base, generates SQL grounded in that context, executes against a sample BigQuery dataset, returns the answer with the SQL shown.
- **What's under it.** RAG retrieval over a corpus of historical queries (FAISS + BM25 hybrid), multi-agent LLM orchestration for plan-then-execute, the same MCP-shaped tool layer I built at Walmart.
- **Why this version exists.** The Walmart V2 is internal; this is the public-facing version of the same architecture, deployed on GCP Cloud Run so anyone reviewing my resume can actually click it and try it.
- **What it isn't.** Not a toy LLM-wrapper. It's the public mirror of the architecture I'm describing on the resume.

### Best for

- Any role where text-to-SQL, RAG, or agent-on-data work is the core ask.
- Walmart Agent Builder · Snorkel FDE · BCG X AI Factory · most data-engineering / AI-engineering roles.

### Watch-outs

- Confirm the URL still loads before any interview. Cloud Run can cold-start; first request can be slow.
- Don't paste the Walmart-internal version's screenshots or naming — this demo uses a public sample dataset.
- If asked "is this what runs at Walmart" — answer honestly: "Same architecture, public sample dataset, demo version. The Walmart deployment runs against a 43-table BigQuery dataset internally."

---

# Demo 2 — FTI RAG Proposal Generator (consulting-coded)

**Header line (drop-in for consulting / FDE / BCG-X roles):**

```
Live Demo: RAG Proposal Generator — UChicago MSADS Capstone (Best in Show)
```

**Demo URL:** [TO ADD if still live — otherwise omit and reference repo + the Best in Show recognition]

**Repo / source:** [TO ADD]

**Last verified live:** [TO FILL IN]

### One-sentence pitch

A retrieval-augmented proposal generator I shipped into FTI Consulting's actual workflow — query rewriting + adaptive chunking, Dockerized Streamlit on AWS EC2, adopted on production work and won Best in Show at UChicago MSADS Capstone.

### Canonical talking points

- **What it does.** Takes a client brief, retrieves relevant past proposals and case-study content with query rewriting and adaptive chunking, generates a draft proposal grounded in the firm's prior work.
- **What's measured.** −30% proposal time. +34% generation quality (from query rewriting). +42% retrieval accuracy (from adaptive chunking).
- **Why it matters in interviews.** Proof I can ship into a *real client's workflow*, not just demo and walk away. FTI didn't just see the demo — they adopted it.
- **Why this is the right demo for consulting-flavored roles.** BCG X, Snorkel, Deloitte all want signal that I can drop into a customer org and ship something that gets used. This is the cleanest version of that proof.

### Best for

- BCG X · Snorkel FDE · Deloitte GPS · any FDE / consulting / client-facing role.

### Watch-outs

- Demo may not be live anymore (capstone, not ongoing project). If the URL is dead, reference the repo + the Best in Show recognition instead. Don't link a 404.
- The +34% / +42% / −30% numbers are the canonical proof points. Don't round or paraphrase — keep them exact.

---

# Demo 3 — GitHub portfolio (always linked)

**Header line (always in resume contact block):**

```
github.com/kmadhok
```

**What lives there.** [TO INVENTORY — list public repos worth pointing to: NL-to-SQL Copilot, any Claude Code skills I've published, any MCP servers, FTI capstone if public, anything else worth a look.]

**Best for.** Every resume. The GitHub link gives the panel a fallback if a specific demo URL is down.

**Watch-outs.**

- Pinned repos should match what the resume claims. If the resume foregrounds "authored + published Claude Code skills," there should be a pinned skill repo.
- Strip stale or embarrassing repos from the public profile. Anything pinned is a thing I can be asked about.

---

# Internal Walmart artifacts (referenced, not linkable)

These are the Walmart-internal builds I describe in interviews. They're not public, but the talking points stay consistent here so I describe them the same way every time.

| Artifact | Internal name | One-line description | Story ID |
|---|---|---|---|
| Jira resolution agent | jira-ticket-worker v3.0 | 6-gate stakeholder reply agent over Customer Perception's 11K-ticket archive | S-A4 |
| Autonomous data analyst | (internal) | 9-stage gated pipeline publishing analyses on a 740K-panelist dataset | S-A3 |
| MCP servers | (internal) | 3 MCP servers, 24+ tools, stdio, over 43-table BigQuery | S-A5 |
| Hybrid orchestrator | (internal) | Cube.js semantic-layer agent + context-engineered agent + reconciling orchestrator | S-A7 |
| Context layer + MCP | V2 / Wibey skill | Reusable substrate under every Walmart analytics agent I've shipped | S-A8 |
| Productized Wibey skills | cp-analytics, Simple CP Interaction | First-of-kind productized AI skills across Walmart Data Ventures | S-A2 |
| ML classification pipeline | (internal) | 4-layer, 7,327 LOC, mypy --strict, 131 pytest tests; 652K → 50 in 45s | S-A6 |

If asked for a link to any of these: "It's a Walmart-internal deployment, can't share the URL. The public-facing version of the same architecture is the NL-to-SQL Copilot above." Don't apologize for it. The internal scope is part of the work.

---

# Pre-interview demo checklist

The morning of any interview where a demo URL is on the resume:

- [ ] Open every URL on the resume. Confirm each loads.
- [ ] Run one real query end-to-end on the NL-to-SQL Copilot. Confirm it returns an answer (Cloud Run can cold-start cold).
- [ ] Confirm the GitHub profile's pinned repos still match what I'm claiming.
- [ ] If any link is broken, swap the resume contact block to remove it before the interview (don't ship a dead link).

---

# Demo gaps / what to build next

- **Wibey-style skill demo (public).** The "productized Wibey skills" story is strong, but there's no public artifact I can point to. Building one tiny public Claude Code skill — even a toy — would give every BCG-X-shaped role a clickable proof point that "I've authored Claude Code skills" is real.
- **MCP server demo (public).** Same logic. The MCP layer at Walmart is invisible. A small public MCP server (BigQuery wrapper, or a public-data wrapper) would make the platform claim concrete.
- **Hybrid orchestrator writeup (blog or repo).** The hybrid orchestrator is the most distinctive technical artifact I have and the hardest to explain cold. A 1-page writeup (architecture diagram + the 90-second story) would be the kind of thing recruiters and engineering leads pass around.
