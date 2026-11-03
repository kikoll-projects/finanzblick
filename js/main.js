// kikoll_finanzblick – Short laden (erst nach Klick) und Fenster schließen
(function () {
  "use strict";

  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Impressum/Datenschutz schließen, ohne dass die Seite nach oben springt
  function schliessen(e) {
    if (!/^#(impressum|datenschutz)$/.test(location.hash)) return;
    if (e) e.preventDefault();
    var y = window.scrollY;
    location.hash = "";
    window.scrollTo(0, y);
  }
  document.querySelectorAll('a[href="#impressum"], a[href="#datenschutz"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var y = window.scrollY;
      location.hash = a.getAttribute("href");
      window.scrollTo(0, y);
      var box = document.querySelector(a.getAttribute("href") + " .modal-close");
      if (box) box.focus({ preventScroll: true });
    });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") schliessen(); });
  document.querySelectorAll(".modal-close, .modal-backdrop").forEach(function (a) {
    a.addEventListener("click", schliessen);
  });

  var btn = document.getElementById("load-short");
  var titleEl = document.getElementById("short-title");
  var metaEl = document.getElementById("short-meta");
  var player = document.getElementById("player");
  if (!btn || !player) return;

  function datum(iso) {
    try {
      return new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "long", year: "numeric" });
    } catch (e) { return ""; }
  }

  function sauber(titel) {
    return (titel || "").replace(/\s*#shorts\s*/gi, " ").trim();
  }

  fetch("data/shorts.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (d) {
      var video = d.monatsrueckblick || d.neuestes_short;
      if (!video || !/^[\w-]{11}$/.test(video.id)) throw new Error("kein Video");
      var istMonat = !!d.monatsrueckblick;
      titleEl.textContent = sauber(video.titel);
      metaEl.textContent = (istMonat ? "Monatsrückblick vom " : "Neuestes Short vom ") + datum(video.veroeffentlicht);
      btn.disabled = false;
      btn.addEventListener("click", function () {
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + video.id + "?autoplay=1&rel=0&playsinline=1&modestbranding=1";
        f.title = sauber(video.titel);
        f.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share";
        f.allowFullscreen = true;
        f.referrerPolicy = "strict-origin-when-cross-origin";
        player.innerHTML = "";
        player.appendChild(f);
      }, { once: true });
    })
    .catch(function () {
      titleEl.textContent = "Shorts auf YouTube";
      btn.disabled = false;
      btn.textContent = "Zum YouTube-Kanal";
      btn.addEventListener("click", function () {
        window.open("https://www.youtube.com/channel/UCcYZMyyNdKHBWNm7S7e4efg", "_blank", "noopener");
      });
    });
})();
