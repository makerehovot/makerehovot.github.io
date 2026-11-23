"""Fetch the Google Calendar (secret iCal address), write events.json and one page per event.

Usage: ICAL_URL=... python scripts/fetch_calendar.py   (or: python scripts/fetch_calendar.py file.ics)

In the Google event:
  - title = Hebrew title; an optional line "EN: English title" in the description
  - the description text is shown on the event's page (workshops/ and en/workshops/)
  - the first URL in the description becomes the sign-up button
  - for an English description, add a line containing only "---" and write the English text after it
"""
import hashlib, html, json, os, re, sys, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events

TZ = ZoneInfo("Asia/Jerusalem")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HE_DAYS = ["יום שני", "יום שלישי", "יום רביעי", "יום חמישי", "יום שישי", "יום שבת", "יום ראשון"]
HE_MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
EN_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
URL_RE = re.compile(r'https?://[^\s<"]+')

PAGE = """<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Make Rehovot</title>
  <link rel="icon" href="{up}assets/logo-havayot.png">
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    :root {{ --ink: #3b3b3d; --ink-soft: #66666a; --bg: #fffdf8; --line: #ece7da; --yellow: #fbb913; --orange: #ee5a24; }}
    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{ --ink: #f3f1ea; --ink-soft: #b9b6ad; --bg: #1d1d1f; --line: #38383b; }}
    }}
    * {{ box-sizing: border-box; margin: 0; }}
    body {{ font-family: "Heebo", system-ui, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.7; min-height: 100vh; display: flex; flex-direction: column; }}
    header {{ background: #e7e0d4; color: #3b3b3d; }}
    .wrap {{ max-width: 760px; margin-inline: auto; padding-inline: 16px; }}
    .nav {{ display: flex; align-items: center; padding-block: 10px; max-width: 1080px; }}
    .brand img {{ height: 64px; width: auto; display: block; }}
    main {{ flex: 1; padding-block: 40px; }}
    h1 {{ font-size: clamp(1.8rem, 5vw, 2.8rem); font-weight: 900; line-height: 1.2; margin-bottom: 12px; }}
    .when {{ color: var(--ink-soft); font-size: 1.1rem; font-weight: 500; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--line); }}
    .desc p {{ font-size: 1.1rem; margin-bottom: 14px; }}
    .desc a {{ color: var(--orange); overflow-wrap: anywhere; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }}
    .btn {{ display: inline-block; padding: 12px 26px; border-radius: 999px; background: var(--orange); color: #fff; font-weight: 700; text-decoration: none; }}
    .btn.ghost {{ background: none; color: var(--ink); border: 2px solid var(--line); }}
  </style>
</head>
<body>
  <header>
    <div class="wrap nav">
      <a class="brand" href="../index.html">
        <img src="{up}assets/logo-makers.png" alt="{brand_alt}">
      </a>
    </div>
  </header>
  <main>
    <div class="wrap">
      <h1>{title}</h1>
      <div class="when">{when}</div>
      <div class="desc">
{desc}
      </div>
      <div class="actions">
{signup}        <a class="btn ghost" href="../index.html#calendar">{back}</a>
      </div>
    </div>
  </main>
</body>
</html>
"""


def linkify(line):
    out, pos = "", 0
    for m in URL_RE.finditer(line):
        url = html.escape(m.group(0))
        out += html.escape(line[pos:m.start()]) + '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, url)
        pos = m.end()
    return out + html.escape(line[pos:])


def paragraphs(text):
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    return "\n".join("        <p>" + "<br>\n        ".join(linkify(l.strip()) for l in b.strip().splitlines()) + "</p>" for b in blocks)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


if len(sys.argv) > 1:
    raw = open(sys.argv[1], "rb").read()
else:
    raw = urllib.request.urlopen(os.environ["ICAL_URL"], timeout=30).read()

cal = icalendar.Calendar.from_ical(raw)
today = datetime.now(TZ).date()
items = recurring_ical_events.of(cal).between(today - timedelta(days=31), today + timedelta(days=400))

events, made = [], set()
for c in items:
    title = str(c.get("SUMMARY", "")).strip()
    if not title or str(c.get("STATUS", "")) == "CANCELLED":
        continue
    start = c.decoded("DTSTART")
    end = c.decoded("DTEND") if c.get("DTEND") else None
    desc = str(c.get("DESCRIPTION", "")).replace("\\n", "\n").replace("\r", "")
    ev = {"title": title}
    en = re.search(r"^[ \t]*EN:[ \t]*(.+)$", desc, re.M)
    if en:
        ev["en"] = en.group(1).strip()
        desc = desc.replace(en.group(0), "")
    parts = re.split(r"^[ \t]*---[ \t]*$", desc, maxsplit=1, flags=re.M)
    he_desc = parts[0]
    en_desc = parts[1] if len(parts) > 1 else parts[0]
    signup = URL_RE.search(desc)
    if signup:
        ev["signup"] = signup.group(0)
    if isinstance(start, datetime):
        s = start.astimezone(TZ)
        d = s.date()
        ev["time"] = s.strftime("%H:%M") + ("–" + end.astimezone(TZ).strftime("%H:%M") if isinstance(end, datetime) else "")
    else:
        d = start
    ev["date"] = d.isoformat()
    slug = "e-%s-%s" % (ev["date"], hashlib.sha1(str(c.get("UID", title)).encode()).hexdigest()[:6])
    made.add(slug)
    ev["link"] = "workshops/%s.html" % slug  # relative to both / and /en/
    events.append(ev)

    for lang in ("he", "en"):
        he = lang == "he"
        text = he_desc if he else en_desc
        text = "\n".join(l for l in text.splitlines() if l.strip() != ev.get("signup"))  # URL-only line -> button
        day = (HE_DAYS if he else EN_DAYS)[d.weekday()]
        mon = (HE_MONTHS if he else EN_MONTHS)[d.month - 1]
        when = ("%s, %d ב%s %d" if he else "%s, %d %s %d") % (day, d.day, mon, d.year)
        if ev.get("time"):
            when += ' · <bdi dir="ltr">%s</bdi>' % ev["time"]
        button = ""
        if ev.get("signup"):
            button = '        <a class="btn" href="%s" target="_blank" rel="noopener">%s</a>\n' % (html.escape(ev["signup"]), "להרשמה" if he else "Sign up")
        page = PAGE.format(
            lang=lang, dir="rtl" if he else "ltr", up="../" if he else "../../",
            title=html.escape(title if he else ev.get("en", title)), when=when,
            brand_alt="חוויות Makers – רשת חוויות רחובות" if he else "Havayot Makers – Havayot Rehovot network",
            desc=paragraphs(text), back="חזרה ליומן" if he else "Back to calendar", signup=button,
        )
        folder = "workshops" if he else os.path.join("en", "workshops")
        write(os.path.join(ROOT, folder, slug + ".html"), page)

# remove pages of events that are no longer in the calendar
for folder in ("workshops", os.path.join("en", "workshops")):
    d = os.path.join(ROOT, folder)
    for f in os.listdir(d) if os.path.isdir(d) else []:
        if f.startswith("e-") and f.endswith(".html") and f[:-5] not in made:
            os.remove(os.path.join(d, f))

events.sort(key=lambda e: (e["date"], e.get("time", "")))
with open(os.path.join(ROOT, "events.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(events, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(len(events), "events")
