# Application Answers — Cohere · Data Engineer, Data Foundations

**Apply here:** https://jobs.ashbyhq.com/cohere/9baccd88-c051-474f-bfe8-6867fca54cee

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope.
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship not required.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 · linkedin.com/in/kanu-madhok · github.com/kmadhok

## Why Cohere
The Data Foundations mandate — build the production data infrastructure that everything else on the AI side depends on — is the work I've been doing at Walmart, and it's the part I actually like. My stack lines up closely with what you're asking for: heavy Python and SQL, and the modern analytics stack you name (BigQuery, Airflow, dbt) is what I build on. I care about the same things this team does — end-to-end ownership where I run an implementation through to a real outcome rather than handing off a half-built pipeline, and turning messy, unstructured inputs into datasets people can actually trust. I'll be straight that my distributed-systems depth is a ramp area — I'm strong in PySpark but haven't run Beam or Flink at scale, and Kubernetes and Go are gaps — but large-scale data-processing design is squarely where I want to grow, and the "operating at the edge of what's known" framing is why Cohere in particular. The genuine-excitement-about-AI bar isn't a stretch; I follow the research and I build on frontier models daily.

## Relevant project
The clearest data-engineering proof point is the recruitment automation I built at Walmart on a 68-table BigQuery platform. It replaced ~20 manual workflows that ran 1–2 times a week, each taking about three hours, with end-to-end pipelines that now take ~3 minutes of setup. The interesting part is the correctness engineering: stratified sampling that enforces category quotas at the SQL layer across 29 categories, and zero-duplicate enforcement done as a write-time guarantee against a persistent allocations table rather than downstream cleanup. It's recruited 280,000+ panelists with a zero duplicate count, and every run emits a coverage report that flags under-filled categories before it goes live.

I also designed and shipped a self-service analytics agent over 67 BigQuery tables — the transformation-and-access layer on top of the raw data. It uses a sub-agent flow (context research, SQL drafting, validation, a devil's-advocate check) with eight deterministic SQL rules and a 23-case golden-query suite underneath the LLM, and it's currently the only AI skill in active use by business teams on Data Ventures. It's the closest thing I've built to "make foundational data legible to non-experts," which is what Data Foundations is ultimately for.
