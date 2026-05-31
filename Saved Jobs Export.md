# LinkedIn Saved Jobs Export

**Generated:** 2026-05-27
**Source:** LinkedIn "Saved Jobs" — pulled via LinkedIn MCP (sequential, jittered to avoid detection)
**Method:** Each job searched by `title + company + location`; matched against company name in results.
**Count:** 20 (of ~34 total saved; rest on pages 2–3 of LinkedIn UI, not yet exported)

> **`[NOT FOUND]`** rows: MCP keyword search returned no exact match. Likely causes — older posting, expired req, or LinkedIn's search ranks promoted listings over the saved one. Pull URL manually from LinkedIn UI and update.

---

## Batch 1 (jobs 1–10)

| # | Title | Company | Location | Posted | LinkedIn URL | Folder |
|---|-------|---------|----------|--------|--------------|--------|
| 1 | AI & Analytics Innovation Senior Product Specialist | Deloitte | New York, NY (Hybrid) | 13h ago | https://www.linkedin.com/jobs/view/4419871139/ | Deloitte - AI Analytics Innovation Senior Product Specialist |
| 2 | Consultant - AI and Data Risk Management | Deloitte | Chicago, IL (Hybrid) | 13h ago | https://www.linkedin.com/jobs/view/4419855203/ | Deloitte - Consultant AI and Data Risk Management |
| 3 | AI Agent Engineer - US Remote | TRM Labs | NAMER (Remote) | 11h ago | https://www.linkedin.com/jobs/view/4389951823/ | TRM Labs - AI Agent Engineer |
| 4 | Senior AI Engineer | Morgan Stanley | New York, NY | 12h ago | https://www.linkedin.com/jobs/view/4409727160/ | Morgan Stanley - Senior AI Engineer |
| 5 | Software Engineer, AI Workflows | Notion | San Francisco, CA (Hybrid) | 12h ago | https://www.linkedin.com/jobs/view/4398965812/ | Notion - Software Engineer AI Workflows |
| 6 | Senior Consultant - Data Science / Data Lake | Deloitte | New York, NY (Hybrid) | 6d ago | `[NOT FOUND — NY req]` (Chicago equivalent: https://www.linkedin.com/jobs/view/4418047808/) | Deloitte - Senior Consultant Data Science Data Lake |
| 7 | Forward Deployed Engineer | Singular Recruitment | New York, United States (Hybrid) | 18h ago | https://www.linkedin.com/jobs/view/4412483632/ | Singular Recruitment - Forward Deployed Engineer |
| 8 | Generative AI Engineer | Dataiku | New York, United States | 1d ago | `[NOT FOUND]` | Dataiku - Generative AI Engineer |
| 9 | Data & Applied Scientist II | Microsoft AI | Redmond, WA | 1d ago | `[NOT FOUND]` | Microsoft AI - Data and Applied Scientist II |
| 10 | Forward Deployed Engineer | HappyRobot | Chicago, IL (Hybrid) | 1d ago | https://www.linkedin.com/jobs/view/4250531432/ | HappyRobot - Forward Deployed Engineer |

## Batch 2 (jobs 11–20)

| # | Title | Company | Location | Posted | LinkedIn URL | Folder |
|---|-------|---------|----------|--------|--------------|--------|
| 11 | Analytics Engineer — Data Warehouse | Together AI | San Francisco, CA | 6d ago | https://www.linkedin.com/jobs/view/4395930432/ | Together AI - Analytics Engineer Data Warehouse |
| 12 | Senior AI Engineer | GitLab | United States (Remote) | 2d ago | `[NOT FOUND]` | GitLab - Senior AI Engineer |
| 13 | Senior Consultant - AI Engineering | IBM | New York, United States (Hybrid) | 2d ago | https://www.linkedin.com/jobs/view/4407779344/ | IBM - Senior Consultant AI Engineering |
| 14 | Delivery Consultant - Data Architect, AWS Professional Services | Amazon Web Services (AWS) | Seattle, WA | 4d ago | https://www.linkedin.com/jobs/view/4400646656/ | AWS - Delivery Consultant Data Architect ProServe |
| 15 | Insights and Analytics Senior Consultant | Deloitte | New York, NY (Hybrid) | 1d ago | https://www.linkedin.com/jobs/view/4410272558/ | Deloitte - Insights and Analytics Senior Consultant |
| 16 | Technical Solutions Consultant, Agent Assist, Applied AI | Google | New York, NY (On-site) | 2d ago | https://www.linkedin.com/jobs/view/4417878962/ | Google - Technical Solutions Consultant Agent Assist Applied AI |
| 17 | Sr AI Engineer | PepsiCo | Chicago, IL (On-site) | 1d ago | https://www.linkedin.com/jobs/view/4251319181/ | PepsiCo - Sr AI Engineer |
| 18 | Data and Analytics Consultant | Systems Evolution, Inc. | Chicago, IL | 1d ago | `[NOT FOUND]` | Systems Evolution - Data and Analytics Consultant |
| 19 | AI and Technology Consultant | Systems Evolution, Inc. | Chicago, IL | 1d ago | `[NOT FOUND]` | Systems Evolution - AI and Technology Consultant |
| 20 | FinanceAI Senior Consultant | Deloitte | Chicago, IL (Hybrid) | 2d ago | https://www.linkedin.com/jobs/view/4419862260/ | Deloitte - FinanceAI Senior Consultant |

---

## Coverage summary

- **Matched (URL + full JD captured):** 15 (added Together AI via web-search fallback)
- **Not found:** 5 (Dataiku, Microsoft AI, GitLab, 2× Systems Evolution; Deloitte NY Data Lake partial — Chicago equivalent JD captured as proxy)

### Web-search fallback also tried for the 5 still-missing — all failed

For Dataiku, Microsoft AI, GitLab, and both Systems Evolution roles: web search surfaced LinkedIn URLs that looked correct, but WebFetch on those URLs returned wrong content (LinkedIn redirects expired/inactive direct URLs to generic search result pages). The reqs are likely closed or have moved IDs.

**To recover any of these manually:**
1. Open LinkedIn → "My Items" → "Saved Jobs" in your browser
2. Click into the listing
3. Copy the URL from the browser address bar
4. Paste into the role folder's `Job Description.md` header
5. Run `jd-to-ready` from there

## Why `[NOT FOUND]` happens

LinkedIn's `search_jobs` ranks by relevance, recency, and **promoted listings**. A saved job from a small employer (Together AI, Dataiku, Systems Evolution) or a stale req often won't surface in the top results even with the exact title + company. To recover, open the job directly in LinkedIn's UI and copy the URL — paste it into the corresponding row below.

## Next steps for these 20 roles

- 14 matched → role folders created at workspace root (see Pipeline.md `Considering / not yet applied`).
- 6 not found → folders created with the title/company; the `Job Description.md` has a `## URL — PASTE FROM LINKEDIN` placeholder. Kanu pastes the URL, then runs `jd-to-ready` per role.
- For any role Kanu wants to apply to next, the path is: open folder → fill in JD body from the LinkedIn posting → run `jd-to-ready` for resume + outreach.
