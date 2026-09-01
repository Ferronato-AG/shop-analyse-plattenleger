#!/usr/bin/env python3
"""Mehrdimensionale Klassifikation der 1624 Ferronato-Produkte.

Leitet aus den vorhandenen Produktdaten (sfinal.json + all_products_raw.json)
konservativ und regelbasiert ab: Marke, Tätigkeit, Untergruppe, Materialien,
Antrieb, Aufnahme, System. Nichts wird geraten: Wo die Datenlage nicht
eindeutig ist, wird das Produkt als «Zuordnung prüfen» markiert.

Output: data/kompass.json (ein Objekt pro Produkt, alle Dimensionen).
"""
import json
import re
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- Berufsgruppen
# Schweizer Sprachgebrauch, allumfassend formuliert (Korrekturanweisung Pkt. 2)
SPARTE_NEU = {
    'Plattenleger': 'Plattenleger',
    'Steinmetz & Bildhauer': 'Steinmetz & Bildhauer',
    'GaLa-Bau & Tiefbau': 'Gartenbau, Pflästerung & Tiefbau',
    'Gipser & Betonkosmetik': 'Gipser, Maler & Betonkosmetik',
    'Autogewerbe': 'Carrosserie & Fahrzeugaufbereitung',
    'Übergreifend': 'Werkstatt & Baustelle',
    'Werkstatt & Baustelle': 'Werkstatt & Baustelle',
}

# ---------------------------------------------------------- Zusatz-Berufsgruppen
# «Natursteinwerk» und «Holzbearbeitung & Zimmerei» sind Zielgruppen ohne
# eigene Primärprodukte im Datenbestand: Produkte behalten ihre Primärgruppe
# und erscheinen zusätzlich hier (Mehrfachzuordnung, Entscheid 2026-08-26).
NW_TYPEN = {'Trennscheiben Brücken- & Tischsäge', 'Trennscheiben Brücken-/Tischfräsen',
            'Trennscheiben Grossformat', 'Schleifringe & Schleifsegmente',
            'Sichtschleifmaschinen', 'Sichtschleifscheiben'}
RX_NATURSTEINWERK = re.compile(
    r'\bCNC\b|Tischfräse|Steinfräse|Brückensäge|Brückenfräs|Fingerfräs|Finger Bit|'
    r'Profilfräs|Umfangfräs|Falzfräser|Cassani|Seilsäge|Kantenschleifmaschine', re.I)
# Ein Natursteinwerk deckt die ganze Verarbeitungskette im Werk ab: Sägen,
# Fräsen, Schleifen/Polieren, Bohren, Kleben, Oberflächenschutz/Reparatur,
# Maschinen, Absaugung, Messen, Plattenhandling. Nicht dazu gehören das
# bildhauerische Handwerkzeug (Handeisen, Raspeln, Knüpfel), Ton/Modelliermasse
# sowie Grabschmuck/Beschriftung von Hand.
NW_WERK_TAETIGKEITEN = {
    'Trennen & Schleifen', 'Bohren & Fräsen', 'Kleben, Fugen & Gehrung',
    'Reinigen, Schützen & Reparieren', 'Maschinen & Geräte',
    'Staub & Absaugung', 'Messen & Anzeichnen',
    'Verlegen, Heben & Transportieren',
}
# Maschinelle Oberflächenbearbeitung (stocken, scharrieren mit Pressluft)
# gehört ebenfalls ins Werk, auch wenn sie unter «Modellieren & Formen» läuft.
NW_OBERFLAECHEN_TYPEN = {'Presslufteisen (Spitz-, Schlag- & Zahneisen)',
                         'Pressluft-Schrifteisen', 'Stockwerkzeuge'}

RX_HOLZ = re.compile(
    r'Latthammer|Zimmerman|Stichsäge|Kapp- ?und ?Gehrung|Säbelsäge|Oberfräse|'
    r'Holzbürst|Holzbohrer|Forstner|Schlagschnur|(?<![A-Za-z])E-Cut(?!.*Metall)|'
    r'Kantenfräser.*Oberfräs|Kettensäge|Multitool|Zimmermannsbleistift', re.I)


def ist_holzbau(p):
    n = p['name']
    if RX_HOLZ.search(n):
        return True
    # Kreissägen und Sägeblätter für Holz (Metall- und Nass-/Steinsägen nicht)
    if re.search(r'kreissäge', n, re.I) and not re.search(r'metall|nass|\bwet\b', n, re.I):
        return True
    # Akku-Montagegeräte (Bohr-/Schlagschrauber), Kernwerkzeug im Holzbau
    if re.search(r'bohrschrauber|schlagschrauber|akku.?schrauber', n, re.I) \
            and not re.search(r'trockenbau', n, re.I):
        return True
    if re.search(r'\btacker\b', n, re.I):
        return True
    if re.search(r'hobel', n, re.I) and not re.search(r'stonelux|\bslx\b|akemi|composite', n, re.I):
        return True
    return False


