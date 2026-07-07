#!/usr/bin/env python3
"""Mechanical, model-agnostic hard-gate checker for skill-loop-trainer runs.

Generalized from the Write Outreach Test harness. Edit BANNED, the SIG marker, and
the parse() function to match the TARGET skill's output format + rules, then run:

    python3 gate_check.py <runs_root> <slug1,slug2,...>

<runs_root> = dir containing wo-<model>/.../runs/<model>/ trees, or any layout you set
via the MODELS / PATH_TMPL constants below. Prints PASS/FAIL per (model, fixture).

This is a STARTING POINT — the email-specific gates (subject<70 credential-first,
50-125 words, em-dash, signature) are what the write-outreach run needed. Swap them
for the target skill's invariants.
"""
import re, os, sys

# --- adapt these to the target skill ---------------------------------------
MODELS = ["claude", "codex", "gemini"]
# how to locate one output file given (runs_root, model, slug):
PATH_TMPL = "{root}/.claude/worktrees/{slug_base}-{model}/{test_dir}/runs/{model}/{slug}.md"
TEST_DIR  = "Write Outreach Test"          # the "<Name> Test" folder name
SLUG_BASE = "wo"                            # the worktree branch prefix
BANNED = ["i hope this email finds you well","i hope you are doing well",
          "i hope this message finds you well","just wanted to reach out",
          "i wanted to reach out to express my interest","i came across your profile",
          "i wanted to take a moment to","leverage","spearhead","synergize","synergy",
          "drove","passionate","rockstar","ninja"]
# Example signature sentinel — swap for the target skill's actual required
# signature line (email · linkedin · github) before running the gate.
SIG = "user@example.com · linkedin.com/in/example · github.com/example"

def parse(text):
    """Return (subject, body). Handles 'Subject: ...' and '## Subject\\n`...`' forms."""
    subject = ""
    sm = re.search(r'(?im)^\s*(?:\*\*?)?subject(?:\*\*?)?\s*:\s*(.+)$', text)
    if sm:
        subject = sm.group(1).strip().strip('*`')
    else:
        sm2 = re.search(r'(?im)^#+\s*subject\s*\n+\s*`?([^`\n]+)`?', text)
        if sm2:
            subject = sm2.group(1).strip().strip('`')
    bm = re.search(r'(?is)\bHi\s+\w+,\s*(.*?)\n\s*Best,', text)
    body = bm.group(1).strip() if bm else ""
    return subject, body

def check(text):
    subj, body = parse(text)
    words = len(re.findall(r"\S+", body))
    emdash = body.count('—')                      # banned em-dash only (en-dash – is fine)
    banned = [b for b in BANNED if re.search(r'(?i)'+re.escape(b), body)]
    cred = subj.lower().startswith("ex-walmart") or "walmart agent builder" in subj.lower()
    return dict(subj_len=len(subj), subj_ok=(0 < len(subj) < 70 and cred),
                words=words, len_ok=50 <= words <= 125, emdash=emdash, G4=emdash == 0,
                banned=banned, G3=not banned, cta=body.count('?'),
                sig=(SIG in text and "Live demo:" in text))
# ---------------------------------------------------------------------------

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    slugs = sys.argv[2].split(',') if len(sys.argv) > 2 else \
            ["cohere-fde", "distyl-fde", "sierra-strategist"]
    slug_base = SLUG_BASE
    for m in MODELS:
        print(f"\n===== {m.upper()} =====")
        for slug in slugs:
            p = PATH_TMPL.format(root=root, slug_base=slug_base, model=m,
                                 test_dir=TEST_DIR, slug=slug)
            if not os.path.exists(p):
                print(f"  {slug:18} MISSING ({p})"); continue
            r = check(open(p, encoding='utf-8').read())
            ok = (r["subj_ok"] and r["len_ok"] and r["G4"] and r["G3"]
                  and r["sig"] and r["cta"] == 1)
            print(f"  {slug:18}[{'PASS' if ok else 'FAIL'}] "
                  f"subj={r['subj_len']:>2}{'OK' if r['subj_ok'] else 'X'} "
                  f"words={r['words']:>3}{'OK' if r['len_ok'] else 'X'} "
                  f"emdash={r['emdash']} banned={r['banned'] or '-'} "
                  f"sig={'OK' if r['sig'] else 'X'} cta={r['cta']}")

if __name__ == "__main__":
    main()
