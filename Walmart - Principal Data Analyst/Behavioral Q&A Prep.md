# Behavioral Q&A Prep — Walmart Principal Data Analyst (AI-Enabled Analytics)

**Round:** Fri, June 19, 2026 · behavioral + one end-to-end slide
**Panel:** Máximo Lau (Sr Mgr, Ecommerce Analytics — practitioner/people-manager lens) · Michael Hawkins (Director, Data & Analytics — AI-transformation/coaching lens) · Bashir Ghellali (unconfirmed)
**Companion:** `Slide Talk Track - Analytics Agent.md`

---

## How to read this panel

This is **not** the 5/29 coding panel. It's a behavioral round for a senior IC who's expected to be a *technical thought leader and coach*. Two things the JD weights that most candidates underplay — make sure they show up in your answers:

1. **Elevating the team** (coaching, reusable patterns, moving people off static reporting). Michael Hawkins' lens.
2. **Stakeholder translation under ambiguity** (vague business ask → scoped solution). Máximo's lens.

Lead answers with the business problem and your judgment calls, not the architecture. Keep numbers honest (don't upgrade "active use" to "org-wide").

---

## Your story inventory (what to reach for)

| Story | Use it for |
|---|---|
| **Analytics agent (A1)** — your slide | end-to-end ownership, eval rigor, adoption |
| **Jira agent (S-A4)** — leverage flywheel | biggest impact, built-before-asked, HITL judgment, bottleneck you spotted |
| **V1→V2 platform pivot (S-A8)** | failure, what you'd do differently, simplification, "adoption is a product problem" |
| **Hybrid orchestrator (S-A7)** | cross-functional (DS+Product+you), first-principles design, principal-level platform thinking |
| **Productized Wibey skills (S-A2)** | influence without authority, clearing a high org bar, first-of-kind |
| **Career narrative (S-CAREER)** | "why ready for principal," title-vs-work gap |

---

## Likely questions + answers

### 1. "Walk me through something you owned end-to-end." (your slide)
→ Use the **slide talk track**. Don't repeat the slide verbatim — narrate the judgment calls: framing the problem with stakeholders, why context-isolated validation, why you stayed the human gate at rollout.

### 2. "Tell me about your biggest impact / something you built before anyone asked."
→ **Jira agent (S-A4).**
> "I was the only one handling Customer Perception's Jira intake — data readiness, panelist lookups, response rates. Typical ticket 30–60 minutes, complex ones a full day, 400+ since January. Nobody asked me to fix it, but it was the bottleneck on everything else I wanted to build. So I built a 6-gate agent — triage, context retrieval over our 11K-ticket archive, plan, draft, BigQuery execute, validate. I deliberately kept myself as the human in the loop: the agent drafts, I review and post, stakeholders just see a normal Jira reply from me. Complex tickets went from a full day to 10–15 minutes. The real win was leverage — once intake was off my plate, I built the analytics agent, the KPI monitor, and the semantic-layer orchestrator on top of the same infrastructure. That one agent funded the rest of the portfolio."

*Follow-up "why not auto-post?"* → Cost of a wrong answer to a stakeholder is far higher than two minutes of my review. At scale I'd add confidence thresholds and auto-post the high-confidence cases.

### 3. "Tell me about a time you failed / what would you do differently."
→ **V1→V2 pivot (S-A8).**
> "I shipped a text-to-SQL app — frontend, English in, SQL out. Demoed it to leadership, it technically worked, and adoption stalled. The blocker wasn't the model, it was the surface — I'd asked people to leave the workflow they already lived in. So I stopped building an app and built a platform: I tore V1 into a reusable context layer plus an MCP and delivered it as a skill inside the tool people already use. That same context layer now powers four other agents. The lesson I carry: adoption is a product problem, not a technology problem. One failed app turned into N agents because the second time I got the abstraction right."

### 4. "Tell me about a weakly-defined / ambiguous problem you had to structure."
→ **Analytics agent framing** or **hybrid orchestrator (S-A7).** The hard part of the analytics agent wasn't the SQL:
> "The hardest part was that 'a right answer' wasn't defined. Business teams asked things in their own language; there were multiple correct queries for any one question. I sat with Product and Data Science to turn ambiguous asks into agent-ready specs and encoded the agreed answers as a 23-case golden set. That translation step *was* the work — the eval suite is just where it got written down."

### 5. "Tell me about working cross-functionally / with Data Science and Product."
→ **Hybrid orchestrator (S-A7).**
> "We had two text-to-data approaches in production — a Cube.js semantic layer that DS and Product co-owned, and my context-engineered agent — and no one knew which to trust per question. I built an orchestrator that runs both in parallel; agreement ships, disagreement gets flagged for Product review. We ran a three-way contract: DS owns the semantic layer, I own the agent and orchestrator, Product owns what the metrics mean and reviews disagreements. The disagreements became labeled data for new definitions — the semantic layer grows itself. I built the pipe; I deliberately didn't put myself in the seat of deciding which business metrics exist."

### 6. "How do you elevate the people around you / coach other analysts?" ⚠️ JD core — prep this
→ Best current evidence: **productized Wibey skills (S-A2)** + the reusable-pattern angle.
> "I was the first analyst on Data Ventures to ship official Wibey skills — they cleared the same Product + DS review any internal tool goes through, then distributed to other analysts. The point wasn't my own productivity; it was building patterns other analysts could pick up instead of re-solving the same problem. The reusable context layer and the golden-set eval harness are the same idea — I'd rather hand the team a substrate they extend than a one-off analysis they consume."
> ⚠️ **Gap to fill before 6/19:** you don't yet have a *direct person-to-person mentorship* story (someone you taught/unblocked by name). For a coaching-weighted JD with two people-managers on the panel, a concrete one would land harder than the platform framing. If you have one — onboarding a teammate, walking an analyst through an agent, a peer you unblocked — tell me and I'll draft it into the story bank.

### 7. "Why this role / why now?" (internal mobility)
→ **Career narrative (S-CAREER),** framed as a *move toward what you already do*.
> "My title is Senior Data Analyst, but the work has been principal-level AI engineering for a while — the text-to-SQL copilot, the Jira agent, the autonomous analyst, the orchestrator. This role is the first one I've seen that's scoped for exactly that: an IC who moves an analytics org from static reporting to AI-augmented analytics and coaches the team to do the same. I'm not trying to leave analytics — I'm trying to do this version of it with a mandate instead of doing it on the side of my desk."

### 8. "How do you communicate complex / technical work to non-technical stakeholders?"
→ Use the **HITL framing** from the Jira agent + the adoption framing from V1→V2.
> "I default to outcomes, not architecture. With the Jira agent, stakeholders never needed to know an agent existed — they got faster, well-supported answers in the workflow they already used. When I do explain the tech, I anchor it to the decision it changes: 'this is why you can trust the number,' not 'here's the retrieval stack.' The V1 failure taught me that — I'd over-indexed on the impressive demo instead of fitting their workflow."

### 9. "Tell me about a tradeoff between experimentation and pragmatism." (JD: "balance experimentation with pragmatism")
→ **Deterministic rules under the LLM** (analytics agent) is a clean one:
> "On the analytics agent, the pragmatic call was layering 8 deterministic SQL rules *under* the LLM. The LLM is flexible but inconsistent; deterministic checks catch the dumb structural failures for free, so I only spend expensive LLM-eval on the genuinely ambiguous cases. I didn't try to make the model do everything — I used the cheapest tool that could catch each class of error."

### 10. "Tell me about a time you influenced without authority."
→ **Productized Wibey skills (S-A2)** — cleared formal review as an analyst, distributed org-wide, first-of-kind.

---

## Questions to ask them (have 3–4 ready)

- "How does this team think about the line between the semantic layer and agent-based analytics today — is that a tension you're actively working through?" *(shows you know the real problem; great for Máximo / DS-adjacent.)*
- "What does 'good' look like for the coaching part of this role in the first six months — is it patterns and tooling, or more hands-on analyst enablement?" *(Michael Hawkins' lens; signals you take the uplift mandate seriously.)*
- "Where is the team furthest along vs. earliest in moving from static reporting to AI-augmented analytics?"
- "What's made previous AI-enablement efforts on the team stick or stall?" *(ties to your adoption-is-a-product-problem POV.)*

---

## Pre-interview checklist

- [ ] Fill the **mentorship/coaching gap** (Q6) — get one concrete person-to-person story into the story bank.
- [ ] Confirm Bashir Ghellali's role/team (ask recruiter or share LinkedIn) so all three are tailored.
- [ ] Build the actual slide from `Slide Talk Track - Analytics Agent.md`.
- [ ] Per standing feedback: confirm in writing with the recruiter exactly how the slide is presented (screen-share? sent ahead? time limit on the slide?).
- [ ] Drill the slide open + close cold; rehearse the 2.5-min track once out loud.