# ------------------------------------------- Gipser, Maler & Betonkosmetik
# Kuratierte Gruppen-Ansicht nach dem Umsetzungsprotokoll Ferronato
# (2026-09-01). Die Ansicht zeigt NUR relevante Produkte, mit eigenen
# Tätigkeits-/Untergruppen-Namen («Bohren & Meisseln» statt «Bohren & Fräsen»,
# keine Maschinen unter Trennen/Schleifen, Manta XR nicht unter Staub &
# Absaugung). Interpretationen des diktierten Protokolls: «Ferro-Seal» =
# FERROSIL-Bänder/-Folien, «Acemi» = AKEMI.
GIPSER_NAME = 'Gipser, Maler & Betonkosmetik'

RX_GIPSER_MASCHINE = re.compile(
    r'giraffe|betonschleifer|deckenschleifer|schwingschleifer|'
    r'bodenschleifmaschine|sanierungsschleifer|winkelschleifer|polierer|'
    r'rührmaschine|rührer|glättbohle|\bLD ?\d+-\d', re.I)


def gipser_view(p, taetigkeit, untergruppe, antrieb, systeme, marke):
    """Liefert (Tätigkeit, Untergruppe) der Gipser-Ansicht oder None."""
    n = p['name']
    typ = p['unterkategorie']
    primaer = p['sparte'] == 'Gipser & Betonkosmetik'

    def maschinen_ug():
        if 'Akku' in antrieb:
            return 'Akku-Maschinen'
        if 'Benzin' in antrieb:
            return 'Benzin-Maschinen'
        return 'Elektrische Maschinen (230 V)'

    # Manta XR: raus aus Staub & Absaugung (Protokoll)
    if re.search(r'manta xr', n, re.I):
        if re.search(r'absaughaube', n, re.I):
            return ('Maschinen & Geräte', 'Maschinenzubehör & Hilfsmittel')
        return ('Maschinen & Geräte', maschinen_ug())
    # Maschinen nie unter Trennen/Schleifen (Protokoll), inkl. FLEX Giraffe
    if primaer and RX_GIPSER_MASCHINE.search(n):
        return ('Maschinen & Geräte', maschinen_ug())
    # Trennen & Schleifen (kuratiert)
    if primaer and untergruppe == 'Trennen':
        return ('Trennen & Schleifen', 'Trennscheiben')
    if primaer and untergruppe == 'Trennen & Schleifen':
        return ('Trennen & Schleifen', 'Trenn- & Schleifscheiben')
    if re.search(r'handrutscher|rutscherplatte|diamantrutscher', n, re.I):
        return ('Trennen & Schleifen', 'Handrutscher')
    if re.search(r'telum|swiflex|\bsda\b', n, re.I) \
            or re.search(r'FLEX Schleifmittel Starter', n, re.I):
        return ('Trennen & Schleifen', 'Schleifmittel')
    if untergruppe == 'Aufnahmeteller & Adapter' \
            and re.search(r'ø ?(100|115|120|140)', n, re.I):
        return ('Trennen & Schleifen', 'Aufnahmeteller')
    if typ == 'Giraffen-Schleifmittel' or re.search(r'giraffen', typ, re.I) \
            and not RX_GIPSER_MASCHINE.search(n):
        return ('Trennen & Schleifen', 'Giraffen-Schleifmittel')
    if re.search(r'ø ?225|225 ?mm', n, re.I) and re.search(r'schleif|dämpfung|vlies', n, re.I):
        return ('Trennen & Schleifen', 'Giraffen-Schleifmittel')
    if primaer and re.search(r'schleifteller|schleiftopf', n, re.I):
        return ('Trennen & Schleifen', 'Schleifwerkzeuge Ø 180/225')
    # Bohren & Meisseln (umbenannt, Protokoll)
    if re.search(r'meissel', n, re.I) and 'SDS' in n.upper() or typ == 'Bohrhämmer & Meissel' and re.search(r'meissel', n, re.I):
        return ('Bohren & Meisseln', 'Meissel')
    if re.search(r'bohrhammer|kombihammer|kombibohr|schlagbohrmaschine', n, re.I):
        return ('Bohren & Meisseln', 'Bohrhämmer')
    if re.search(r'bohrschrauber|schlagschrauber|trockenbauschrauber', n, re.I):
        return ('Bohren & Meisseln', 'Schlagbohrschrauber')
    if primaer and p['hauptkategorie'][:2] == '03':
        return ('Bohren & Meisseln', 'Werkzeuge & Zubehör')
    # Baustellen- & Werkstattbedarf
    if re.search(r'gipserbeil|\bbeil\b|latthammer', n, re.I):
        return ('Baustellen- & Werkstattbedarf', 'Baustellenwerkzeuge')
    if re.search(r'tischfräse', n, re.I):
        return ('Baustellen- & Werkstattbedarf', 'Baustellenmaschinen')
    if primaer and taetigkeit == 'Baustellen- & Werkstattbedarf':
        return ('Baustellen- & Werkstattbedarf', 'Werkstatt')
    # Kleben, Fugen & Gehrung
    if re.search(r'kartuschen ?presse|skelettpistole|klebepistole|presspistole', n, re.I):
        return ('Kleben, Fugen & Gehrung', 'Kartuschenpressen & Klebepistolen')
    if re.search(r'weiss.?chemie|cosmo(?!s)|hd-?100|akenova|silikon(?!-schleif)|dichtstoff', n, re.I) \
            and not re.search(r'psa|halbmaske|schleifleinen|tabelle', n, re.I):
        return ('Kleben, Fugen & Gehrung', 'Kleb- & Dichtstoffe')
    if re.search(r'colour ?bond|spectrum|platinum', n, re.I):
        return ('Kleben, Fugen & Gehrung', 'Gehrungen')
    if re.search(r'japanspachtel|malerspachtel|künstlerspachtel|milani.?spachtel|'
                 r'gipsraspel|stukkateurspachtel|anmischplatte|misch-?messbecher', n, re.I):
        return ('Kleben, Fugen & Gehrung', 'Spachtel & Werkzeuge')
    if primaer and taetigkeit == 'Kleben, Fugen & Gehrung':
        return ('Kleben, Fugen & Gehrung', 'Kleb- & Dichtstoffe')
    # Lackieren & Beschichten
    if typ == 'Betonpigmente' or re.search(r'pulverfarbe|pigment', n, re.I):
        return ('Lackieren & Beschichten', 'Pigmente')
    if re.search(r'farbtonvertiefer', n, re.I):
        return ('Lackieren & Beschichten', 'Imprägnierungen & Farbtonvertiefer')
    # Reinigen, Schützen & Reparieren
    if re.search(r'abdeckfolie|abdeckvlies|abdeckband|floorliner|malerband|speedymask', n, re.I):
        return ('Reinigen, Schützen & Reparieren', 'Abdeckfolien & -materialien')
    if re.search(r'klebeband|bautenschutzband|gewebeband', n, re.I):
        return ('Reinigen, Schützen & Reparieren', 'Schutz- & Klebebänder')
    if re.search(r'smart repair', n, re.I) or 'StoneLux-Reparatursystem' in systeme:
        return ('Reinigen, Schützen & Reparieren', 'Reparaturwerkzeuge & -systeme')
    if primaer and taetigkeit == 'Reinigen, Schützen & Reparieren':
        return ('Reinigen, Schützen & Reparieren', 'Reinigen & Imprägnieren')
    # Staub & Absaugung (nur FLEX plus Masken, Protokoll)
    if marke == 'FLEX':
        zubehoer = re.search(r'filtersä?ck|filter\b|flachfaltenfilter|reinigungsset|'
                             r'trolley|fahrwerk|vorabschneider|cyclone|absaughaube|'
                             r'absaugschlauch|saugschlauch', n, re.I)
        ist_sauger = re.search(r'sauger', n, re.I) \
            or (re.search(r'\bVC[EL]? ?\d', n) and not zubehoer)
        if ist_sauger:
            return ('Staub & Absaugung', 'Staubsauger')
        if zubehoer:
            return ('Staub & Absaugung', 'Absaugzubehör')
    if re.search(r'moldex|staubmaske|feinstaubmaske|staub-halbmaske', n, re.I):
        return ('Staub & Absaugung', 'Staubmasken')
    # Übrige Primär-Gipser-Produkte: Tätigkeit behalten
    if primaer:
        t = 'Bohren & Meisseln' if taetigkeit == 'Bohren & Fräsen' else taetigkeit
        if taetigkeit == 'Maschinen & Geräte':
            ug = untergruppe if untergruppe != 'Maschinenzubehör & Ersatzteile' \
                else 'Maschinenzubehör & Hilfsmittel'
            return (t, ug)
        return (t, untergruppe)
    return None


