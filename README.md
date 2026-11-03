# kikoll_finanzblick – Website

Statische Website für GitHub Pages (kostenlos).

- `index.html` – Startseite mit Kanälen, Monatsrückblick-Short, Empfehlungen, Impressum (`#impressum`) und Datenschutz (`#datenschutz`)
- `data/shorts.json` – neuestes Monatsrückblick-Short; wird von `.github/workflows/shorts.yml` alle 6 Stunden aktualisiert
- `scripts/update_shorts.py` – liest den YouTube-Feed (kein API-Schlüssel nötig)

Vor dem Start ersetzen: Max-Mustermann-Daten im Impressum und in der Datenschutzerklärung, Beispiel-Affiliate-Links (`https://example.com/...`).

Schrift: Barlow, SIL Open Font License (`fonts/OFL.txt`).
