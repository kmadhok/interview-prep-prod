





# Live Reps Question Bank

Role: Walmart Principal Software Engineer - Agent Builder

Use this for out-loud practice. Do not silently read these. Pick a question, answer under time pressure, then critique the answer before moving on.

## How to Practice

Behavioral and role-fit reps:
- Answer in 90 seconds.
- Use this shape: situation, action, result, principal-level takeaway.
- Self-score immediately: was the business bottleneck clear, was your action specific, was the result measurable, and did you sound like a peer?

Technical reps:
- Answer in 2-4 minutes.
- Lead with the user/business problem before architecture.
- Mention guardrails, evals, observability, and rollout. Those are the principal-level signals.

System-design reps:
- Answer in 8-12 minutes.
- Do not start with tools. Start with the workflow and decision risk.
- Use the scaffold below every time.

## System Design Answer Scaffold

1. Clarify the workflow.
   - Who is the user?
   - What decision or task are they trying to complete?
   - What is the current bottleneck?
   - What is the cost of being wrong?

2. Define success.
   - Time saved.
   - Cost avoided.
   - Sales lift or conversion improvement.
   - Error reduction.
   - Adoption by non-technical users.

3. Decide whether this should be an agent.
   - Use deterministic automation when the rules are stable.
   - Use an LLM when the inputs are messy, ambiguous, language-heavy, or require synthesis.
   - Use human-in-the-loop when the action is high-impact or hard to reverse.

4. Sketch the architecture.
   - Intake layer: chat, form, ticket, event trigger, webhook, schedule.
   - Context layer: source systems, docs, policies, historical cases, metrics.
   - Reasoning layer: planner, classifier, specialist sub-agents, deterministic rules.
   - Tool layer: APIs, SQL, workflow actions, notifications, approvals.
   - Output layer: recommendation, draft action, explanation, audit trail.

5. Add guardrails.
   - Tool allowlist.
   - Strict schemas.
   - Permission checks.
   - Validation against source systems.
   - Confidence thresholds.
   - Human approval for irreversible actions.
   - Retry budgets and stop conditions.

6. Evaluate and observe.
   - Offline golden cases.
   - Historical replay.
   - Precision/recall for triage.
   - Acceptance rate by users.
   - Override rate.
   - Escalation rate.
   - Cost, latency, failure mode dashboards.

7. Roll out.
   - Start as recommendation-only.
   - Shadow current workflow.
   - Pilot with one category/team.
   - Expand after measurable trust.
   - Automate only low-risk actions first.

## Fast Warmups

1. Tell me about yourself.
2. Why this Agent Builder role?
3. Why Walmart, why this team, why now?
4. You are already doing agent work in Data Ventures. Why move?
5. What did you ship in the last 90 days?
6. What is the simplest way to explain your Data Ventures agent to a non-technical executive?
7. What is the one sentence version of your career narrative?
8. What should this panel remember about you after the interview?

## Behavioral Reps

1. Tell me about a time you owned a problem end to end with no clear support.
2. Tell me about a time you challenged a senior stakeholder's preferred direction.
3. Tell me about a time you built something that users actually adopted.
4. Tell me about a time you simplified an overcomplicated process.
5. Tell me about a time you failed.
6. Tell me about something you built that did not work at first.
7. Tell me about a time you killed or replaced your own idea.
8. Tell me about a time you had to influence non-technical stakeholders.
9. Tell me about a time ambiguity was high and you had to move anyway.
10. Tell me about a time you disagreed with a product or business partner.
11. Tell me about a time you had to make a tradeoff between speed and correctness.
12. Tell me about a time you had to debug a production issue.
13. Tell me about a time your first architecture was too complex.
14. Tell me about a time you earned trust from a skeptical stakeholder.
15. Tell me about a time you had to communicate a technical limitation clearly.
16. Tell me about a time you improved a system after it was already working.
17. Tell me about a time you had to operate without perfect metrics.
18. Tell me about a time you automated yourself out of a repeated workflow.
19. Tell me about a time you made a decision with incomplete data.
20. Tell me about a time you had to change your mind.

## Technical and Agent Design Reps

1. Describe the Data Ventures analytics agent architecture.
2. Why did you use sub-agents instead of one agent with tools?
3. How do you evaluate whether an agent is working?
4. How do you prevent hallucinated SQL or bad actions?
5. What are your production guardrails?
6. When would you not use an LLM?
7. How do you debug an agent regression?
8. What observability would you want in an agent-building platform?
9. What is the difference between a workflow and an agent?
10. What is the difference between prompt engineering and context engineering?
11. How do you choose between BM25, dense retrieval, and hybrid retrieval?
12. How do you decide when to add a reranker?
13. How do you choose between Claude, Gemini, and OpenAI?
14. How do you design a golden-query eval set?
15. What makes an agent safe enough for production?
16. What failure modes worry you most in multi-agent systems?
17. How do you keep agent latency acceptable?
18. How would you control cost in a high-volume agent?
19. How would you handle tool-call loops?
20. How would you design memory for an enterprise agent?

## Principal-Level Reps

