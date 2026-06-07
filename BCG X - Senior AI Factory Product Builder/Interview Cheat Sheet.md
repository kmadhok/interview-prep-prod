# 🎯 Interview Cheat Sheet — BCG X / Maan Hani · Mon 6/1, 2 PM ET

> **GLANCE, don't READ.** Triggers + first-words only. If you're reading a sentence off this, you're too slow.
> **Case = whiteboard.** Only the 5-step spine helps you live. Do NOT read answers off this during the case.

---

## ⛔ 3 TICS TO KILL (the whole game)
1. Never **"I believe / I fundamentally"** → say **"the deciding factor was…"**
2. Lead with the **architectural reason**, not the convenience one.
3. Unsure? **Answer the question fully**, then branch. Don't flee to portfolio breadth.
- Say **"MCP"** (not MCPU) · **"every step/decision"** (not "every token")
- **Pause 3 sec** before answering. Structured-slow beats fast-rambling.

---

## 🧩 CASE — say the spine OUT LOUD at the start
**CLARIFY → FRAME → PRIORITIZE → SOLUTION → MEASURE**
1. **Clarify** — restate + 2-3 *vital* Qs only (does the answer change my design?)
2. **Frame** — draw a tree/2×2, narrate it
3. **Prioritize** — pick highest-leverage branch, say *why* (size × adoption-safety)
4. **Solution** — what / who uses it / data / failure modes
5. **Measure** — $ / hrs / adoption % ← **NEVER leave empty. He WILL notice.**

**2 moves that win:**
- ✂️ **SUBTRACT** — name what you'd CUT/KILL, not just build
- 🔁 **Adoption mechanism** — "2-team pilot → 30% weekly-active gate → scale"

**Whiteboard layout:** problem top-left · 5 steps down left edge · tree center · solution right · **metrics bottom** · NARRATE every line.

---

## 🗣️ BEHAVIORAL
**TMAY (60 sec, real):** Sr Data Analyst, Walmart Data Ventures, point-of-contact for ~30 → intake outgrew one person → started building → Jira agent (400+ tickets), autonomous analyst, semantic layer → *what pulls me to AI Factory: building AI tools consultants actually adopt.*

**Why BCG X:** the work I already do — biz/tech generalist, end-to-end, first-principles — at the scope it was sized for.

**Failure → V1 RAG app:** built a frontend nobody used → *"first instinct was make the model better; blocker was the surface, not the system"* → rebuilt as context layer + MCP into the tool they already used → **don't build a destination, embed in the workflow.**

---

## 🔧 TECHNICAL — every answer ends on a gate / abstain / metric

**Jira agent (lead):** 400+ tickets since Jan '25 · 30-60 min → 10 min · ~17-60 workdays saved. Context layer + agent + traceable work log.

**Eval ("how do you know it works"):** ① structural — SQL vs **join graph (52 nodes, 36 verified paths)** ② intent — vs 313 historical queries ③ provenance. *"Today I'm the gate; next version → golden-set regression."*

**Failure budgets line:** *"Agent autonomy sized for execution, my review for communication — two budgets, each sized to blast radius."*

**Abstain ("what if unsure"):** complexity triage → gather context via MCP → **grounded**: can only cite data the SQL returned → **abstains**, returns "insufficient data," never a wrong number.

**Agent vs pipeline:** *"Agent where input varies, deterministic where I can verify."* Deterministic tree = if-else explosion over unstructured tickets. Proof: **separate verifier agent** runs SQL, checks deliverable numbers = queried data.

**MCP vs tool:** *"MCP when the capability is reusable across agents + worth a stable contract."* My DB layer = MCP because every agent talks to it the same way → build once.

**What's next:** automate the head, gate the tail — deterministic sub-flow per common theme → gate 100% → ~30%, embed in Jira for self-serve.

**Same substrate, diff posture:** Jira = human *outside* loop (high blast radius); analyst = validation *inside* (low). One substrate, postures sized to cost.

---

## 🏗️ ARCHITECTURE (draw 6 boxes, 60 sec, narrate)
`context layer → agent/router → MCP → BigQuery → verifier → work log`
1. Context layer = the asset (schema/joins/defs, survives between calls)
2. Agent = triage 3. MCP = reach context (14 tools, *reserve*) 4. Execute SQL 5. Verifier = numbers match queried data 6. Work log = provenance + my gate
**Reserve only if probed:** drift validators (self-maintaining) · `cp_generate_validated_sql` · pick 2-3 numbers MAX (68 tables, 7+ consumers, 57 analyses).

---

## ❓ QUESTIONS FOR MAAN (pick 2-3)
1. How does AI Factory measure "a tool is working" — adoption, time saved, something else?
2. Astronomy → LinkedIn → BCG: hardest part of translating technical rigor into a consulting org?
3. An AI Factory pattern you've shipped that more consultants would use if they knew about it?

---

## ⏱️ TIME (45 min) — if anything overruns, protect the CASE
TMAY ~3 · behavioral ~7 · technical ~12 · **case ~18-20** · your Qs ~3-5

## ✅ Day-of
Zoom 5 min early · 5-step spine out loud at case start · open on the *business problem* not architecture · *thank-you to Maan + Ganna within 24h*