# Primärgruppen-Korrekturen (Feedback Denis/Ferronato 2026-08-27):
# CNC-Fräswerkzeuge laufen auf festmontierten Maschinen mit Wasserzuführung
# (Steinarbeiten) und gehören nicht zum Plattenleger → Primärgruppe
# Natursteinwerk.
def primaergruppe_korrektur(p, berufsgruppe):
    if berufsgruppe == 'Plattenleger' and p['unterkategorie'] == 'CNC-Fräswerkzeuge':
        return 'Natursteinwerk'
    return berufsgruppe


def zusatz_gruppen_von(p, taetigkeit):
    out = []
    ist_steinmetz = p['sparte'] == 'Steinmetz & Bildhauer'
    if (p['unterkategorie'] in NW_TYPEN or RX_NATURSTEINWERK.search(p['name'])
            or (ist_steinmetz and taetigkeit in NW_WERK_TAETIGKEITEN)
            or (ist_steinmetz and p['unterkategorie'] in NW_OBERFLAECHEN_TYPEN)):
        out.append('Natursteinwerk')
    if ist_holzbau(p):
        out.append('Holzbau & Zimmerei')
    return out


# ---------------------------------------------------------------- Marken
EIGENMARKEN = ['FERRIX', 'FERLOX', 'FERROSIL', 'FERBAC', 'FERROBLACK',
               'FERROLIT', 'FERROFLEX', 'FERRAMICS', 'FERRIT', 'FERROSTAR']
