"""Fetch the Google Calendar (secret iCal address) and write events.json for the site.

Usage: ICAL_URL=... python scripts/fetch_calendar.py   (or: python scripts/fetch_calendar.py file.ics)
In the Google event: title = Hebrew title; optional line "EN: English title" in the description;
a URL in the description becomes the event link.
"""
import json, os, re, sys, urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events

TZ = ZoneInfo("Asia/Jerusalem")

if len(sys.argv) > 1:
    raw = open(sys.argv[1], "rb").read()
else:
    raw = urllib.request.urlopen(os.environ["ICAL_URL"], timeout=30).read()

cal = icalendar.Calendar.from_ical(raw)
today = datetime.now(TZ).date()
items = recurring_ical_events.of(cal).between(today - timedelta(days=31), today + timedelta(days=400))

events = []
for c in items:
    title = str(c.get("SUMMARY", "")).strip()
    if not title or str(c.get("STATUS", "")) == "CANCELLED":
        continue
    start, end = c.decoded("DTSTART"), (c.decoded("DTEND") if c.get("DTEND") else None)
    desc = str(c.get("DESCRIPTION", ""))
    ev = {"title": title}
    en = re.search(r"^\s*EN:\s*(.+)$", desc, re.M)
    if en:
        ev["en"] = en.group(1).strip()
    link = re.search(r"https?://[^\s<\"]+", desc)
    if link:
        ev["link"] = link.group(0)
    if isinstance(start, datetime):
        s = start.astimezone(TZ)
        ev["date"] = s.strftime("%Y-%m-%d")
        ev["time"] = s.strftime("%H:%M") + ("–" + end.astimezone(TZ).strftime("%H:%M") if isinstance(end, datetime) else "")
    else:
        ev["date"] = start.isoformat()
    events.append(ev)

events.sort(key=lambda e: (e["date"], e.get("time", "")))
out = os.path.join(os.path.dirname(__file__), "..", "events.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(len(events), "events")
