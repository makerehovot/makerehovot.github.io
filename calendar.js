// ---- Calendar data: edit here (shared by the Hebrew and English pages) ----
// Regular opening hours (weekday: 0 = Sunday ... 6 = Saturday)
const OPEN = { weekdays: [1, 2], from: "17:00", to: "21:00" };
// Specific workshops / events. title = Hebrew, en = English. time and link are optional.
// link: a signup form (opens in a new tab) or a page on this site, e.g. "workshops/test.html"
// { date: "2026-11-18", title: "סדנת תפירה", en: "Sewing workshop", time: "17:30–19:30", link: "https://forms.gle/..." }
const EVENTS = [
  { date: "2026-11-09", title: "סדנת בדיקה", en: "Test workshop", link: "workshops/test.html" },
];
// Dates the space is closed even though it's a regular opening day: ["2026-12-01"]
const CLOSED = [];
// Holidays / special days, shown as labels. date (and optional "to" for a range) are YYYY-MM-DD.
// closed: true = the space is closed that day (taken from the Havayot vacation calendar, תשפ״ז).
const HOLIDAYS = [
  { date: "2026-11-09", title: "חג הסיגד", en: "Sigd" },
  { date: "2026-11-16", title: "יום בן־גוריון", en: "Ben-Gurion Day" },
  { date: "2026-12-04", to: "2026-12-12", title: "חנוכה", en: "Hanukkah" },
  { date: "2026-12-31", title: "יום השפה העברית", en: "Hebrew Language Day" },
  { date: "2027-01-23", title: "ט״ו בשבט", en: "Tu BiShvat" },
  { date: "2027-02-07", title: "יום המשפחה", en: "Family Day" },
  { date: "2027-02-21", to: "2027-02-22", title: "פורים קטן", en: "Purim Katan" },
  { date: "2027-03-22", title: "ערב פורים", en: "Purim eve" },
  { date: "2027-03-23", to: "2027-03-24", title: "פורים", en: "Purim", closed: true },
  { date: "2027-04-17", title: "יום העלייה", en: "Aliyah Day" },
  { date: "2027-04-21", title: "ערב פסח", en: "Passover eve" },
  { date: "2027-04-22", to: "2027-04-28", title: "פסח", en: "Passover", closed: true },
  { date: "2027-05-04", title: "יום השואה", en: "Holocaust Remembrance Day" },
  { date: "2027-05-11", title: "יום הזיכרון", en: "Memorial Day", closed: true },
  { date: "2027-05-12", title: "יום העצמאות", en: "Independence Day", closed: true },
  { date: "2027-05-17", title: "יום הרצל", en: "Herzl Day" },
  { date: "2027-05-21", title: "פסח שני", en: "Pesach Sheni" },
  { date: "2027-05-25", title: "ל״ג בעומר", en: "Lag BaOmer" },
  { date: "2027-06-04", title: "יום ירושלים", en: "Jerusalem Day" },
  { date: "2027-06-10", title: "ערב שבועות", en: "Shavuot eve", closed: true },
  { date: "2027-06-11", title: "שבועות", en: "Shavuot", closed: true },
  { date: "2027-08-03", title: "יום ז׳בוטינסקי", en: "Jabotinsky Day" },
  { date: "2027-08-11", title: "ערב תשעה באב", en: "Tisha B'Av eve" },
  { date: "2027-08-12", title: "תשעה באב", en: "Tisha B'Av" },
  { date: "2027-08-18", title: "ט״ו באב", en: "Tu B'Av" },
];
// ----------------------------------------------------------------------------