FREMDMARKEN = ['FLEX', 'PROBST', 'AKEMI', 'FEIN', 'PROXXON', 'DISTAR', 'KGS',
               'REXID', 'BETCUT', 'HUSQVARNA', 'MILANI', 'STONELUX', 'HALDER',
               'PICARD', 'KRAFTWERK', 'FELDMÜHLE', 'FELDMUEHLE', 'SIMPLEX',
               'CUTURI', 'LYRA', 'GUILLET', 'DUSS', 'ALMI', 'NEMO', 'NORTON',
               'GENTILIN', 'METABO', 'BOSCH', 'KNIPEX', 'MAKITA', 'SIGMA',
               'BEKA', 'RUTHE', 'OCHSENKOPF', 'STUBAI', 'BELLOTA']
MARKEN_ANZEIGE = {'FELDMUEHLE': 'FELDMÜHLE', 'HUSQVARNA': 'Husqvarna',
                  'STONELUX': 'StoneLux', 'MILANI': 'Milani', 'LYRA': 'Lyra',
                  'GUILLET': 'Guillet', 'RUTHE': 'Ruthe', 'BEKA': 'BEKA'}

# AKEMI-Produktlinien bleiben unter AKEMI
AKEMI_LINIEN = ['AKEPOX', 'COLOUR BOND', 'MARMORKITT', 'AKESTONE', 'TRIPLE EFFECT']


# Produktlinien ohne Markennennung im Namen → eindeutige Marke
# (Kundenfeedback: Butterfly gehört zu DISTAR)
LINIEN_MARKE = {'BUTTERFLY': 'DISTAR'}


def _marken_treffer(text_upper):
    """Frühester Marken-Treffer im Text gewinnt (Kombinationsnamen wie
    «DISTAR Spraynozzle … - Proxxon» gehören zur zuerst genannten Marke)."""
    best = None
    for m in EIGENMARKEN + FREMDMARKEN + list(LINIEN_MARKE):
        hit = re.search(r'(?<![A-ZÄÖÜ])' + re.escape(m) + r'(?![A-ZÄÖÜ])', text_upper)
        if hit and (best is None or hit.start() < best[0]):
            best = (hit.start(), LINIEN_MARKE.get(m, m))
    return best[1] if best else None


def marke_von(name, beschreibung):
    m = _marken_treffer(' ' + name.upper() + ' ')
    if not m:
        up_name = ' ' + name.upper() + ' '
        if any(l in up_name for l in AKEMI_LINIEN):
            m = 'AKEMI'
    if not m:
        # Fallback Beschreibung: nur, wenn die Marke dort exakt so geschrieben
        # steht wie im Markennamen (verhindert «fein geschliffen» → FEIN)
        desc = ' ' + (beschreibung or '') + ' '
        for kand in EIGENMARKEN + FREMDMARKEN:
            geschrieben = MARKEN_ANZEIGE.get(kand, kand)
            if re.search(r'(?<![A-Za-zÄÖÜäöü])' + re.escape(geschrieben) + r'(?![a-zäöü])', desc):
                m = kand
                break
    if not m:
        return 'Ohne Markenangabe', 'Ohne Markenangabe'
    anzeige = MARKEN_ANZEIGE.get(m, m)
    gruppe = 'Ferronato-Eigenmarken' if m in EIGENMARKEN else anzeige
    return anzeige, gruppe


