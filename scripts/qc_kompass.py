#!/usr/bin/env python3
"""Qualitätskontrolle Sortiments-Kompass gemäss Korrekturanweisung (15 Punkte)."""
import json
import re
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
K = json.load(open(REPO / 'data' / 'kompass.json'))
HTML = (REPO / 'deliverable' / 'Ferronato_Sortiments_Kompass.html').read_text()

ok = fail = 0


def check(nr, titel, bedingung, detail=''):
    global ok, fail
    status = 'OK  ' if bedingung else 'FAIL'
    if bedingung:
        ok += 1
    else:
        fail += 1
    print(f'{status} {nr:>2}. {titel}' + (f' — {detail}' if detail else ''))


kat_felder = [x['taetigkeit'] for x in K] + [x['untergruppe'] for x in K]

# 1. Kein «Schneiden» als Tätigkeitsbezeichnung
schneiden = [k for k in set(kat_felder) if re.search(r'schneiden', k, re.I)]
check(1, 'Kein «Schneiden»/«Schneiden & Trennen» in Kategorien', not schneiden, str(schneiden))

# 2. Kein «Energie» als Kategoriebezeichnung
energie = [k for k in set(kat_felder) if 'energie' in k.lower()]
check(2, 'Kein «Energie» in Kategorien', not energie, str(energie))

# 3. Akku vs. 230 V unterscheidbar
n_akku = sum(1 for x in K if 'Akku' in x['antrieb'])
n_230 = sum(1 for x in K if 'Elektrisch 230 V' in x['antrieb'])
check(3, 'Akku- und 230-V-Geräte unterscheidbar', n_akku > 0 and n_230 > 0,
      f'{n_akku} Akku, {n_230} × 230 V')

# 4. Trennen / Schleifen / Trennen & Schleifen getrennt
ugs_ts = {x['untergruppe'] for x in K if x['taetigkeit'] == 'Trennen & Schleifen'}
check(4, 'Trennen, Schleifen, Trennen & Schleifen getrennt',
      {'Trennen', 'Schleifen', 'Trennen & Schleifen'} <= ugs_ts, str(sorted(ugs_ts)))

# 5. Feinsteinzeug und UCS getrennt
n_fsz = sum(1 for x in K if 'Feinsteinzeug' in x['materialien'])
n_ucs = sum(1 for x in K if 'UCS / Ultracompact' in x['materialien'])
check(5, 'Feinsteinzeug und UCS getrennt', n_fsz > 0 and n_ucs > 0,
      f'{n_fsz} Feinsteinzeug, {n_ucs} UCS')

# 6. Materialdifferenzierung
mats = {m for x in K for m in x['materialien']}
soll = {'Granit', 'Marmor', 'Kalkstein', 'Sandstein', 'Beton', 'Altbeton', 'Frischbeton'}
check(6, 'Granit/Marmor/Kalkstein/Sandstein/Beton/Alt-/Frischbeton differenziert',
      soll <= mats, str(sorted(soll - mats)) if not soll <= mats else f'{len(mats)} Material-Tags')

# 7. Marken sauber zugeordnet (Feedback-Fälle)
bf = [x for x in K if 'butterfly' in x['name'].lower()]
wg = [x for x in K if 'Wassergefäss' in x['name']]
check(7, 'Marken zugeordnet (Butterfly→DISTAR, Wassergefäss→PROXXON)',
      all(x['marke'] == 'DISTAR' for x in bf) and all(x['marke'] == 'PROXXON' for x in wg),
      f'{len(bf)} Butterfly, {len(wg)} Wassergefäss')

# 8. FLEX und PROBST nicht vermischt: jede Produktkarte hat genau eine Marke,
#    Darstellung gruppiert pro Untergruppe nach Marke
flexprobst = [x for x in K if x['marke'] in ('FLEX', 'PROBST')]
doppelmarke = [x for x in K if x['marke'] == 'FLEX' and x['name'].upper().startswith('PROBST')
               or x['marke'] == 'PROBST' and x['name'].upper().startswith('FLEX')]
check(8, 'FLEX und PROBST getrennt (eine Marke pro Produkt, Marken-Gruppierung)',
      len(doppelmarke) == 0 and 'brandlbl' in HTML, f'{len(flexprobst)} Produkte')

# 9. Vakuum- von Greif-/Zangensystemen getrennt
vhk = {x['untergruppe'] for x in K if x['taetigkeit'] == 'Verlegen, Heben & Transportieren'}
check(9, 'Vakuumsysteme von Greif-/Zangensystemen getrennt',
      {'Vakuumsysteme', 'Greif- & Zangensysteme'} <= vhk, str(sorted(vhk)))

# 10. Bauhämmer von Steinmetz-/Bildhauerhämmern getrennt
ht = {x['hammer_typ'] for x in K if x['hammer_typ']}
check(10, 'Bau- und Steinmetz-/Bildhauerhämmer getrennt',
      {'Steinmetz- & Bildhauerhammer', 'Bau- & Baustellenhammer'} <= ht,
      f"{sum(1 for x in K if x['hammer_typ'])} Hämmer typisiert")

# 11. Aufnahmen/Adapter mehrfach auffindbar
teller = [x for x in K if x['untergruppe'] == 'Aufnahmeteller & Adapter']
mehrfach = [x for x in K if x['zusatz_taetigkeiten']]
check(11, 'Aufnahmeteller & Adapter eigene Gruppe, Mehrfachzuordnung aktiv',
      len(teller) > 0 and len(mehrfach) > 0,
      f'{len(teller)} Teller/Adapter, {len(mehrfach)} Produkte mit Zusatz-Tätigkeit')

# 12. Keine automatischen Top-Rangnummern mehr
check(12, 'Keine Top-1-bis-Top-5-Ränge im Kompass',
      'top_rang' not in HTML and '★ Top' not in HTML
      and not any('top_rang' in x or 'top_score' in x for x in K))

# 13. Manuelles Prio-Feld vorhanden
check(13, 'Prio 1/2/3/Irrelevant als manuelles Feld je Produkt',
      all(s in HTML for s in ['Prio 1', 'Prio 2', 'Prio 3', 'Irrelevant', 'data-prio']))

# 14. Unklare Fälle als «Zuordnung prüfen» markiert
n_pruef = sum(1 for x in K if x['pruefen'])
check(14, 'Unklare Fälle als «Zuordnung prüfen» markiert',
      n_pruef > 0 and 'Zuordnung prüfen' in HTML, f'{n_pruef} Produkte')

# 15. Alle 1624 Produkte vorhanden, Preise/Links/Beschreibungen erhalten
raw = json.load(open(REPO / 'data' / 'all_products_raw.json'))
ids_raw = {p['id'] for p in raw['products']}
ids_k = {x['id'] for x in K}
n_url = sum(1 for x in K if x['url'])
n_preis = sum(1 for x in K if x['preis'])
n_preis_raw = sum(1 for p in raw['products'] if p.get('price_chf'))
check(15, 'Alle 1624 Produkte mit Preis/Link/Beschreibung erhalten',
      len(K) == 1624 and ids_raw == ids_k and n_url == 1624 and n_preis == n_preis_raw,
      f'{len(K)} Produkte, {n_url} Links, {n_preis}/{n_preis_raw} Preise')

print(f'\n{ok} OK, {fail} FAIL')
raise SystemExit(1 if fail else 0)
