# AI & Data Engineer

**Company:** Tern
**Locations:** United States (Remote)
**Compensation:** $175K – $200K/yr + equity + benefits
**Source:** https://www.linkedin.com/jobs/view/4420765542/ (LinkedIn job_id 4420765542; saved-jobs drip run 2026-07-02)

---

## About Tern

Tern is a venture-backed software company on a mission to reshape the $127B travel agency industry by giving power back to the entrepreneurs who built it. Nearly 98% of travel agencies are small businesses that have been chronically underserved by technology. Tern's platform helps travel advisors run more efficient, professional, and profitable operations — the modern infrastructure they need to lead the next chapter of travel.

## About the Role

This role builds and owns the AI and data systems at the core of Tern's product. You'll set the standard on evals, pipeline reliability, and advisor reporting on a small team where the scope is real and the ownership is yours.

AI is becoming central to Tern's product, and the quality of those AI features lives or dies on the data behind them. You'll be a **senior builder on the data team, working closely with the Data / AI Lead**, and your north star is making Tern's AI features **trustworthy**. That's an engineering problem — you solve it by building the systems those features run on, the **eval harnesses** that tell us whether they're actually good, and the **monitoring** that catches quality and drift in production.

That work rests on a data foundation you'll also own. Tern is the system of record for every advisor and agency on the platform, so its data does double duty: feeding the AI features and powering the reporting advisors and agency owners rely on to run their businesses. You own that data end to end — from the pipelines that move it through to the reporting built on top of it.

## Engineering Standards

- **Ship regularly.** Every engineering pair ships a working, tested feature every week. Fast and good are not in tension. Testing is part of the build.
- **We own our code and how users experience it.** Watch what we ship in production, stay close to support, monitoring, and user feedback, and own fixes end to end.
- **Make the people around us faster and better** — code and design reviews that teach, clear written work, unblocking colleagues quickly.
- **Every team is an AI team.** We use AI fluently in daily work — design review, test generation, debugging. We run **Claude Code with a deep library of custom skills and agents, unlimited token usage**, and we're actively building **agentic and MCP-based tooling** on top of our own systems.

## Our Stack

Ruby on Rails application with a Hotwire front end, backed by a Postgres database, hosted on Heroku (migrating to Google Cloud Platform). Data flows into **BigQuery**, modeled with **dbt**, with reporting in **ThoughtSpot** and **Hex**. Claude Code is part of daily development. You don't need to have used every piece, but you should be fluent enough to be productive quickly and excited to work this way.

## Main Responsibilities — What You'll Do

- Build and ship the systems behind Tern's AI features: the data infrastructure, services, and agentic tooling they run on. The output is **working software in production, not decks or recommendations**.
- Build the **evaluation systems** that answer whether an AI feature is good enough to ship and good enough to keep — eval harnesses, datasets, and production monitoring that run as software, not one-off analyses. Where no quality bar exists yet, build the thing that sets it.
- Own **data quality** as a first-class concern across ingestion, modeling, and reporting. Catch problems before they reach a model, a dashboard, or a user. Fix them end to end.
- Build and maintain the **ETL systems** that move and shape data from the application and third-party sources. Keep them reliable as volume grows.
- Work alongside product squads to build the **reporting** that gives advisors and agency owners real visibility into how their business is performing.
- Make the people around you faster and better. Share context early and write clearly so others can build on your work.

## What We're Looking For — What You Have

- **Production AI/ML experience (the must-have):** You've built and shipped AI and/or ML systems that real users depended on in production, and you owned what happened after launch — watching quality, debugging bad outputs, making the system better over time. Matters more than any specific tool or title.
- **Evals as engineering:** You treat evaluation as something you build, not a report you write. A real point of view on what to measure, how to catch drift and regressions, and when a metric is lying to you — ideally from building evals for a production system.
- **Data pipeline and service ownership:** You've personally built and owned pipelines and services that move data from application sources into a warehouse. You know what breaks, when and why, and you own the fix.
- **High agency:** You've taken ambiguous, under-specified problems and driven them to a working outcome. You don't need a fully-scoped ticket to start.

### Bonus Points

- Experience with Ruby on Rails or working directly from an application database rather than just downstream data
- Hands-on experience with LLM evaluation and observability tooling
- Experience with MCP-based tooling or agentic data workflows

## Compensation

Compensation Range: **$175K – $200K**, plus equity and benefits package.

## How We Hire

- Interview is built to surface demonstrated execution; kept deliberately light rather than a long gauntlet.
- Resumes are screened for specific, verifiable things you shipped and the impact they had — not responsibilities or titles.
- They go deep on one or two things you personally built and shipped: the real story — the ambiguity, the dead ends, what broke, and how you owned the fix.
- A practical exercise that reflects the actual work, with AI tools available and expected.
- Throughout, they look for evidence that working with you made other engineers better.

## Notes for Kanu

- **Strong on-paper fit + no hard gates:** Remote-US, no clearance/citizenship/sponsorship language, no travel requirement. Comp $175–200K is at/above floor.
- **This JD is unusually eval-forward** — "evals as engineering," production monitoring, drift/regression catching are the *must-have*. Lead the resume and any walkthrough with the golden-query/eval-harness and observability work (analytics agent eval + KPI-monitor observability).
- **Claude Code + custom skills/agents + MCP tooling is literally their daily stack** — Kanu's agent/MCP build story is a near-exact culture match; say so.
- Stack is BigQuery + dbt + Hex/ThoughtSpot (analytics-engineering flavored) with an RoR app DB as the source system. Ruby is a bonus, not required.
- Hiring contact on the posting: **Jack Bradmiller-Feld (Data @ Tern)** — 3rd-degree; relevant once this is Applied and outreach auto-stages.
- Small team (~42 employees, fast growth); "senior builder," high-agency, ships weekly. Ownership scope is real.