# ---------------------------------------------------------------- Materialien
# (regex, Anzeigename) — Reihenfolge egal, Mehrfachzuordnung erwünscht
MATERIAL_REGELN = [
    (r'feinsteinzeug', 'Feinsteinzeug'),
    (r'\bucs\b|ultra.?compact|dekton|neolith|laminam|sapienstone', 'UCS / Ultracompact'),
    (r'keramik|fliese|steingut|steinzeug(?!.*fein)', 'Keramik'),
    (r'granit', 'Granit'),
    (r'marmor', 'Marmor'),
    (r'kalkstein', 'Kalkstein'),
    (r'sandstein', 'Sandstein'),
    (r'schiefer', 'Schiefer'),
    (r'quarzit', 'Quarzit'),
    (r'porphyr', 'Porphyr'),
    (r'terrazzo', 'Terrazzo'),
    (r'frischbeton', 'Frischbeton'),
    (r'altbeton', 'Altbeton'),
    (r'(?<!frisch)(?<!alt)beton(?!kosmetik)', 'Beton'),
    (r'backstein', 'Backstein'),
    (r'ziegel|klinker', 'Ziegel & Klinker'),
    (r'kalksandstein', 'Kalksandstein'),
    (r'mauerwerk', 'Mauerwerk'),
    (r'kunststein|komposit|quarz.?komposit|engineered stone', 'Kunststein & Komposit'),
    (r'naturstein|hartgestein|weichgestein', 'Naturstein (allgemein)'),
    (r'\bglas', 'Glas'),
    (r'\bgips(?!er)', 'Gips'),
    (r'asphalt', 'Asphalt'),
    (r'metall|stahl(?!fäustel)|\balu(?!minium.?oxid)', 'Metall'),
    (r'\bholz(?!stiel|griff|kohle)', 'Holz'),
    (r'\bton\b|töpfer', 'Ton & Keramikmasse'),
]


def materialien_von(text):
    t = text.lower()
    out = []
    for rx, name in MATERIAL_REGELN:
        if re.search(rx, t) and name not in out:
            out.append(name)
    return out


# ---------------------------------------------------------------- Antrieb
def antrieb_von(text):
    t = text.lower()
    out = []
    if re.search(r'\bakku|batteriebetrieb|cordless|18\s?v\b|36\s?v\b|10[.,]8\s?v\b|12\s?v\b', t):
        out.append('Akku')
    if re.search(r'230\s?v|netzbetrieb|netzkabel|wechselstrom', t):
        out.append('Elektrisch 230 V')
    if re.search(r'druckluft|pressluft|pneumat|kompressor', t):
        out.append('Druckluft')
    if re.search(r'benzin|2-takt|4-takt|verbrennungsmotor', t):
        out.append('Benzin')
    return out


# ---------------------------------------------------------------- Aufnahme
AUFNAHME_REGELN = [
    (r'm\s?14', 'M14'),
    (r'm\s?16', 'M16'),
    (r'x-?lock', 'X-LOCK'),
    (r'sds.?max', 'SDS-max'),
    (r'sds.?plus', 'SDS-plus'),
    (r'klett', 'Klett'),
    (r'22[.,]23', 'Bohrung 22,23 mm'),
    (r'25[.,]4', 'Bohrung 25,4 mm'),
    (r'einsteckende', 'Einsteckende (Pressluft)'),
    (r'1/4["\s]?zoll|sechskant.?aufnahme', 'Sechskant 1/4"'),
]


def aufnahme_von(text):
    t = text.lower()
    return [name for rx, name in AUFNAHME_REGELN if re.search(rx, t)]


# ---------------------------------------------------------------- Systeme
SYSTEM_REGELN = [
    (r'proxxon|distar', 'PROXXON/DISTAR-Trennsystem'),
    (r'colour\s?bond|jollynator', 'Colour Bond & Jollynator (Gehrung)'),
    (r'stonelux|\bslx\b', 'StoneLux-Reparatursystem'),
    (r'trockenbohrkrone', 'Ferrix-Trockenbohrkronen'),
    (r'vakuum', 'Vakuum-System'),
    (r'akepox', 'AKEPOX-Klebesystem'),
]


def systeme_von(text):
    t = text.lower()
    return [name for rx, name in SYSTEM_REGELN if re.search(rx, t)]


