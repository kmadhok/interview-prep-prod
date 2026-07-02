# Application Answers — BlackRock · Data Engineer, VP (Aladdin Financial Engineering)

**Apply here:** https://careers.blackrock.com/job/new-york/data-engineer-vice-president-aladdin-financial-engineering/45831/91621763888

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required (No).
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why BlackRock
The part of this role I keep coming back to is the line about leveraging AI for efficiency and agentic automation on top of the Advanced Data Analytics platform — that's exactly the work I do now. At Walmart Data Ventures I build the data curation and analytics layer and then put agents on top of it: an MCP server over our BigQuery platform, retrieval over thousands of historical queries, and automation that turns manual analyst workflows into unattended pipelines. The AFE mandate — Snowflake/Databricks, ETL and derived data, and generating investment intelligence for the Single Security space — maps cleanly onto that build-the-platform-then-automate-it pattern. I'll be honest that structured products are a domain I'd be ramping into rather than one I already know; what I bring is the data-engineering rigor and the agentic-automation instinct the team says it wants to apply there.

## Relevant project
I automated ~20 recruitment workflows at Walmart end-to-end on a 68-table BigQuery platform — stratified-sampling pipelines that recruited 280,000+ panelists across 29 categories with zero duplicates, enforced structurally at write time rather than cleaned up downstream. A recurring 3-hour task now takes about 3 minutes of setup and runs unattended. It's the closest thing I have to the AFE brief: large enterprise data, curation and quota logic at the SQL layer, and reliability treated as a first-class property.

I also built a production agent that resolves data-readiness tickets against that same platform. It's a 6-gate pipeline with an MCP server over BigQuery plus a FAISS + BM25 retrieval layer over 11,000 historical SQL queries, and it writes a permanent work-log artifact at every step so there's an audit trail. It took 400+ tickets from 30-60 minutes each to under 10, which is the "leverage AI for efficiency and agentic automation" idea made concrete.
