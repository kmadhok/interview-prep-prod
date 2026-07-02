# Application Answers — PwC · US Tech, AI Evaluation Engineer (QA), Senior Associate

**Apply here:** https://jobs.us.pwc.com/job/tampa/us-tech-ai-evaluation-engineer-qa-senior-associate/932/90837388896

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why PwC
This role is about making GenAI agents trustworthy enough to ship to clients, and that's the exact problem I spend most of my time on. The JD leads with automated testing, governance controls, and executing LLM evaluation frameworks against defined metrics — I've built all three into production agents at Walmart, not as an afterthought but as the gate that decides whether an answer ships. I like that PwC is putting an eval engineer between the agent and the client instead of trusting the model's output; that's the maturity signal I look for. The People Tech & AI framing also fits how I actually work — I've spent the last year translating ambiguous stakeholder questions into agent-ready specs with product and data-science partners, which is most of what "AI-enabled client solutions" comes down to. One honest gap: I haven't worked directly with Power Automate, though the RPA-style automation patterns behind it are familiar and I'd ramp fast.

## Relevant project
The closest match is a self-service analytics agent I built over 67 BigQuery tables — it's the only AI skill currently in active use by business teams on Walmart Data Ventures, and it's essentially a testable, governed agent. The eval stack is three layers ordered cheapest-to-most-expensive: 8 deterministic SQL rules that fire before any LLM call (no SELECT *, every join needs a key, no cross-table aggregation without a date filter), a 23-case golden-query suite where the agent passes when its result matches known-good output even if the SQL varies, and a context-isolated Validator plus Devil's Advocate sub-agent that don't share the drafter's context window so they catch hallucinated columns the drafter would defend. The gate to ship is: passes deterministic rules, passes the relevant golden case, and both reviewers clear it — otherwise it escalates instead of answering.

I also run a production Jira ticket-resolution agent that leans on the same discipline from the QA side: every gate writes a permanent work-log artifact (the SQL it considered, the table it picked, the join it made), which is both the audit trail and the eval substrate, plus a 10-retry self-healing execution budget that diagnoses and retries a failed query before escalating. The failure mode I design against is confident-wrong — clean SQL over a stale flag — which is exactly what process-level checks catch that observability alone misses.