# ---------------------------------------------------------------- Tätigkeiten
# Neue Hauptstruktur (ohne «Schneiden», ohne «Energie»)
TAETIGKEIT_MAP = {
    '01': 'Messen & Anzeichnen',
    '02': 'Trennen & Schleifen',
    '03': 'Bohren & Fräsen',
    '04': 'Trennen & Schleifen',
    '05': 'Verlegen, Heben & Transportieren',
    '06': 'Kleben, Fugen & Gehrung',
    '07': 'Reinigen, Schützen & Reparieren',
    '08': 'Staub & Absaugung',
    '09': 'Maschinen & Geräte',
    '10': 'Arbeitsschutz (PSA)',
    '11': 'Baustellen- & Werkstattbedarf',
    '12': 'Sanitär- & Montagesysteme',
    '13': 'Lackieren & Beschichten',
    '14': 'Modellieren & Formen',
}
TAETIGKEIT_ORDNUNG = [
    'Messen & Anzeichnen', 'Trennen & Schleifen', 'Bohren & Fräsen',
    'Verlegen, Heben & Transportieren', 'Kleben, Fugen & Gehrung',
    'Reinigen, Schützen & Reparieren', 'Staub & Absaugung',
    'Maschinen & Geräte', 'Arbeitsschutz (PSA)',
    'Baustellen- & Werkstattbedarf', 'Sanitär- & Montagesysteme',
    'Lackieren & Beschichten', 'Modellieren & Formen',
]

RX_TRENN = re.compile(r'trennscheibe|trennen|trenn-|säge|sägeblatt|schneid|'
                      r'spalter|schere|cutter|ritz|abbruch', re.I)
RX_SCHLEIF = re.compile(r'schleif|schärf|abzieh(?:stein)?|raspel|feile|bürst|'
                        r'antik|stock(?:en|hammer|maschine|einheit)|fräskopf', re.I)
RX_POLIER = re.compile(r'polier|politur|hochglanz', re.I)
RX_AUFNAHME_TELLER = re.compile(r'aufnahmeteller|stützteller|adapter|aufnahme(dorn|flansch)|'
                                r'verlängerung|reduzier', re.I)

RX_HAMMER_STEINMETZ = re.compile(r'fäustel|knüpfel|klüpfel|klöpfel|schriftenhammer|'
                                 r'stockhammer|kipphammer|zweispitz|ritzhammer|richthammer|'
                                 r'ansetzhammer|meisselhammer|pl-hammer|presslufthammer|'
                                 r'künstler', re.I)
RX_HAMMER_BAU = re.compile(r'schonhammer|gummihammer|plattenleger.?hammer|verlegehammer|'
                           r'schlosserhammer|latthammer|maurerhammer|vorschlaghammer|'
                           r'pflasterhammer|plattenhammer', re.I)

RX_VAKUUM = re.compile(r'vakuum|saugheber|sauger(?!.*staub)|saugplatte', re.I)
RX_GREIF = re.compile(r'zange|greifer|klemm|packzange|versetz|hebezange|steinzieher|'
                      r'plattenheber|tragklaue', re.I)


def untergruppe_trennen_schleifen(p, text, flags):
    """Zuordnungsregel Pkt. 3: nach tatsächlicher Anwendung, nicht Produktname allein."""
    name_uk = p['name'] + ' ' + p['unterkategorie']
    ist_polier = bool(RX_POLIER.search(name_uk))
    ist_trenn = bool(RX_TRENN.search(name_uk))
    ist_schleif = bool(RX_SCHLEIF.search(name_uk))
    if RX_AUFNAHME_TELLER.search(p['name']):
        return 'Aufnahmeteller & Adapter'
    if ist_polier and not ist_trenn:
        return 'Polieren'
    if ist_trenn and ist_schleif:
        return 'Trennen & Schleifen'
    # Beschreibung prüft die kombinierte Anwendung (z. B. «zum Trennen und Schleifen»)
    if ist_trenn and re.search(r'(trennen und schleifen|schleifen und trennen|'
                               r'auch (?:zum )?schleifen)', text, re.I):
        return 'Trennen & Schleifen'
    if ist_trenn:
        return 'Trennen'
    if ist_schleif:
        return 'Schleifen'
    if RX_POLIER.search(text):
        return 'Polieren'
    if RX_TRENN.search(text) and RX_SCHLEIF.search(text):
        flags.append('Anwendung Trennen/Schleifen nicht eindeutig')
        return 'Trennen & Schleifen'
    if RX_TRENN.search(text):
        return 'Trennen'
    if RX_SCHLEIF.search(text):
        return 'Schleifen'
    flags.append('Anwendung Trennen/Schleifen nicht bestimmbar')
    return 'Zuordnung prüfen'


