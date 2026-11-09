// Volunteer popup: opens once automatically (10s after load or at ~half-page scroll),
// then stays quiet for 14 days on that device. Links with [data-volunteer] reopen it.
(function () {
  const dlg = document.getElementById("volunteer-dialog");
  if (!dlg || typeof dlg.showModal !== "function") return;
  const KEY = "volunteerPopupClosedAt", QUIET_DAYS = 14, DELAY_MS = 10000;

  const recentlyClosed = () => {
    try { return Date.now() - Number(localStorage.getItem(KEY)) < QUIET_DAYS * 864e5; }
    catch (e) { return false; }
  };
  const open = () => { if (!dlg.open) dlg.showModal(); };

  dlg.addEventListener("close", () => {
    try { localStorage.setItem(KEY, String(Date.now())); } catch (e) {}
  });
  dlg.querySelector(".vol-close").addEventListener("click", () => dlg.close());
  // click on the backdrop (the dialog element itself, outside its content box) closes it
  dlg.addEventListener("click", (e) => {
    if (e.target !== dlg) return;
    const r = dlg.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dlg.close();
  });
  document.querySelectorAll("[data-volunteer]").forEach((a) =>
    a.addEventListener("click", (e) => { e.preventDefault(); open(); }));

  if (recentlyClosed()) return;
  let done = false;
  const auto = () => {
    if (done) return;
    done = true;
    clearTimeout(timer);
    window.removeEventListener("scroll", onScroll);
    open();
  };
  const onScroll = () => {
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight / 2) auto();
  };
  const timer = setTimeout(auto, DELAY_MS);
  window.addEventListener("scroll", onScroll, { passive: true });
})();
