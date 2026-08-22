"""Daily Apply Queue digest -> ntfy push. Pure compose, injected clock/opener.

Delivers the Applied Detector's fail-loud nudge (Spec - Applied Detector.md)
plus queue freshness. The topic name is a secret: read from
~/.claude/ntfy_topic.txt, never committed (Spec - Apply Packet.md, decision 3).
"""
from __future__ import annotations
import argparse, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

from apply_packet import _packet_folders, read_packet

STALE_DAYS = 3
TOPIC_FILE = Path.home() / ".claude" / "ntfy_topic.txt"


def gather(repo_root: Path, now: datetime) -> dict:
    """Execute `gather`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    queued, stale = [], []
    for folder in _packet_folders(repo_root):
        rec = read_packet(folder)
        if not rec or rec.get("state") != "queued":
            continue
        entry = {"folder": folder.name, "posted_date": rec.get("posted_date"),
                 "easy_apply": rec.get("easy_apply"), "uploaded_ts": rec.get("uploaded_ts")}
        queued.append(entry)
        try:
            age = (now - datetime.fromisoformat(rec.get("uploaded_ts"))).days
        except (TypeError, ValueError):
            age = None
        if age is not None and age > STALE_DAYS:
            stale.append({**entry, "age_days": age})
    queued.sort(key=lambda q: q.get("posted_date") or "", reverse=True)
    return {"queued": queued, "stale": stale}


def compose(data: dict) -> str:
    """Execute `compose`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    q, s = data["queued"], data["stale"]
    if not q:
        return "Apply Queue: empty"
    newest = q[0]
    lines = [f"Apply Queue: {len(q)} ready to apply (newest: {newest['folder']}"
             + (f", posted {newest['posted_date']}" if newest.get("posted_date") else "") + ")"]
    for item in s:
        lines.append(f"waiting {item['age_days']}d — did you apply? {item['folder']}")
    easy = [x["folder"] for x in q if x.get("easy_apply")]
    if easy:
        lines.append(f"Easy Apply available: {', '.join(easy)}")
    return "\n".join(lines)


def send(topic: str, text: str, opener=urllib.request.urlopen) -> None:
    """Execute `send`; propagate invalid input, I/O, authentication, and provider failures to the caller unless handled here."""
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=text.encode("utf-8"),
        headers={"Title": "Apply Queue digest"})
    with opener(req, timeout=15) as resp:
        if getattr(resp, "status", 200) >= 300:
            raise RuntimeError(f"ntfy returned {resp.status}")


def main(argv=None) -> int:
    """Run the command-line workflow; parse/user/provider failures terminate with the documented nonzero status."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--send", action="store_true")
    args = p.parse_args(argv)
    now = datetime.now(timezone.utc).astimezone()
    text = compose(gather(Path(args.repo_root), now))
    print(text)
    if args.send:
        if not TOPIC_FILE.exists():
            print(f"DIGEST ERROR: {TOPIC_FILE} missing — cannot push", file=sys.stderr)
            return 1
        send(TOPIC_FILE.read_text(encoding="utf-8-sig").strip(), text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