def untergruppe_verlegen(p, text, flags):
    name_uk = p['name'] + ' ' + p['unterkategorie']
    if RX_VAKUUM.search(name_uk):
        return 'Vakuumsysteme'
    if RX_GREIF.search(name_uk):
        return 'Greif- & Zangensysteme'
    if re.search(r'planum|abzieh|nivellier|richtlatte', name_uk, re.I):
        return 'Planum & Abziehsysteme'
    if re.search(r'transport|roller|wagen|karre|hebezeug|anschlagmittel|kran', name_uk, re.I):
        return 'Transport & Hebezeuge'
    if re.search(r'pflaster|verlegehammer|keil|rüttler', name_uk, re.I):
        return 'Verlegewerkzeuge & Pflaster'
    if RX_VAKUUM.search(text):
        return 'Vakuumsysteme'
    if RX_GREIF.search(text):
        return 'Greif- & Zangensysteme'
    flags.append('Verlege-Untergruppe nicht eindeutig')
    return 'Zuordnung prüfen'


def untergruppe_maschinen(p, text, antrieb, flags):
    if re.search(r'akkus? & ladegerät|ladegerät|batterielade', p['unterkategorie'] + ' ' + p['name'], re.I):
        return 'Akkus & Ladegeräte'
    if 'Akku' in antrieb:
        return 'Akku-Maschinen'
    if 'Elektrisch 230 V' in antrieb:
        return 'Elektrische Maschinen (230 V)'
    if 'Druckluft' in antrieb:
        return 'Druckluft-Maschinen'
    if 'Benzin' in antrieb:
        return 'Benzin-Maschinen'
    if re.search(r'zubehör|ersatzteil|kohlebürste|schutzhaube|führung|absaug', p['name'] + ' ' + p['unterkategorie'], re.I):
        return 'Maschinenzubehör & Ersatzteile'
    flags.append('Antriebsart nicht aus den Daten bestimmbar')
    return 'Zuordnung prüfen'


def untergruppe_baustellenbedarf(p, text, flags):
    name_uk = p['name'] + ' ' + p['unterkategorie']
    if RX_HAMMER_STEINMETZ.search(name_uk):
        return 'Steinmetz- & Bildhauerhämmer'
    if RX_HAMMER_BAU.search(name_uk) or re.search(r'hammer|fäustel', name_uk, re.I):
        return 'Bau- & Baustellenhämmer'
    if re.search(r'axt|brech|spitzeisen(?!.*bildhauer)', name_uk, re.I):
        return 'Äxte & Brechwerkzeuge'
    if re.search(r'rührwerk|rührkorb|rührquirl', name_uk, re.I):
        return 'Rührwerke & Rührkörbe'
    if re.search(r'beleucht|strom|kabelroll|verlänger', name_uk, re.I):
        return 'Baustellenbeleuchtung & Strom'
    if re.search(r'koffer|transport|tasche|kissen|lager', name_uk, re.I):
        return 'Transport- & Koffersysteme'
    if re.search(r'entsorgung|big.?bag|reinigungspapier', name_uk, re.I):
        return 'Entsorgung & Verbrauchsmaterial'
    return 'Werkstatt & Handwerkzeug'


