#!/usr/bin/env python3
"""
Email the daily Torchlight leaderboard (+ a running cumulative tally) as CSV attachments.

Reads the public, always-on DAILY leaderboard from Firestore over REST
(events/daily/puzzles/{date}/results), builds two CSV sheets — that day's board
and a cumulative tally across LB_START_DATE..target — and emails them.

Designed to run daily from GitHub Actions just after the midnight-IST puzzle rollover,
so the reported puzzle (yesterday, IST) is already final.

Env:
  GMAIL_USER           sender gmail address (e.g. srane12cl@gmail.com)
  GMAIL_APP_PASSWORD   16-char Google App Password for GMAIL_USER
  MAIL_TO              recipient(s), comma-separated (default: sailee.rane12@gmail.com)
  LB_START_DATE        first puzzle date to include in the cumulative tally (default: 2026-09-23)
  TARGET_DATE          puzzle date to report (default: yesterday in IST)
  FB_PROJECT_ID        Firestore project (default: torchlight-leaderboard-may-21)
  FB_API_KEY           public web API key (default: from docs/leaderboard/config.js)
"""

import csv
import io
import os
import json
import smtplib
import urllib.request
import urllib.error
from datetime import datetime, timedelta, date
from email.message import EmailMessage
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
HINT_PENALTY_MS = 30_000

# Public values (same as docs/leaderboard/config.js). Safe to ship; reads are public.
FB_PROJECT_ID = os.environ.get("FB_PROJECT_ID", "torchlight-leaderboard-may-21")
FB_API_KEY = os.environ.get("FB_API_KEY", "AIzaSyBOus4XY3mDs73KcONWaS2lrWkwo2TRThI")


def fetch_results(puzzle_date):
    """Return a list of entry dicts for one puzzle date (empty list if none)."""
    base = (
        f"https://firestore.googleapis.com/v1/projects/{FB_PROJECT_ID}"
        f"/databases/(default)/documents/events/daily/puzzles/{puzzle_date}/results"
    )
    entries = []
    page_token = None
    while True:
        url = f"{base}?pageSize=300&key={FB_API_KEY}"
        if page_token:
            url += f"&pageToken={page_token}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                payload = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
            raise
        for doc in payload.get("documents", []):
            f = doc.get("fields", {})
            def _int(k):
                return int(f.get(k, {}).get("integerValue", 0) or 0)
            ms = _int("ms")
            hints = _int("hints")
            adj = _int("adjustedMs") or (ms + hints * HINT_PENALTY_MS)
            entries.append({
                "name": f.get("name", {}).get("stringValue", "").strip(),
                "ms": ms,
                "adj": adj,
                "hints": hints,
                "mistakes": _int("mistakes"),
                "won": f.get("won", {}).get("booleanValue", False),
            })
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return entries


def fmt(ms):
    s = int(ms) // 1000
    return f"{s // 60}:{s % 60:02d}"


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def board_csv(entries):
    rows = sorted(entries, key=lambda r: (not r["won"], r["adj"]))
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Rank", "Name", "Time", "Adjusted", "Hints", "Mistakes",
                "Result", "RawMs", "AdjustedMs"])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r["name"], fmt(r["ms"]), fmt(r["adj"]), r["hints"],
                    r["mistakes"], "WON" if r["won"] else "lost", r["ms"], r["adj"]])
    return buf.getvalue(), rows


def tally_csv(by_date):
    players = {}
    for entries in by_date.values():
        for r in entries:
            p = players.setdefault(r["name"], {
                "days": 0, "adj": 0, "best": None, "hints": 0, "mistakes": 0})
            p["days"] += 1
            p["adj"] += r["adj"]
            p["hints"] += r["hints"]
            p["mistakes"] += r["mistakes"]
            if p["best"] is None or r["adj"] < p["best"]:
                p["best"] = r["adj"]
    ranked = sorted(players.items(), key=lambda kv: (-kv[1]["days"], kv[1]["adj"]))
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Rank", "Player", "PuzzlesPlayed", "TotalAdjusted", "BestTime",
                "TotalHints", "TotalMistakes", "TotalAdjustedMs"])
    for i, (name, p) in enumerate(ranked, 1):
        w.writerow([i, name, p["days"], fmt(p["adj"]), fmt(p["best"]),
                    p["hints"], p["mistakes"], p["adj"]])
    return buf.getvalue(), ranked


def env(name, default=""):
    """os.environ.get, but treat an unset OR blank value as missing.
    (GitHub Actions passes "" for undefined vars/inputs.)"""
    v = os.environ.get(name, "").strip()
    return v if v else default


def main():
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    to = [a.strip() for a in env("MAIL_TO", "sailee.rane12@gmail.com").split(",")
          if a.strip()]

    start = date.fromisoformat(env("LB_START_DATE", "2026-09-23"))
    target_env = env("TARGET_DATE")
    if target_env:
        target = date.fromisoformat(target_env)
    else:
        target = (datetime.now(IST) - timedelta(days=1)).date()

    # Pull every date in the cumulative window once.
    by_date = {d.isoformat(): fetch_results(d.isoformat())
               for d in daterange(start, target)}
    today_entries = by_date.get(target.isoformat(), [])

    board_text, board_rows = board_csv(today_entries)
    tally_text, ranked = tally_csv(by_date)

    total_entries = sum(len(v) for v in by_date.values())
    days_with_data = sum(1 for v in by_date.values() if v)
    top = board_rows[0] if board_rows else None

    subject = f"Torchlight leaderboard — {target.isoformat()} ({len(board_rows)} players)"
    lines = [
        f"Torchlight daily leaderboard for {target.isoformat()}",
        "",
        f"  Players on the board : {len(board_rows)}",
    ]
    if top:
        lines.append(f"  Fastest              : {top['name']} ({fmt(top['adj'])} adjusted)")
    lines += [
        "",
        f"Cumulative tally ({start.isoformat()} → {target.isoformat()}):",
        f"  Puzzles with entries : {days_with_data}",
        f"  Unique players       : {len(ranked)}",
        f"  Total entries        : {total_entries}",
        "",
        "Two sheets are attached:",
        f"  - leaderboard_{target.isoformat()}.csv  (this puzzle's board)",
        f"  - cumulative_tally_{start.isoformat()}_to_{target.isoformat()}.csv",
        "",
        "Note: the daily board records winners only (opt-in by name).",
    ]
    body = "\n".join(lines)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(to)
    msg.set_content(body)
    msg.add_attachment(board_text.encode(), maintype="text", subtype="csv",
                       filename=f"leaderboard_{target.isoformat()}.csv")
    msg.add_attachment(tally_text.encode(), maintype="text", subtype="csv",
                       filename=f"cumulative_tally_{start.isoformat()}_to_{target.isoformat()}.csv")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, password)
        s.send_message(msg)

    print(f"Sent {target.isoformat()} board ({len(board_rows)} players) + "
          f"cumulative tally ({len(ranked)} players) to {', '.join(to)}")


if __name__ == "__main__":
    main()
