from prepped_not_applied import role_is_resolved_in_pipeline, stale_prepped_not_applied

PIPELINE = "\n".join([
    "## Active",
    "| **Acme — Agent Builder** | **Applied** — submitted 2026-06-20 | n | d | c | f |",
    "## Considering / not yet applied",
    "| **Beta — ML Engineer** | Considering — JD reviewed, not yet applied | n | d | c | f |",
    "## Closed / On hold",
    "| **Gamma — Data Sci** | **Rejected** | Applied 2026-06-01 → rejected | notes |",
])

def test_resolved_true_for_active_applied():
    assert role_is_resolved_in_pipeline("Acme", PIPELINE)

def test_resolved_true_for_closed_section():
    assert role_is_resolved_in_pipeline("Gamma", PIPELINE)   # closed = resolved, don't nudge

def test_resolved_false_for_considering():
    assert not role_is_resolved_in_pipeline("Beta", PIPELINE)  # prepped+considering = nudge candidate

def test_resolved_false_for_unknown_company():
    assert not role_is_resolved_in_pipeline("Zeta", PIPELINE)

def test_stale_filters_on_age_and_resolution():
    prepped = [
        ("Acme", "Agent Builder", 9),   # applied → excluded
        ("Beta", "ML Engineer", 9),     # unresolved + stale → INCLUDED
        ("Gamma", "Data Sci", 9),       # closed → excluded
        ("Beta", "ML Engineer", 1),     # unresolved but fresh (<3) → excluded
    ]
    out = stale_prepped_not_applied(prepped, PIPELINE, threshold_days=3)
    assert out == [("Beta", "ML Engineer", 9)]

def test_threshold_boundary_inclusive():
    prepped = [("Beta", "ML Engineer", 3)]
    assert stale_prepped_not_applied(prepped, PIPELINE, threshold_days=3) == [("Beta", "ML Engineer", 3)]

def test_empty_prepped():
    assert stale_prepped_not_applied([], PIPELINE) == []

def test_resolved_false_when_company_only_in_notes_of_closed_row():
    pipeline = "\n".join([
        "## Closed / On hold",
        "| **Unrelated — Some Role** | Rejected | referral from Acme contact |",
    ])
    # "Acme" appears only in another closed row's notes — must NOT resolve Acme
    assert not role_is_resolved_in_pipeline("Acme", pipeline)

def test_resolved_true_when_company_is_the_closed_rows_subject():
    pipeline = "\n".join([
        "## Closed / On hold",
        "| **Acme — ML Eng** | Rejected | Applied 2026-05-01 → rejected |",
    ])
    assert role_is_resolved_in_pipeline("Acme", pipeline)