def klassifiziere(p, r):
    text = ' '.join([p['name'], p.get('zusammenfassung', ''), p.get('usp', ''),
                     r.get('description') or '',
                     ' '.join(r.get('breadcrumb') or []),
                     ' '.join(r.get('cat_names') or [])])
    flags = []
    hk_nr = p['hauptkategorie'][:2]
    taetigkeit = TAETIGKEIT_MAP[hk_nr]
    marke, marken_gruppe = marke_von(p['name'], r.get('description') or '')
    antrieb = antrieb_von(text)
    materialien = materialien_von(text)
    aufnahme = aufnahme_von(text)
    systeme = systeme_von(text)

    # Untergruppe je Tätigkeit
    if taetigkeit == 'Trennen & Schleifen':
        untergruppe = untergruppe_trennen_schleifen(p, text, flags)
    elif taetigkeit == 'Verlegen, Heben & Transportieren':
        untergruppe = untergruppe_verlegen(p, text, flags)
    elif taetigkeit == 'Maschinen & Geräte':
        untergruppe = untergruppe_maschinen(p, text, antrieb, flags)
    elif taetigkeit == 'Baustellen- & Werkstattbedarf':
        untergruppe = untergruppe_baustellenbedarf(p, text, flags)
    else:
        untergruppe = p['unterkategorie']

    # Hämmer ausserhalb von HK 11 ebenfalls typisieren (Pkt. 12)
    hammer_typ = ''
    if re.search(r'hammer|fäustel|knüpfel|klüpfel|klöpfel', p['name'], re.I) \
            and not re.search(r'bohrhammer|kombihammer|abbruchhammer', p['name'], re.I):
        if RX_HAMMER_STEINMETZ.search(p['name']):
            hammer_typ = 'Steinmetz- & Bildhauerhammer'
        elif RX_HAMMER_BAU.search(p['name']):
            hammer_typ = 'Bau- & Baustellenhammer'
        elif p['sparte'] == 'Steinmetz & Bildhauer':
            hammer_typ = 'Steinmetz- & Bildhauerhammer'
        else:
            hammer_typ = 'Bau- & Baustellenhammer'

    # Mehrfachzuordnung (Pkt. 9/15): zusätzliche Tätigkeiten
    zusatz_taetigkeiten = []
    if untergruppe == 'Aufnahmeteller & Adapter' and re.search(r'stonelux|repar|slx', text, re.I):
        zusatz_taetigkeiten.append('Reinigen, Schützen & Reparieren')
    if taetigkeit != 'Staub & Absaugung' and re.search(r'absaug|staubhaube', p['name'], re.I):
        zusatz_taetigkeiten.append('Staub & Absaugung')
    # Maschinen zusätzlich bei ihrer Anwendung anzeigen
    if taetigkeit == 'Maschinen & Geräte':
        if re.search(r'schleifer|schleifmaschine|poliermaschine|polierer|trennschneider|'
                     r'säge|stockmaschine|bürstmaschine', p['name'], re.I):
            zusatz_taetigkeiten.append('Trennen & Schleifen')
        if re.search(r'bohrmaschine|bohrhammer|bohrschleifer|fräsmaschine', p['name'], re.I):
            zusatz_taetigkeiten.append('Bohren & Fräsen')
        if re.search(r'rührwerk', p['name'], re.I):
            zusatz_taetigkeiten.append('Kleben, Fugen & Gehrung')
    # Umgekehrt: Maschinen, die unter einer Anwendung geführt sind,
    # auch unter Maschinen & Geräte zeigen
    elif re.search(r'maschine|schleifer\b|polierer\b|trennschneider|winkelschleifer',
                   p['name'], re.I) and antrieb:
        zusatz_taetigkeiten.append('Maschinen & Geräte')

    preis = r.get('price_chf') or ''
    if not preis:
        flags.append('Kein Preis in den Shopdaten')

    return {
        'id': p['id'],
        'name': p['name'],
        'artnr': r.get('artnr', ''),
        'preis': preis,
        'url': r.get('url', ''),
        'beschreibung': p.get('zusammenfassung', ''),
        'usp': p.get('usp', ''),
        'berufsgruppe': (bg := primaergruppe_korrektur(p, SPARTE_NEU[p['sparte']])),
        'zusatz_gruppen': [g for g in zusatz_gruppen_von(p, taetigkeit) if g != bg],
        'gipser': (lambda gv: {'t': gv[0], 'ug': gv[1]} if gv else None)(
            gipser_view(p, taetigkeit, untergruppe, antrieb, systeme, marke)),
        'taetigkeit': taetigkeit,
        'zusatz_taetigkeiten': zusatz_taetigkeiten,
        'untergruppe': untergruppe,
        'produkttyp': p['unterkategorie'],
        'marke': marke,
        'marken_gruppe': marken_gruppe,
        'materialien': materialien,
        'antrieb': antrieb,
        'aufnahme': aufnahme,
        'systeme': systeme,
        'hammer_typ': hammer_typ,
        'pruefen': flags,
    }


def main():
    data = json.load(open(REPO / 'data' / 'sfinal.json'))
    raw = json.load(open(REPO / 'data' / 'all_products_raw.json'))
    rawmap = {x['id']: x for x in raw['products']}
    out = [klassifiziere(p, rawmap[p['id']]) for p in data]
    (REPO / 'data' / 'kompass.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    n_pruefen = sum(1 for x in out if x['pruefen'])
    print(f'{len(out)} Produkte klassifiziert, {n_pruefen} mit «Zuordnung prüfen»')
    import collections
    print('\nUntergruppen Trennen & Schleifen:')
    for uk, n in collections.Counter(x['untergruppe'] for x in out
                                     if x['taetigkeit'] == 'Trennen & Schleifen').most_common():
        print(f'  {n:4d}  {uk}')
    print('\nUntergruppen Maschinen & Geräte:')
    for uk, n in collections.Counter(x['untergruppe'] for x in out
                                     if x['taetigkeit'] == 'Maschinen & Geräte').most_common():
        print(f'  {n:4d}  {uk}')
    print('\nMarken:')
    for m, n in collections.Counter(x['marke'] for x in out).most_common(20):
        print(f'  {n:4d}  {m}')


if __name__ == '__main__':
    main()
