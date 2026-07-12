# tailor-resume — Behavior Contract

The tailor-resume step produces a resume markdown tailored to the role from
the canonical `Resume Achievements Master.md`. This contract pins the
observable end-state of a completed tailor-resume run.

## Clauses

### tailor-resume-C1: Resume md exists matching profile prefix

A resume markdown file exists in the role folder whose filename starts with
the profile's `resume_glob_prefix()` (from `scripts/config.py`).

**How checked:** Glob the selected role for the profile-derived prefix.

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

### tailor-resume-C4: Resume is nontrivial and contains profile contact email

The selected resume has more than 400 non-whitespace characters and includes
the configured profile email. Both are artifacts owned by tailor-resume.

**How checked:** Read the matching resume markdown, measure stripped length,
and require `profile.user_email` in its contact header. Structured `gaps[]`
remain a cross-cutting trace requirement validated by the behavior trace audit.
