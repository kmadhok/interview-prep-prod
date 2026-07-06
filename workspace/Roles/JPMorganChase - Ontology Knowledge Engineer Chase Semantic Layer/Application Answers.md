# Application Answers — JPMorganChase · Ontology / Knowledge Engineer — Chase Semantic Layer

**Apply here:** https://www.linkedin.com/jobs/view/4421295461

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why JPMorganChase
The part of this role that maps directly to what I already do is the semantic layer — building the shared vocabulary that makes data mean the same thing across use cases, so downstream analytics and AI can trust it. At Walmart Data Ventures I own the semantic definitions that sit between a 67-table platform and the business teams asking questions of it, and the recurring problem is exactly the one this role exists to solve: the same concept gets modeled three different ways until someone curates a single authoritative representation. I also spend a lot of my time on the translation piece the JD calls out — turning ambiguous business requirements into formal, technically rigorous definitions that a non-technical stakeholder can still read and agree with. This is a foundational-capability role that underpins enterprise AI and governance rather than a single dashboard, and that leverage is what I want to work on next. I'd be relocating for it, and I'm treating it as a real move, not a maybe.

## Relevant project
I built and shipped a hybrid orchestrator at Walmart that runs every business question through both a CubeJS semantic-layer skill and a context-engineered analytics agent in parallel, then turns the disagreement between them into the signal. When the two outputs match, it ships; when they don't, it reasons about why — is the semantic-layer definition stale, is the agent hallucinating a join, or is the question itself ambiguous — and every discrepancy feeds back into refining the semantic-layer definitions over time. That is the same governance loop this role describes: the layer gets smarter and more internally consistent without anyone hand-authoring every definition. Underneath it, the analytics agent itself is a sub-agent flow (Context Researcher, SQL Drafter, Validator, Devil's Advocate) over 67 BigQuery tables, with 8 deterministic structural rules and a 23-case golden suite as the validation gate — it's currently the only AI skill in active use by business teams on Data Ventures, and it's the piece that taught me how much downstream trust depends on the semantic definitions being correct at the source.

<!-- No custom application questions visible on the posting. -->
