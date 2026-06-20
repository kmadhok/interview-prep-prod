from job_parser import parse_job_email, is_job_subject, first_url

def test_subject_loose_job_prefix():
    assert is_job_subject("JOB Blackstone")
    assert is_job_subject("JOB: Pinterest AI")
    assert is_job_subject("  job something")
    assert not is_job_subject("Jobs report Q3")
    assert not is_job_subject("Re: JOB forwarded")
    assert not is_job_subject("")

def test_first_url_strips_trailing_punct():
    assert first_url("see https://x.com/a). end") == "https://x.com/a"
    assert first_url("no link here") == ""

def test_linkedin_job_parsed():
    r = parse_job_email("JOB Blackstone", "https://www.linkedin.com/jobs/view/4428726955/")
    assert r.is_job and r.source == "linkedin" and r.job_id == "4428726955"
    assert r.url == "https://www.linkedin.com/jobs/view/4428726955/"

def test_ats_url_is_ats_no_jobid():
    r = parse_job_email("JOB Acme", "apply here https://boards.greenhouse.io/acme/jobs/123")
    assert r.is_job and r.source == "ats" and r.job_id == ""

def test_non_job_subject_rejected():
    r = parse_job_email("lunch?", "https://www.linkedin.com/jobs/view/1/")
    assert not r.is_job and "subject" in r.reason

def test_job_subject_no_url_rejected():
    r = parse_job_email("JOB Cohere", "forgot the link")
    assert not r.is_job and "URL" in r.reason
