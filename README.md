# Shop-Analyse Plattenleger

Scrape der Shop-Kategorie «Plattenleger» (shop.ferronato.ch, Stand 18.08.2026), Neukategorisierung aus Sicht der Zielgruppe und Top-Produkte pro Kategorie.

- `deliverable/Ferronato_Plattenleger_Sortiment.html`: interaktive Übersicht (Suche, Filter), lokal im Browser öffnen
- `deliverable/ferronato_plattenleger_produkte.xlsx`: Excel (Blätter: Alle Produkte, Top-Produkte, Kategorien)
- `docs/taxonomie.md`: neue Kategorienstruktur mit Regeln
- `data/final.json`, `products_raw.json`: Rohdaten und Ergebnis
- `scripts/`: `scrape.py` (Scraper), `build_excel.py`, `build_html.py`

Ablauf: `python3 scripts/scrape.py data/products_raw.json`, Kategorisierung/Texte via Agenten, dann `build_excel.py` und `build_html.py` (venv mit `openpyxl`).
