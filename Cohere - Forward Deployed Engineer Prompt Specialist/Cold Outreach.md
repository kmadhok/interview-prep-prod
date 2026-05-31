# Cold Outreach — Cohere, Forward Deployed Engineer, Prompt Specialist

_Drafted 2026-05-24. Cohere — Agentic Platform (North). Role posts in Toronto / Montreal / NYC / SF (hybrid). Kanu is Chicago-based — confirm location/relocation fit before sending. Do not send blind; review, then send._

## Role summary

FDE-shaped role on Cohere's **Agentic Platform / North** team — bridge between the North platform and enterprise customers (RBC, Dell, LG CNS) across finance, healthcare, telco. Five verbs: optimize prompts for Command, develop+evaluate custom tools, build core agents (OOTB) for North, build customer-tailored agents, partner with customers on quality/efficiency/accuracy metrics.

---

## Contacts

| Name | Title | LinkedIn | Email (inferred) | Confidence |
|------|-------|----------|------------------|------------|
| **Lauren Duvall** | Senior Talent Acquisition Partner, Cohere (Canada / Montreal) | https://www.linkedin.com/in/laurenjduvall/ | `lauren.duvall@cohere.com` · `lauren@cohere.com` · `lduvall@cohere.com` | Low (pattern unverified) |
| **Patrick Lewis** | Senior Director, Agentic AI, Cohere (London) — leads Retrieval-Augmentation, Tool-use & Agents | https://www.linkedin.com/in/patrick-s-h-lewis/ | `patrick@cohere.com` · `patrick.lewis@cohere.com` · `plewis@cohere.com` | Low (pattern unverified) |

**Email-pattern note.** Cohere's public email pattern is not verified from prior Kanu correspondence. Cohere employees in public engineering posts have used `first@cohere.com` (firstname-only), which is the best first guess for a small-ish AI lab — but try `first.last@cohere.com` and `flast@cohere.com` if the first attempt bounces. **Default channel is LinkedIn InMail** until an email is confirmed.

**Why these two:**

- **Lauren Duvall** — verified Cohere recruiter, started Feb 2026. Background: 6 years as Sr Manager TA at Slalom (consulting) recruiting engineering, data, sales — a familiar archetype profile. She's the right inbox for the application.
- **Patrick Lewis** — Sr Director of Agentic AI, the practice that owns this role. Best-known publicly as a co-author of the original RAG paper (Lewis et al., 2020). He almost certainly isn't the day-to-day HM (London; the role is hybrid NA-Canada), but he is the most senior visible owner of the agent/retrieval/tool-use surface the JD describes. A short note to him does double duty: signals direct interest in the team's actual technical work, and asks him to point to the real HM.

**HMs not surfaced.** The FDE lead in NA isn't publicly identifiable from a single LinkedIn pass. Andy Rueda is an FDE in NYC (likely peer/early team, not lead). Daniel Roseman is FDE Agentic Platform Enablement in London. If Patrick doesn't reply, second-best HM-adjacent pings would be Sunith Raj S. (Principal, AI Solutions, NYC) or John Weatherly (Head of Global Public Sector, Raleigh — wrong vertical but knows the org).

---

## Draft 1 — Recruiter (Lauren Duvall)

**Channel:** LinkedIn InMail (default — email pattern unverified)
**Subject:** Forward Deployed Engineer, Prompt Specialist (Agentic Platform) — quick note from Kanu Madhok

Hi Lauren,

I came across the Forward Deployed Engineer, Prompt Specialist role on the Agentic Platform team and it lined up unusually well with what I've been doing.

Quick background: I'm a Senior Data Analyst at Walmart Data Ventures, but the work is principal-level AI engineering — I ship production LLM agents end to end. The clearest examples: an autonomous Jira resolution agent (6-gate workflow, MCP-driven tool layer, golden-set eval per gate) that's closed 400+ data requests and cut turnaround from 30–60 min to under 10 min; and a text-to-SQL copilot over a 67-table BigQuery surface where I run the prompt iteration + eval loop against 23 golden-query tests. Before Walmart, I shipped a RAG application *into* a client's workflow at FTI Consulting — adopted in production, Best in Show at UChicago MSADS Capstone.

That trio — prompts, tool layer, eval, on real customer agents — is the role.

One question on logistics: I'm Chicago-based. Are any of the four locations (Toronto / Montreal / NYC / SF) open to relocation, or is on-site presence in one of those cities a hard requirement up front? Happy to discuss either way.

Would you have 15 minutes this week or next? I can send a resume + a live demo of the architecture (NL-to-SQL Copilot on GCP Cloud Run).

Best,
Kanu Madhok
madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok

---

## Draft 2 — Senior practice leader (Patrick Lewis)

**Channel:** LinkedIn InMail
**Subject:** FDE / Prompt Specialist on the Agentic Platform — and a note on tool-use evals

Hi Patrick,

I came across the Forward Deployed Engineer, Prompt Specialist opening on the Agentic Platform team and wanted to reach out directly — your work on retrieval-augmentation and tool-use is what made me look closer at the role. The original RAG paper sits behind half of what I've shipped in the last year.

Short version of my background: Senior Data Analyst at Walmart Data Ventures, but the work is end-to-end AI engineering — production LLM agents (autonomous Jira resolver over an 11K-ticket archive, autonomous data analyst on a 740K-panelist dataset, MCP-driven tool layer underneath), and the eval harnesses that gate them (golden-set per gate, deliberate HITL based on cost-of-error). Same shape of work the JD describes, smaller customer surface.

Two reasons I'm writing you instead of only the recruiter: (1) you'd know better than anyone who the right hiring manager is — happy to be pointed there. (2) if there's a 15-min slot to hear how the Agentic Platform team thinks about tool-use evals for enterprise customers, I'd value that conversation independent of the role.

Best,
Kanu Madhok
madhok.kanu@gmail.com · linkedin.com/in/kanu-madhok · github.com/kmadhok

---

## Notes

- **Send order:** Lauren first. Wait 5 business days. If silent, send Patrick.
- **Location is a real blocker.** Cohere lists four sites and "hybrid" — Chicago isn't one of them. Confirm with Lauren before deep prep. The recruiter email above raises it explicitly so the answer comes back fast rather than after a screen.
- **Cohere Health ≠ Cohere.** Several Cohere Health (healthcare prior-auth) employees showed up in LinkedIn searches; all excluded.
- **Email-pattern caveat.** Both addresses are inferred; if the first guess bounces, try the alternates. Default to InMail until one is confirmed working.
- **Demo URL** — same as on every recent outreach: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/
- **What's missing:** an actual NA-based FDE lead. Worth a Cohere employee search around "FDE lead" / "Solutions Architect lead" / "Agentic Platform lead" with a NA filter on a future pass if Lauren+Patrick both go silent.
