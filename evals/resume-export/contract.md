# resume-export — Behavior Contract

The resume-export step builds a one-page PDF from the tailored resume
markdown. This contract pins the observable end-state of a completed
resume-export run.

## Clauses

### resume-export-C1: PDF exists next to the resume md

A PDF file exists in the role folder whose name starts with the profile's
`resume_glob_prefix()` — i.e. the `.pdf` sibling of the resume `.md`.

**How checked:** Glob `workspace/Roles/Acme - Senior Agent Builder/` for
`{resume_glob_prefix()}*.pdf`; assert at least one match. (Same glob
verify_artifacts.check_pdf uses.)

### resume-export-C2: One page

The PDF is exactly one page. The page-count technique is a stdlib regex over
the PDF bytes (`/Type /Page[^s]`) — the same one `build_resume_pdf.py`'s
`_count_pdf_pages` uses, so no pypdf dependency is needed.

**How checked:** Read the PDF bytes; count `/Type\s*/Page[^s]` occurrences;
assert the count is exactly 1.

### resume-export-C3: No title leak

The resume markdown does not leak a bare "Resume" heading into the PDF
title. `build_resume_pdf.py`'s `_detect_title_leak` returns 0 when clean;
this clause asserts the same for the resume `.md` backing the PDF.

**How checked:** Apply the `_detect_title_leak` logic (re-implemented inline
so this verifier stays standalone without importing build_resume_pdf, which
pulls in reportlab) to the resume `.md`; assert the result is 0.
