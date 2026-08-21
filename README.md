# Shop-Analyse Ferronato

Scrape der Shop-Kategorie «Plattenleger» (shop.ferronato.ch, Stand 18.08.2026), Neukategorisierung aus Sicht der Zielgruppe und Top-Produkte pro Kategorie.

- `deliverable/Ferronato_Plattenleger_Sortiment.html`: interaktive Übersicht (Suche, Filter), lokal im Browser öffnen
- `deliverable/ferronato_plattenleger_produkte.xlsx`: Excel (Blätter: Alle Produkte, Top-Produkte, Kategorien)
- `docs/taxonomie.md`: neue Kategorienstruktur mit Regeln
- `data/final.json`, `products_raw.json`: Rohdaten und Ergebnis
- `scripts/`: `scrape.py` (Scraper), `build_excel.py`, `build_html.py`

Ablauf: `python3 scripts/scrape.py data/products_raw.json`, Kategorisierung/Texte via Agenten, dann `build_excel.py` und `build_html.py` (venv mit `openpyxl`).

## Gesamtshop (21.08.2026)
- `deliverable/Ferronato_Sortiments_Kompass.html`: interaktive Übersicht des ganzen Shops (1624 Produkte, 6 Sparten, 14 Hauptkategorien, 221 Top-Produkte)
- `deliverable/ferronato_gesamtshop_produkte.xlsx` / `.csv`: Excel-Export
- `docs/taxonomie_shop.md`: Taxonomie v2 mit korrigiertem Scoring nach Kundenfeedback (Bestseller: Proxxon/Distar Starter Set, Butterfly DTS, Colour Bond, Jollynator, Ferrix Trockenbohrkronen)
- Scripts: `scrape_all.py`, `build_excel_shop.py`, `build_html_shop.py`