(function () {
  const EN = document.documentElement.lang === "en";
  const locale = EN ? "en-GB" : "he-IL";
  const text = (o) => (EN && o.en) || o.title;
  const closedLabel = EN ? "Closed" : "סגור";
  const dows = EN ? ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] : ["א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳"];

  const key = (d) => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  // expand HOLIDAYS (incl. ranges) into a lookup by date
  const HOL = {};
  HOLIDAYS.forEach((h) => {
    const [y1, m1, d1] = h.date.split("-").map(Number);
    const end = (h.to || h.date);
    for (let d = new Date(y1, m1 - 1, d1); key(d) <= end; d.setDate(d.getDate() + 1)) HOL[key(d)] = h;
  });
  // external links (signup forms) open in a new tab, pages on this site in the same tab
  const setLink = (el, url) => {
    el.href = url;
    if (/^https?:/.test(url)) { el.target = "_blank"; el.rel = "noopener"; }
  };
  const grid = document.getElementById("cal-grid");
  const title = document.getElementById("cal-title");
  const now = new Date();
  let view = new Date(now.getFullYear(), now.getMonth(), 1);
  const fmt = new Intl.DateTimeFormat(locale, { month: "long", year: "numeric" });
  const dayFmt = new Intl.DateTimeFormat(locale, { weekday: "long", day: "numeric", month: "long" });

  function render() {
    title.textContent = fmt.format(view);
    grid.textContent = "";
    dows.forEach((d) => {
      const c = document.createElement("div");
      c.className = "cal-dow";
      c.textContent = d;
      grid.appendChild(c);
    });
    const y = view.getFullYear(), m = view.getMonth();
    for (let i = 0; i < new Date(y, m, 1).getDay(); i++) {
      const b = document.createElement("div");
      b.className = "cal-day blank";
      grid.appendChild(b);
    }
    for (let day = 1; day <= new Date(y, m + 1, 0).getDate(); day++) {
      const date = new Date(y, m, day), k = key(date);
      const cell = document.createElement("div");
      cell.className = "cal-day";
      const num = document.createElement("span");
      num.className = "num";
      num.textContent = day;
      if (k === key(now)) cell.classList.add("today");
      cell.appendChild(num);
      const hol = HOL[k];
      const closed = CLOSED.includes(k) || (hol && hol.closed);
      if (OPEN.weekdays.includes(date.getDay())) {
        const h = document.createElement("span");
        h.className = "hrs";
        if (closed) {
          cell.classList.add("closed");
          h.textContent = closedLabel;
        } else {
          cell.classList.add("open");
          h.textContent = OPEN.from + "–" + OPEN.to;
        }
        cell.appendChild(h);
      }
      if (hol) {
        const l = document.createElement("span");
        l.className = "cal-hol";
        l.textContent = text(hol);
        cell.appendChild(l);
      }
      EVENTS.filter((e) => e.date === k).forEach((e) => {
        const ev = document.createElement(e.link ? "a" : "span");
        ev.className = "cal-ev";
        ev.textContent = text(e);
        ev.title = text(e) + (e.time ? " · " + e.time : "");
        if (e.link) setLink(ev, e.link);
        cell.appendChild(ev);
      });
      grid.appendChild(cell);
    }
  }

  document.getElementById("cal-prev").onclick = () => { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); render(); };
  document.getElementById("cal-next").onclick = () => { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); render(); };
  render();

  const upcoming = EVENTS.filter((e) => e.date >= key(now)).sort((a, b) => a.date.localeCompare(b.date));
  if (upcoming.length) {
    document.getElementById("cal-upcoming").hidden = false;
    const ul = document.getElementById("cal-upcoming-list");
    upcoming.forEach((e) => {
      const li = document.createElement("li");
      const [yy, mm, dd] = e.date.split("-").map(Number);
      const name = document.createElement(e.link ? "a" : "strong");
      name.textContent = text(e);
      if (e.link) setLink(name, e.link);
      const when = document.createElement("span");
      when.textContent = " · " + dayFmt.format(new Date(yy, mm - 1, dd)) + (e.time ? " · " + e.time : "");
      li.append(name, when);
      ul.appendChild(li);
    });
  }
})();
