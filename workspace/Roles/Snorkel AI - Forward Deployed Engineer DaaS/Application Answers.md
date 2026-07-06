# Application Answers — Snorkel AI · Forward Deployed Engineer, Data as a Service

**Apply here:** https://job-boards.greenhouse.io/snorkelai/jobs/5689470004

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Snorkel
The premise that meaningful AI starts with the data, not the model, is the belief I've been operating on in practice — the agents I've shipped are only as good as the eval data and quality gates underneath them, and that's where most of my engineering time actually goes. This role is end-to-end ownership of the AI data pipeline lifecycle: building evaluators, designing quality-measurement systems, validating LLM outputs, and packaging production-grade datasets — which is the exact discipline I've built into my Walmart agents, just pointed at internal analytics instead of client deliverables. I like that it's forward-deployed, at the intersection of data science, data engineering, and AI engineering, partnering directly with delivery teams and clients, because that customer-facing, own-the-whole-lifecycle motion is how I work best. And the founding-member framing for the technical DaaS team is a real draw — I'd rather help define the evaluation frameworks and delivery patterns than inherit them. On requirements: I clear the 4+ years, Python and SQL are core to me, and I've done real production validation of LLM systems; the one honest stretch is that my API-integration work has been internal-platform rather than a broad external-integration surface.

## Relevant project
The most relevant build is a self-service analytics agent I shipped over 67 BigQuery tables, and specifically its evaluation stack, which is exactly the evaluators-and-quality-measurement work this role centers on. It's three layers ordered cheapest-to-most-expensive: 8 deterministic SQL rules that fire before any LLM call, a 23-case golden-query suite where the agent passes when its result matches known-good output even if the SQL varies, and a context-isolated Validator plus Devil's Advocate sub-agent that don't share the drafter's context window so they catch hallucinated columns the drafter would defend. The gate to ship is all three clearing — otherwise it escalates instead of guessing. It's the only AI skill currently in active use by business teams on Walmart Data Ventures.

For the data-engineering-and-scale side, I also automated ~20 recruitment workflows on a 68-table BigQuery platform using stratified-sampling pipelines that recruited 280,000+ panelists across 29 categories with zero duplicates — dedup enforced as a write-time guarantee, not downstream cleanup — turning a recurring 3-hour manual task into ~3 minutes of setup. That's the packaging-clean-datasets-with-quality-assurance discipline the DaaS role asks for, done at real volume.
