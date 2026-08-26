# Ziel-Taxonomie Gesamtshop Ferronato (Sortiments-Kompass v2)

Überarbeitet 2026-08-26 nach der Korrekturanweisung von Chris Beyeler:
mehrdimensionale Produkttaxonomie statt reinem Ordnerbaum. Ein Produkt hat
genau eine Primär-Berufsgruppe und eine Primär-Tätigkeit, erscheint aber
zusätzlich überall dort, wo es fachlich hingehört (Marke, System, Material,
Zusatz-Tätigkeiten). Pipeline: `scripts/classify_kompass.py` →
`data/kompass.json` → `scripts/build_kompass.py` →
`deliverable/Ferronato_Sortiments_Kompass.html`. QC: `scripts/qc_kompass.py`
(15 Punkte gemäss Anweisung).

## Berufsgruppen (Schweizer Sprachgebrauch, allumfassend)
- Plattenleger
- Steinmetz & Bildhauer (inkl. Grabschmuck, Steinbearbeitung, Töpfern/Keramik)
- Natursteinwerk (stationäre Steinbearbeitung: CNC-Werkzeuge, Brücken-/
  Tischsägen und -fräsen, Schleifringe & Schleifsegmente für
  Kantenschleifmaschinen; ergänzt 2026-08-26)
- Gartenbau, Pflästerung & Tiefbau (vorher «GaLa-Bau & Tiefbau»)
- Gipser & Betonkosmetik
- Carrosserie & Fahrzeugaufbereitung (vorher «Autogewerbe»)
- Holzbearbeitung & Zimmerei (Latthämmer, Stich-/Säbel-/Kapp- und
  Gehrungssägen, Oberfräsen, Zimmermannsbedarf; ergänzt 2026-08-26.
  CH-Sprachgebrauch: «Zimmerei»/«Zimmermann EFZ», Branchenbegriff «Holzbau»)
- Werkstatt & Baustelle (PSA, Universalmaschinen, Baustellenbedarf; Shop-Name
  für die frühere Sparte «Übergreifend», Entscheid Chris Beyeler 2026-08-26)

Natursteinwerk und Holzbearbeitung & Zimmerei sind Sekundärgruppen: Sie werden
über Mehrfachzuordnung befüllt, die Produkte behalten ihre Primärgruppe.

## Tätigkeiten (Hauptkategorien)
| Tätigkeit | Bemerkung |
|---|---|
| Messen & Anzeichnen | |
| Trennen & Schleifen | ersetzt «Schneiden & Trennen» und «Schleifen, Kanten & Polieren». Untergruppen: Trennen · Schleifen · Trennen & Schleifen · Polieren · Aufnahmeteller & Adapter. Zuordnung nach tatsächlicher Anwendung, nicht nach Produktname. «Schneiden» wird als Begriff nicht mehr verwendet. |
| Bohren & Fräsen | |
| Verlegen, Heben & Transportieren | Untergruppen: Vakuumsysteme · Greif- & Zangensysteme · Planum & Abziehsysteme · Verlegewerkzeuge & Pflaster · Transport & Hebezeuge. Vakuum und mechanisches Greifen strikt getrennt. |
| Kleben, Fugen & Gehrung | |
| Reinigen, Schützen & Reparieren | |
| Staub & Absaugung | |
| Maschinen & Geräte | ersetzt «Maschinen & Energie» («Energie» entfernt). Untergruppen nach Antriebsart: Akku-Maschinen · Elektrische Maschinen (230 V) · Druckluft-Maschinen · Benzin-Maschinen · Akkus & Ladegeräte · Maschinenzubehör & Ersatzteile. |
| Arbeitsschutz (PSA) | |
| Baustellen- & Werkstattbedarf | Hämmer getrennt: Bau- & Baustellenhämmer vs. Steinmetz- & Bildhauerhämmer (Fäustel, Knüpfel, Schrifthämmer, PL-/Pressluft-Hämmer). |
| Sanitär- & Montagesysteme | |
| Lackieren & Beschichten | |
| Modellieren & Formen | |

## Dimensionen pro Produkt (Mehrfachzuordnung erwünscht)
- **Marke:** eindeutig ein Hersteller (FLEX, PROBST, AKEMI, DISTAR, PROXXON,
  KNIPEX, Norton, FEIN …) oder «Ferronato-Eigenmarken» (FERRIX, FERLOX,
  FERROSIL, FERBAC, FERROBLACK, FERROLIT, FERROFLEX, FERRAMICS, FERRIT).
  FLEX und PROBST werden nie vermischt; Produktlinien ohne Markennennung sind
  hinterlegt (Butterfly → DISTAR). Darstellung: innerhalb jeder Untergruppe
  nach Marke gruppiert.
- **Materialien (mehrere möglich):** Keramik, Feinsteinzeug, UCS/Ultracompact
  (inkl. Dekton, Neolith — separat von Feinsteinzeug), Granit, Marmor,
  Kalkstein, Sandstein, Schiefer, Quarzit, Porphyr, Terrazzo, Naturstein
  (allgemein), Kunststein & Komposit, Beton, Frischbeton, Altbeton, Backstein,
  Ziegel & Klinker, Kalksandstein, Mauerwerk, Glas, Gips, Asphalt, Metall,
  Holz, Ton & Keramikmasse.
- **Antrieb:** Akku · Elektrisch 230 V · Druckluft · Benzin.
- **Aufnahme:** M14, M16, X-LOCK, SDS, Klett, Bohrung 22,23/25,4 mm,
  Einsteckende (Pressluft), Sechskant.
- **System:** PROXXON/DISTAR-Trennsystem, Colour Bond & Jollynator (Gehrung),
  StoneLux-Reparatursystem, Ferrix-Trockenbohrkronen, Vakuum-System,
  AKEPOX-Klebesystem. Systemzubehör (Aufnahmeteller, Adapter) erscheint bei
  allen relevanten Anwendungen.

## Priorisierung (manuell, Entscheid Ferronato)
Die automatischen Top-1-bis-Top-6-Ränge sind entfernt. Jedes Produkt trägt ein
manuell editierbares Feld: Prio 1 · Prio 2 · Prio 3 · Irrelevant · (leer =
noch nicht bewertet). Keine automatische Vergabe nach Preis, Menge oder
geschätzter Relevanz. Gespeichert im Browser (localStorage), exportierbar als
JSON über «Stand exportieren».

## Regeln
- Keine Zuordnung raten: Produkte mit unklarer Datenlage tragen die Kennzeichnung
  «Zuordnung prüfen» (mit Begründung) und sammeln sich in einer eigenen Ansicht.
- Kein Produkt, Preis, Shoplink oder Beschreibungstext geht verloren
  (QC-Punkt 15: 1624/1624).
- Zubehör und Verbrauchsmaterial wandert zur Anwendung, nicht in einen
  Zubehör-Topf; bei mehreren Anwendungen Mehrfachanzeige.
- Werkstatt & Baustelle bleibt das primäre Zuhause übergreifender Produkte;
  kaufrelevante Artikel werden per Mehrfachzuordnung zusätzlich in die
  passenden Berufsgruppen gehängt, gepflegt wird nur die Primärkategorie.
