# 🏗️ Build Architectures — Reference (BCG X / Maan)

> **Use:** drill from this morning-of, out loud. During the round it's a SILENT side-tab anchor — glance to recover a box name, don't read off it. Maan can tell narration-from-memory from reciting-from-doc.
> **Discipline:** lead with **2 builds** (Jira + Analyst). NL-to-SQL is a tertiary live-demo only if asked. The other two are ONE-LINERS — never volunteer all five.
> **Frame every build:** what was broken → what I built → who uses it → how I know it works. Adoption bookends architecture, not the reverse.

---

## 🥇 LEAD #1 — Jira Resolution Agent (`jira-ticket-worker`)

**One-liner:** fully autonomous BDV ticket resolver — triage through CSV delivery, zero internal checkpoints, 10-retry self-healing.

**Numbers:** 400+ tickets since Jan '25 · 30-60 min → 10 min · ~17-60 workdays saved.

**Architecture (5-phase pipeline on the shared substrate):**
```
ticket → TRIAGE → UNDERSTAND → PLAN → EXECUTE → DELIVER → [my review] → Jira
         (solvable  (MCP: schema,  (numbered  (run SQL,    (CSVs +
          end-to-    joins, 2-3     SQL plan)  10-retry     synthesized
          end?)      similar past             self-heal)   response)
                     queries)
```
- **EXECUTE self-healing:** 3 retries SQL syntax · 2 timeouts · 3 zero-row → opens an **Investigation Branch** (states a hypothesis, runs a 5-min exploratory query, applies the learning).
- **Autonomy posture:** agent is fully autonomous; **my review sits OUTSIDE the loop** — *"autonomy sized for execution, my review for communication — two failure budgets, each sized to blast radius."*
- **Eval:** ① SQL vs join graph (52 nodes / 36 verified paths) ② intent vs 313 historical queries ③ provenance work log. *"Today I'm the gate; next → golden-set regression."*
- **The leverage close:** *"The intake bottleneck was what kept me from building anything else. Automating it funded the rest of the portfolio."*

---

## 🥈 LEAD #2 — Autonomous Data Analyst (`cp-analytics`)

**One-liner:** plain-English questions from PMs → reproducible, audited SQL analyses with charts + auto-generated follow-up hypotheses. Ships direct to users.

**Numbers:** 57 analyses powered · only AI skill in active business-team use in DV · Director + product approved.

**Architecture (pure orchestrator + sub-agents):**
```
question → ORCHESTRATOR (never runs Bash; only Read/Write/Task)
              │ dispatches each idea to an isolated sub-agent
              ▼
           SUB-AGENT (own context) → SQL via MCP → BigQuery → findings
              │
              ▼
           REFLECT score = Impact × Surprise × Gaps
              │  ≥4 → spawn a depth idea (IDEA-002 → -D1 → -D2)
              ▼
           cp-audit (6-layer validate) → cp-fix (remediate) → report
```
- **Why pure orchestrator:** context isolation (one idea's results don't pollute another) · autonomy (sub-agents avoid CLI safety prompts) · crash recovery (`session.json` resume).
- **SQL traceability = a contract:** every query must be fully-qualified, runnable, >50 chars — **violations block.** Every number traces to runnable SQL.
- **Posture contrast (the platform-thinking move):** *"Same substrate as the Jira agent — but validation sits INSIDE the loop here, because blast radius is low (the user's own next decision). Same substrate, different HITL posture, each sized to cost."*

---

## 🔻 TERTIARY — NL-to-SQL Copilot (live demo only if he asks "anything I can try?")
RAG over historical SQL → English-to-SQL against BigQuery. Has a live URL. **Don't volunteer** — it's the V1 that taught the adoption lesson; its real value lives on now as `cp_search_sql` inside the MCP.

## ▫️ ONE-LINERS — mention only if directly relevant, never lead
- **Hybrid orchestrator / self-growing semantic layer:** dual-backend (Cube.js + raw-SQL agent), reconciles with 0.5% tolerance, disagreements become labeled data for the semantic layer. Auto-improve loop *built but gated* behind an env flag — *"capability ready; deployment deliberately gated until the org trusts the loop."*
- **KPI monitor:** daily checks via the MCP, Slack alerts. Thin agent on the same substrate.

---

## 🧱 THE SHARED SUBSTRATE (the thing that makes it "platform," not "5 demos")
```
        CONTEXT LAYER (source of truth: schema, joins, business defs, join graph)
              │ exposed via
              ▼
            MCP (tools) ──► every agent above is THIN on top of this
```
- **The one-sentence thesis** — say this if he asks how the builds relate:
  *"Every system is a thin agent on one reusable substrate. The substrate is the asset; each agent is the next thin thing on top. That's the pattern I'd bring to AI Factory — build the reusable layer once, ship many tools on it."*
- Reserve (only if probed): 68 tables, 1,350+ cols · 5 daily drift validators (self-maintaining) · 7+ downstream consumers. **Pick 2-3 numbers MAX.**

---

## ⛔ Reminders
- Architecture is **proof**, adoption is the **point** — open and close on who uses it + what changed.
- Don't dump the substrate stats (steals the case clock Maan protects).
- If he says "draw it" → the shared-substrate diagram above, 6 boxes, 60 sec, narrate every line.
