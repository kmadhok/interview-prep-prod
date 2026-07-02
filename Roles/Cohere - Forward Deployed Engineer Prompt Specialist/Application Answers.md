# Application Answers — Cohere · Forward Deployed Engineer, Prompt Specialist

**Apply here:** https://jobs.ashbyhq.com/cohere/6745547c-cc72-466c-867c-a0539b04909b

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship not required.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why Cohere
This role lives at the intersection I'm most comfortable in — software engineering and ML, close to the customer, where the job is making a model and its tools actually perform against a metric someone cares about. Prompt optimization, tool development, and rigorous evaluation aren't separate skills for me; they're the loop I run when I ship an agent, and the eval half is where I'm strongest. I've built the "define quality, efficiency, and accuracy metrics with the customer, then tune against them" discipline the JD describes, rather than shipping prompts on vibes. The tool layer maps directly to work I already do — the agents I've built at Walmart run over MCP tool interfaces I designed and evaluated. North is the draw: building both the out-of-the-box core agents and the tailored per-customer ones, for finance/healthcare/telco customers where the bar is real. I'm at the upper end of the 0–5 year band, and I'd lean on "deployed agents in production" over "growth mindset" — though I have plenty of the latter too.

## Relevant project
The best evidence for the prompt-and-tool-and-eval loop is my self-service analytics agent over 67 BigQuery tables. The tool layer is deliberate — deterministic SQL rules and MCP interfaces the agent calls — and the evaluation is layered: eight deterministic rules that fire before any LLM call, a 23-case golden-query suite that grades on result-correctness rather than exact SQL, and a context-isolated validator plus devil's-advocate sub-agent that catch hallucinations the drafter would defend. That's what "rigorous evaluation to ensure alignment with customer objectives" looks like in practice. It's the only AI skill in active use by business teams on my team.

To show it works with a stranger asking real questions, I also deployed a live text-to-SQL copilot outside my day job: Gemini grounded on RAG over historical queries, live BigQuery execution, and auto-visualization. The whole point was grounding the model on prior examples so it anchors on real column names instead of inventing them — prompt and context engineering against a live schema. It's runnable mid-conversation: https://sql-rag-frontend-simple-481433773942.us-central1.run.app/
