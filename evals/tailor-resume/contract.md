# tailor-resume — Behavior Contract

The tailor-resume step produces a resume markdown tailored to the role from
the canonical `Resume Achievements Master.md`. This contract pins the
observable end-state of a completed tailor-resume run.

## Clauses

### tailor-resume-C1: Resume md exists matching profile prefix

A resume markdown file exists in the role folder whose filename starts with
the profile's `resume_glob_prefix()` (from `scripts/config.py`).

**How checked:** Glob `workspace/Roles/Acme - Senior Agent Builder/` for
files matching `{resume_glob_prefix()}*.md`; assert at least one match.

### tailor-resume-C2: No content from Resume Claims To Verify

The resume contains no quarantined-claim markers. The file
`Resume Claims To Verify.md` is the quarantine file for unverified claims;
its presence is indicated by the marker string "Resume Claims To Verify" and
the phrase "UNVERIFIED". Neither should appear in a tailored resume.

**How checked:** Read the resume text; assert it does not contain the
substring "Resume Claims To Verify" and does not contain "UNVERIFIED".

### tailor-resume-C3: No placeholder leaks

The resume contains none of the placeholder markers that indicate unfinished
tailoring: `[NUMBER?]`, `<user_`, `{name}`, `TBD`.

**How checked:** Read the resume text; assert none of those four strings
appear.

### tailor-resume-C4: Gaps file present when JD demands non-canonical claims

IF the workspace JD contains "fusion reactors" THEN a gaps file
`.eval-gaps.json` exists in the role folder listing at least one gap with
kind indicating no canonical match (e.g. `no-canonical-match`). This is the
fixture-run convention: pipeline runs record returned gaps there for the
verifier. If the JD does not contain "fusion reactors", this clause passes
vacuously.

**How checked:** If "fusion reactors" appears in any `*.md` file in the role
folder, assert `workspace/Roles/Acme - Senior Agent Builder/.eval-gaps.json`
exists, parses as JSON, and its gaps list has at least one entry whose
`kind` contains "no-canonical-match" (or is a non-empty list of gaps).
