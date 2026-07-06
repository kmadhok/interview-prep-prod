# Application Answers — Anduril Industries · Senior Analytics Engineer, People Data

**Apply here:** https://www.linkedin.com/jobs/view/4419580375 (JD source; also on Anduril careers — search "Analytics Engineer, People Data")

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number field: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. (Sponsorship required: No.)
- Notice period: 2 weeks from offer acceptance.
- Phone / LinkedIn / GitHub: 952-303-1045 / linkedin.com/in/kanu-madhok / github.com/kmadhok

## Why Anduril
The core of this role — owning the full lifecycle from ingesting messy source data to clean, governed, analytics-ready datasets, and doing it with engineering discipline like version control, testing, and CI/CD — is what I do day to day. At Walmart I've built and automated ETL/ELT on a large BigQuery platform with structural data-quality enforcement and coverage checks, and I partner constantly with non-technical stakeholders to turn a vague analytical ask into a reliable dataset, which is the People-Analyst-and-HRBP partnership this JD describes. My SQL, Python, cloud-warehouse, dbt, and Airflow experience maps directly; the stack-specific tools like SQLMesh, Iceberg, and Flyte, plus the HRIS data domain, are ramp rather than a rebuild. I'd rather be candid than oversell there — I'd be strong on the pipeline-and-modeling core from day one and coming up to speed on the people-data-specific stack.

## Relevant project
I replaced ~20 recruitment workflows we used to run by hand 1–2× a week with end-to-end automation on a 68-table BigQuery platform — a 3-hour task now takes about 3 minutes of setup, I've recruited 280,000+ panelists across 29 categories, and the duplicate count is zero. The pipelines use stratified sampling to hit category quotas at the SQL layer, and zero-duplicate enforcement is structural — every recruit checks a persistent allocations table before assignment, so deduplication is a write-time guarantee, not a downstream cleanup. Every run also emits a coverage report against the 29-category targets and flags any category that undershoots before the recruit goes live — the data-quality-and-monitoring discipline this role is built around.

I also shipped a self-service analytics agent over 67 BigQuery tables that's the only AI skill currently in active use by business teams on Walmart Data Ventures. What's relevant here is the eval substrate: 8 deterministic SQL rules that enforce structural correctness (no SELECT *, every join needs a key, no cross-table aggregation without a date filter), a 23-case golden-query regression suite, and validation before anything ships — the version-control-and-testing rigor the JD asks an analytics engineer to bring to data models.