1. What makes your work principal-level versus senior engineer-level?
2. If you joined, what mechanism would you put in place so the second agent ships faster than the first?
3. How would you decide which agent use case to build first?
4. How would you balance speed with safety?
5. How do you measure sales growth, cost savings, or time savings when causality is messy?
6. What would your first 30/60/90 days look like?
7. What platform primitives should every internal agent have?
8. How would you make Agent Builder usable by non-technical builders?
9. What would you push back on if leadership asked for the wrong agent?
10. What technical debt are you willing to accept in v1, and what debt is unacceptable?
11. How would you create engineering leverage beyond your own output?
12. How would you define an agent template library?
13. How would you decide when a one-off agent should become a platform capability?
14. How would you avoid building a demo factory?
15. What would you standardize across agent builds?
16. What would you intentionally leave flexible?
17. How would you make non-technical builders successful without letting them create unsafe automations?
18. How would you partner with merchandising and supply-chain leaders?
19. How would you communicate agent risk to executives?
20. How would you prove the team is working after 90 days?

## Curveballs

1. What concerns do you have about this role?
2. What do you not know yet about merchandising or supply chain?
3. Are you willing to relocate to Bentonville?
4. Have you talked to your current manager?
5. Why should we hire you over someone already in supply chain engineering?
6. Your title is Senior Data Analyst. Why are you ready for Principal Software Engineer?
7. What if your agent gives the wrong recommendation and it costs money?
8. How would you handle a stakeholder who wants full autonomy before the system is ready?
9. What if business users do not adopt the agent?
10. What if the low-code platform cannot express the architecture you want?
11. What if a deterministic system would solve the problem better than an LLM?
12. What if legal, compliance, or security blocks your preferred design?
13. What if the business wants ten agents and you can only build two?
14. What would make you say no to a use case?
15. What is a weakness in your background for this role?
16. What would your current manager say you need to improve?
17. What is the biggest mistake teams make with internal AI agents?
18. What if your evals pass but users still do not trust the answer?
19. What if the data sources are incomplete or stale?
20. What if two agents disagree?

## Panelist-Specific Reps

Navin Kasa:
- How would you decide which use case is worth building first?
- How would you turn Agent Builder from a set of tools into a scalable platform?
- What would you ship in the first 90 days if the domain is still unfamiliar?
- What business metric would you use before sales or cost savings move?
- What do you think is the hardest product risk in agent building?

Nathan Oswalt:
- Walk me through a debugging session for an agent failure.
- How would you justify agent investment with an ROI mindset?
- How do you think about automation when the real world is messy?
- How would you partner with operators who do not care about LLMs?
- How do you decide what should be autonomous versus reviewed?

Michael Ferrell:
- How would you make a non-technical business user productive with Agent Builder?
- How would you keep the platform simple without making it too limited?
- Tell me about messy real-world data you had to automate around.
- What did you build that enabled others instead of just serving them?
- How would you teach someone to think in terms of agents?

## System Design Prompts

Use the scaffold above. Do not jump directly to "I would use an LLM." First define the workflow, risk, metrics, and rollout.

### 1. Inventory Exception Handling Agent

Prompt:
Design an agent that helps supply-chain or store operators identify and resolve inventory exceptions, such as stockouts, phantom inventory, unexpected demand spikes, or replenishment mismatches.

What to cover:
- What exception types you would start with.
- How the agent ingests events and context.
- How it distinguishes known deterministic fixes from ambiguous cases.
- What tools it can call.
- What actions require human approval.
- How you measure business impact.

Strong answer signals:
- Start recommendation-only.
- Prioritize high-volume, reversible workflows.
- Use source-of-truth checks before recommending action.
- Track override rate and false-positive rate.
- Do not claim the agent can fix inventory autonomously on day one.

### 2. Vendor Onboarding Agent

Prompt:
Design an agent that helps new suppliers complete onboarding faster by guiding them through documents, requirements, missing fields, policy questions, and status updates.

What to cover:
- User groups: supplier, merchant, compliance, internal support.
- Required data sources: policies, forms, supplier profile, ticket history, onboarding status.
- How to prevent incorrect compliance guidance.
- How to escalate edge cases.
- How to measure time saved and supplier satisfaction.

Strong answer signals:
- Separate policy explanation from approval decisions.
- Use retrieval with citations to policy sources.
- Keep a full audit trail.
- Automate reminders and status checks before automating approvals.
- Build templates for repeat supplier categories.

### 3. Merchandising Price-Change Review Agent

Prompt:
Design an agent that reviews proposed price changes and helps merchants understand expected impact, risks, competitor context, inventory implications, and approval readiness.

What to cover:
- Inputs: proposed price, item, category, margin, demand, inventory, competitor data, historical elasticity.
- Outputs: recommendation, rationale, risk flags, questions for merchant.
- Guardrails around price recommendations.
- Human-in-the-loop approval.
- Evaluation against historical decisions.

Strong answer signals:
- Treat this as decision support, not autonomous pricing at first.
- Separate analysis from final authority.
- Use deterministic calculations for margin and thresholds.
- Use LLM for explanation, synthesis, and exception reasoning.
- Track recommendation acceptance and post-change outcomes.

