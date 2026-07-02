# Application Answers — Obra Capital · AI Full Stack Developer

**Apply here:** https://www.obra.com/jobs/10007-ls3re-r69d4-yxlbw-ht5bk-tjetj-5aajb-lynbg-nmjy8-a52c5

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045
- LinkedIn: linkedin.com/in/kanu-madhok
- GitHub: github.com/kmadhok

## Why Obra Capital
The line in this JD that sold me is "we aren't looking for an AI researcher; we need someone who can ship real products around LLMs and make them genuinely useful to the people who depend on them every day." That's exactly the kind of engineer I am — everything I've built is an internal AI tool that a business team actually uses to make decisions, not a prototype. The core of the role — RAG pipelines over proprietary documents, complex SQL against relational data, a vector store for retrieval, and a clean interface that turns messy internal data into something an analyst or trader trusts — is the stack I work in daily, and the bar that matters here (accuracy and reliability on sensitive data) is the part I obsess over, because an agent that's confidently wrong on a P&L number is worse than no agent at all. Credit investing and the specific financial primitives — Mark-to-Market, Security Master — are new domains for me, and I'd be upfront about that; my track record is picking up complex business domains fast because I sit directly with the stakeholders and translate their ambiguity into working software. I'd also be straight that heavy production React is my lighter axis relative to my Python/RAG/SQL core — I've built front-ends at the Streamlit and Recharts level rather than owning a large React app — but end-to-end ownership from database to interface is how I already work. This would be an NYC relocation for me, and I'm treating that as real.

## Relevant project
The build that best shows I ship full-stack LLM products is a live text-to-SQL copilot I built and deployed on my own: a Streamlit front end over a Gemini 2.5 backend, with LangChain orchestrating RAG retrieval of similar historical queries by embedding similarity, live BigQuery execution, and an auto-visualization layer that picks the chart type from the result shape. It's publicly runnable — you type a natural-language question and get SQL, real results, and a chart back — and it's the same architectural pattern (grounded LLM + RAG + SQL + a usable interface) this role is asking for, just on a public schema instead of proprietary financial data. On the production-reliability side, at Walmart I shipped a RAG-backed agent on an MCP server over BigQuery with a FAISS + BM25 retrieval layer over 11,000 historical queries; it took 400+ recurring requests from 30-60 minutes each to under 10, is approved by Sr. Director and product leadership, and writes an auditable artifact at every step — which is the discipline you want when the output feeds people making money decisions. Between the deployed copilot and the production agent, I've built exactly the RAG-plus-SQL-plus-interface product Obra needs, and I care most about the part where the people who depend on it every day actually trust it.

<!-- No custom application questions visible on the posting. -->
