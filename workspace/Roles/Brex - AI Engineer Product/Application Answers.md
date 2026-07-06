# Application Answers — Brex · AI Engineer, Product (Audit Agent)

**Apply here:** https://www.brex.com/careers/8606845002?gh_jid=8606845002

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required (No).
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why Brex
This is the exact problem I find most interesting right now: the agent reasons, but the product harness around it is what makes the reasoning trustworthy and operable. Building the Audit Agent's harness — the reviewer experience, the data contracts with the financial system of record, and the feedback loops that make the agent better over time — is the work I already do, just pointed at spend review instead of analytics. My whole approach to production agents is that a non-deterministic system needs a product and eval layer to compensate: deterministic rules underneath the model, a golden-set gate before anything ships, permanent audit artifacts at every step, and a human reviewer who can trust and act on the output. The backend-heavy split with a real UI minority fits how I build, and the traceability angle — an agent replacing manual review work where every decision has to be auditable — is squarely in my wheelhouse.

## Relevant project
I shipped a self-service analytics agent over 67 BigQuery tables as a sub-agent flow — Context Researcher, SQL Drafter, Validator, and a Devil's Advocate that challenges the output before it ships. There are 8 deterministic rules that fire before the LLM is ever trusted, then a 23-case golden-query eval suite, then human-in-the-loop review at rollout. It's currently the only AI skill in active use by business teams on Data Ventures. That layered harness — cheap deterministic checks, then eval, then a human gate — is exactly the pattern the Audit Agent needs.

I also built a production agent that resolves data-readiness tickets, where every gate writes a permanent work-log artifact — the query it considered, the table it picked, the join it made — so there's a full audit trail behind each answer. It took 400+ tickets from 30-60 minutes to under 10. For an audit-and-review product where traceability is the whole point, that write-an-artifact-at-every-step discipline is the part I'd bring on day one.
