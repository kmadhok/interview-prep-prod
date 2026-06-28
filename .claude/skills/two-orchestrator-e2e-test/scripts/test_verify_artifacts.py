import sys, json, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import verify_artifacts as va


def _clone_with(files: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = d / name
        p.write_text(content, encoding="utf-8")
    return d


def test_rollup_severities():
    assert va.rollup([va.check("a", True)]) == "pass"
    assert va.rollup([va.check("a", False, severity="warn")]) == "warn"
    assert va.rollup([va.check("a", False, severity="fail")]) == "fail"
    # a hard fail dominates a warn
    assert va.rollup([va.check("a", False, "", "warn"), va.check("b", False, "", "fail")]) == "fail"


def test_intake_pass_and_fail():
    good = _clone_with({"Job Description.md": "# Role\n\n" + "x" * 100})
    res = va.check_intake(good)
    assert res["status"] == "pass", res

    empty = _clone_with({})  # no Job Description.md
    assert va.check_intake(empty)["status"] == "fail"


_GOOD_CLASS = json.dumps({
    "themes": [
        {"tag": "NL→SQL", "evidence": "expose tables to natural language"},
        {"tag": "agents", "evidence": "data agents need to reason"},
        {"tag": "end-to-end", "evidence": "source ingestion to semantic layer"},
        {"tag": "business-translation", "evidence": "translate business requirements"},
    ],
    "archetype": "FDE / client-facing",
    "archetype_rationale": "embeds with customers",
    "notes": "",
    "classified_ts": "2026-06-28",
})


def test_classify_pass():
    clone = _clone_with({".classification.json": _GOOD_CLASS})
    assert va.check_classify(clone)["status"] == "pass"


def test_classify_off_vocab_theme_fails():
    bad = json.loads(_GOOD_CLASS)
    bad["themes"][0]["tag"] = "made-up-tag"
    clone = _clone_with({".classification.json": json.dumps(bad)})
    res = va.check_classify(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "themes-in-vocab" and not c["ok"] for c in res["checks"])


def test_classify_missing_file_fails():
    assert va.check_classify(_clone_with({}))["status"] == "fail"


_RESUME_OK = ("# Kanu Madhok\n\nmadhok.kanu@gmail.com\n\n" +
              "## EXPERIENCE\n- Built a registry-governed semantic layer over 67 tables.\n" * 6)


def test_tailor_resume_pass():
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": _RESUME_OK})
    assert va.check_tailor_resume(clone)["status"] == "pass"


def test_tailor_resume_verify_leak_fails():
    leaked = _RESUME_OK + "\n- Drove [VERIFY: 95% accuracy] across the org.\n"
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": leaked})
    res = va.check_tailor_resume(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "no-verify-leak" and not c["ok"] for c in res["checks"])


def test_tailor_resume_missing_fails():
    assert va.check_tailor_resume(_clone_with({}))["status"] == "fail"