### 4. Supplier Chargeback Dispute Triage Agent

Prompt:
Design an agent that triages supplier chargeback disputes and routes them to the right resolution path.

What to cover:
- Intake from tickets or portal messages.
- Retrieval over policy, contracts, prior disputes, shipment data, and transaction records.
- Classification into common dispute types.
- Evidence packet generation.
- Escalation for high-dollar or ambiguous disputes.

Strong answer signals:
- Start with triage and evidence assembly, not final adjudication.
- Use confidence thresholds.
- Use structured output so downstream workflows can consume the result.
- Measure time to resolution, routing accuracy, and rework rate.

### 5. Store Associate Task Assistant

Prompt:
Design an agent that helps store associates answer operational questions and complete routine tasks faster during a shift.

What to cover:
- Mobile-first or handheld interface.
- Permission-aware answers.
- Retrieval over store SOPs, item data, inventory, schedules, and local context.
- Escalation to manager or support.
- Offline or degraded-mode behavior.

Strong answer signals:
- Keep answers short and action-oriented.
- Avoid asking associates to parse long generated text.
- Ground answers in store-specific data.
- Track task completion and associate feedback.

### 6. Merchandising Assortment Review Agent

Prompt:
Design an agent that helps merchants review assortment performance and identify which items to keep, expand, substitute, or discontinue.

What to cover:
- Inputs: sales, margin, inventory, returns, customer behavior, category strategy, seasonality.
- How to explain tradeoffs.
- What decisions are too risky to automate.
- How to compare agent recommendations with historical merchant decisions.
- How to support scenario analysis.

Strong answer signals:
- Use deterministic metric computation.
- Use LLM for narrative synthesis and surfacing hypotheses.
- Provide confidence and caveats.
- Make recommendations reviewable, not opaque.

### 7. Forecast Exception Explanation Agent

Prompt:
Design an agent that explains why a demand forecast changed and what a planner should do next.

What to cover:
- Forecast inputs and deltas.
- External factors like weather, events, promotions, seasonality, and supply constraints.
- Explanation quality.
- Tool calls to source data.
- How to prevent confident but wrong causal claims.

Strong answer signals:
- Distinguish correlation from causation.
- Use "possible drivers" rather than unsupported certainty.
- Link every explanation to source evidence.
- Evaluate with historical forecast-change cases.

### 8. Agent Builder Template Platform

Prompt:
Design the internal platform primitives that let non-technical Walmart teams build useful agents safely.

What to cover:
- Templates: triage agent, alerting agent, research assistant, workflow assistant.
- Required configuration: tools, data sources, permissions, cadence, escalation path.
- Built-in evals and observability.
- Governance and approval.
- How to prevent unsafe or unmaintainable agents.

Strong answer signals:
- Opinionated templates beat blank-canvas builders.
- Natural language where flexible, structured fields where safety matters.
- Every agent needs owner, eval set, tool allowlist, logs, and kill switch.
- Platform success is measured by safe reuse, not number of agents created.

### 9. Agent Regression Monitoring System

Prompt:
Design a monitoring system that detects when an enterprise agent has regressed after a prompt, model, tool, or data-source change.

What to cover:
- Offline regression suite.
- Canary traffic.
- Online metrics.
- Failure clustering.
- Alerting and rollback.

Strong answer signals:
- Version prompts, tools, models, retrieval indexes, and eval sets.
- Run golden cases on every change.
- Replay historical traffic where possible.
- Monitor silent failures, not just crashes.
- Keep rollback boring and fast.

### 10. Multi-Agent Reconciliation System

Prompt:
Design a system where two different agents or backends produce answers to the same business question, then a supervisor reconciles disagreements.

What to cover:
- When parallel systems are worth the cost.
- How to compare outputs.
- How to handle disagreement.
- How to use disagreement to improve the system.
- How to keep latency and cost acceptable.

Strong answer signals:
- Use parallelism only where errors are costly or sources disagree.
- Compare structured intermediate outputs, not just final prose.
- Make disagreement visible to users.
- Feed discrepancies into semantic-layer or retrieval improvements.

## Mini Drills

Use these when you only have 15 minutes.

1. Draw your Data Ventures agent from memory in 3 minutes.
2. Explain why the Validator and Devil's Advocate are separate in 90 seconds.
3. Give your "when not to use an LLM" answer in 60 seconds.
4. Give your failure story in 90 seconds.
5. Give your relocation answer in 30 seconds.
6. Give your "Senior Data Analyst to Principal Software Engineer" answer in 90 seconds.
7. Give your first 90 days answer in 90 seconds.
8. Give your non-technical builder platform answer in 2 minutes.

## Self-Score Rubric

Score each answer 1-5.

- 5: Specific, concise, business-first, technically credible, includes tradeoffs and metrics.
- 4: Clear and credible, but missing one of metrics, tradeoffs, or rollout.
- 3: Understandable but generic or too tool-heavy.
- 2: Rambling, too abstract, or unclear result.
- 1: Sounds rehearsed, evasive, or not principal-level.

If an answer scores below 4, redo it immediately. Do not move on until the second attempt is cleaner.
