#!/usr/bin/env python3
"""Aktualisiert data/shorts.json aus dem YouTube-Feed des Kanals.

Laeuft taeglich per GitHub Actions (.github/workflows/shorts.yml).
- "monatsrueckblick": neuestes Short, dessen Titel "Monatsrückblick" enthaelt.
  Der Wert bleibt gespeichert, auch wenn das Video spaeter aus dem Feed
  (nur die letzten 15 Videos) herausfaellt.
- "neuestes_short": neuestes Short ueberhaupt (Ersatz, solange es noch
  keinen Monatsrueckblick gibt).
Nur Python-Standardbibliothek, kein API-Schluessel noetig.
"""
import json
import pathlib
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CHANNEL_ID = "UCcYZMyyNdKHBWNm7S7e4efg"   # YouTube: Kikoll_Finanzblick
SUCHWORT = "monatsruckblick"              # "Monatsrückblick" ohne Umlaut, klein
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
ZIEL = pathlib.Path(__file__).resolve().parent.parent / "data" / "shorts.json"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def normal(text: str) -> str:
    """Kleinbuchstaben, Umlaute vereinfacht (ü -> u, ue -> u)."""
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.replace("ue", "u").replace("-", "").replace(" ", "")


def lade_feed(url: str = FEED) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "finanzblick-website/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    videos = []
    for e in root.findall("a:entry", NS):
        link = e.find("a:link", NS).get("href", "")
        videos.append({
            "id": e.findtext("yt:videoId", namespaces=NS),
            "titel": e.findtext("a:title", namespaces=NS),
            "veroeffentlicht": e.findtext("a:published", namespaces=NS),
            "ist_short": "/shorts/" in link,
        })
    videos.sort(key=lambda v: v["veroeffentlicht"], reverse=True)
    return videos


def eintrag(v: dict | None) -> dict | None:
    if not v:
        return None
    return {"id": v["id"], "titel": v["titel"], "veroeffentlicht": v["veroeffentlicht"]}


def main() -> int:
    alt = {}
    if ZIEL.exists():
        alt = json.loads(ZIEL.read_text(encoding="utf-8"))
    try:
        videos = lade_feed()
    except Exception as err:  # Feed kurz nicht erreichbar: alte Datei behalten
        print(f"Feed nicht erreichbar, nichts geaendert: {err}", file=sys.stderr)
        return 0

    shorts = [v for v in videos if v["ist_short"]]
    neu_monat = next((v for v in shorts if SUCHWORT in normal(v["titel"])), None)
    monat = eintrag(neu_monat)
    alt_monat = alt.get("monatsrueckblick")
    if alt_monat and (not monat or alt_monat["veroeffentlicht"] > monat["veroeffentlicht"]):
        monat = alt_monat  # gespeicherten (neueren) Monatsrueckblick behalten

    daten = {
        "kanal": f"https://www.youtube.com/channel/{CHANNEL_ID}",
        "monatsrueckblick": monat,
        "neuestes_short": eintrag(shorts[0] if shorts else None) or alt.get("neuestes_short"),
    }
    vergleich = {k: v for k, v in alt.items() if k != "geaendert"}
    if vergleich == daten:
        print("Keine Aenderung.")
        return 0
    daten["geaendert"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Aktualisiert:", json.dumps(daten, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
