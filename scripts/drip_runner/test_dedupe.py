from dedupe import is_duplicate, company_in_pipeline, job_id_in_pipeline

PIPE = "| **Pinterest — AI Solutions Engineer** | ... | Pinterest careers (job 4387218136) | ... |"

def test_company_match_case_insensitive():
    assert company_in_pipeline("pinterest", PIPE)
    assert not company_in_pipeline("Acme Corp", PIPE)
    assert not company_in_pipeline("", PIPE)

def test_job_id_match():
    assert job_id_in_pipeline("4387218136", PIPE)
    assert not job_id_in_pipeline("9999999999", PIPE)
    assert not job_id_in_pipeline("", PIPE)

def test_is_duplicate_combines():
    assert is_duplicate("Pinterest", "0", PIPE)
    assert is_duplicate("Other", "4387218136", PIPE)
    assert not is_duplicate("Brand New Co", "123", PIPE)
