from dedupe import is_duplicate, company_in_pipeline, job_id_in_pipeline

PIPE = "| **Pinterest — AI Solutions Engineer** | ... | Pinterest careers (job 4387218136) | ... |"

def test_company_match_word_boundary():
    assert company_in_pipeline("pinterest", PIPE)      # whole word, case-insensitive
    assert not company_in_pipeline("Pin", PIPE)         # substring must NOT match "Pinterest"
    assert not company_in_pipeline("Acme Corp", PIPE)
    assert not company_in_pipeline("", PIPE)

def test_job_id_match():
    assert job_id_in_pipeline("4387218136", PIPE)
    assert not job_id_in_pipeline("9999999999", PIPE)
    assert not job_id_in_pipeline("", PIPE)

def test_is_duplicate_only_on_job_id():
    assert is_duplicate("Other", "4387218136", PIPE)    # precise job_id hit -> duplicate
    assert not is_duplicate("Pinterest", "0", PIPE)      # company alone is NOT a dup (avoids silent loss)
    assert not is_duplicate("Brand New Co", "123", PIPE)
