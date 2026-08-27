#!/usr/bin/env python3
"""Generiert den Ferronato Sortiments-Kompass als selbstständiges HTML.

Basis: data/kompass.json (aus scripts/classify_kompass.py).
Mehrdimensionale Taxonomie: Berufsgruppe → Tätigkeit → Untergruppe → Marke →
Produkt, plus Ansichten nach Marke, System und «Zuordnung prüfen».
Manuelle Prio-Felder (Prio 1/2/3/Irrelevant), Abhaken und Korrektur-Notizen
werden im Browser gespeichert (localStorage) und sind exportierbar.
"""
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / 'deliverable' / 'Ferronato_Sortiments_Kompass.html'

BERUFSGRUPPEN = [
    'Plattenleger', 'Steinmetz & Bildhauer', 'Natursteinwerk',
    'Gartenbau, Pflästerung & Tiefbau', 'Gipser & Betonkosmetik',
    'Carrosserie & Fahrzeugaufbereitung', 'Holzbau & Zimmerei',
    'Werkstatt & Baustelle',
]
# Gruppen ohne Primärprodukte: befüllt über Mehrfachzuordnung (zusatz_gruppen)
SEKUNDAER_GRUPPEN = {'Natursteinwerk', 'Holzbau & Zimmerei'}
HUES = {
    'Plattenleger': (215, 60), 'Steinmetz & Bildhauer': (28, 45),
    'Natursteinwerk': (18, 30),
    'Gartenbau, Pflästerung & Tiefbau': (140, 40),
    'Gipser & Betonkosmetik': (270, 35),
    'Carrosserie & Fahrzeugaufbereitung': (355, 55),
    'Holzbau & Zimmerei': (80, 35),
    'Werkstatt & Baustelle': (200, 10),
}
TAETIGKEITEN = [
    'Messen & Anzeichnen', 'Trennen & Schleifen', 'Bohren & Fräsen',
    'Verlegen, Heben & Transportieren', 'Kleben, Fugen & Gehrung',
    'Reinigen, Schützen & Reparieren', 'Staub & Absaugung',
    'Maschinen & Geräte', 'Arbeitsschutz (PSA)',
    'Baustellen- & Werkstattbedarf', 'Sanitär- & Montagesysteme',
    'Lackieren & Beschichten', 'Modellieren & Formen',
]
UG_ORDNUNG = {
    'Trennen & Schleifen': ['Trennen', 'Schleifen', 'Trennen & Schleifen',
                            'Polieren', 'Aufnahmeteller & Adapter'],
    'Verlegen, Heben & Transportieren': ['Vakuumsysteme', 'Greif- & Zangensysteme',
                                         'Planum & Abziehsysteme',
                                         'Verlegewerkzeuge & Pflaster',
                                         'Transport & Hebezeuge'],
    'Maschinen & Geräte': ['Akku-Maschinen', 'Elektrische Maschinen (230 V)',
                           'Druckluft-Maschinen', 'Benzin-Maschinen',
                           'Akkus & Ladegeräte', 'Maschinenzubehör & Ersatzteile'],
    'Baustellen- & Werkstattbedarf': ['Bau- & Baustellenhämmer',
                                      'Steinmetz- & Bildhauerhämmer',
                                      'Äxte & Brechwerkzeuge',
                                      'Rührwerke & Rührkörbe',
                                      'Baustellenbeleuchtung & Strom',
                                      'Transport- & Koffersysteme',
                                      'Entsorgung & Verbrauchsmaterial',
                                      'Werkstatt & Handwerkzeug'],
}


def payload():
    kompass = json.load(open(REPO / 'data' / 'kompass.json'))
    prods = []
    for x in kompass:
        prods.append({
            'id': x['id'], 'n': x['name'], 'a': x['artnr'], 'pr': x['preis'],
            'u': x['url'], 'b': x['beschreibung'],
            'g': x['berufsgruppe'], 'zg': x.get('zusatz_gruppen', []),
            't': x['taetigkeit'],
            'zt': x['zusatz_taetigkeiten'], 'ug': x['untergruppe'],
            'typ': x['produkttyp'], 'm': x['marke'], 'mg': x['marken_gruppe'],
            'mat': x['materialien'], 'an': x['antrieb'], 'auf': x['aufnahme'],
            'sys': x['systeme'], 'ht': x['hammer_typ'], 'fl': x['pruefen'],
        })
    return prods


HTML = r'''<title>Ferronato Sortiments-Kompass</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">
<style>
:root{
  --bg:#f5f4f1; --panel:#ffffff; --panel2:#efeeea; --ink:#23252a; --mut:#6c7078;
  --line:#e2e0da; --link:#1c4f9c; --chip:#eceae4; --chip-ink:#4c5058;
  --amber-bg:#fdf3d7; --amber-ink:#8a6100; --amber-line:#e3c26a;
  --p1:#1a7f37; --p1-bg:#e3f2e6; --p2:#9a6700; --p2-bg:#fcf0d3;
  --p3:#4a5a8a; --p3-bg:#e7ebf6; --irr:#82868d; --irr-bg:#ececec;
  --done:#1a7f37; --shadow:0 1px 3px rgb(0 0 0 / .08);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#191b1f; --panel:#212429; --panel2:#2a2d33; --ink:#e6e4df; --mut:#9a9ea6;
    --line:#35383f; --link:#8ab0e8; --chip:#31343b; --chip-ink:#b8bcc4;
    --amber-bg:#3a3113; --amber-ink:#e3c26a; --amber-line:#8a6100;
    --p1:#5cc072; --p1-bg:#1e3324; --p2:#e0b64e; --p2-bg:#3a3113;
    --p3:#9db0e0; --p3-bg:#252c40; --irr:#8a8e96; --irr-bg:#2c2e33;
    --done:#5cc072; --shadow:0 1px 3px rgb(0 0 0 / .4);
  }
}
:root[data-theme="dark"]{
  --bg:#191b1f; --panel:#212429; --panel2:#2a2d33; --ink:#e6e4df; --mut:#9a9ea6;
  --line:#35383f; --link:#8ab0e8; --chip:#31343b; --chip-ink:#b8bcc4;
  --amber-bg:#3a3113; --amber-ink:#e3c26a; --amber-line:#8a6100;
  --p1:#5cc072; --p1-bg:#1e3324; --p2:#e0b64e; --p2-bg:#3a3113;
  --p3:#9db0e0; --p3-bg:#252c40; --irr:#8a8e96; --irr-bg:#2c2e33;
  --done:#5cc072; --shadow:0 1px 3px rgb(0 0 0 / .4);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.5 "Source Sans 3",system-ui,sans-serif}
a{color:var(--link)}
h1,h2,h3,h4{font-family:"Barlow Semi Condensed",system-ui,sans-serif;
  text-wrap:balance;margin:0}
.layout{display:flex;min-height:100vh}
.side{width:272px;flex:0 0 272px;background:var(--panel);
  border-right:1px solid var(--line);padding:18px 14px;position:sticky;top:0;
  height:100vh;overflow-y:auto}
.side h1{font-size:21px;font-weight:700;letter-spacing:.2px}
.side .sub{color:var(--mut);font-size:12.5px;margin:2px 0 16px}
.navlbl{font-size:11px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--mut);margin:16px 4px 6px;font-weight:600}
.navbtn{display:flex;align-items:center;gap:8px;width:100%;text-align:left;
  border:0;background:none;color:var(--ink);font:inherit;font-size:14px;
  padding:7px 9px;border-radius:8px;cursor:pointer}
.navbtn:hover{background:var(--panel2)}
.navbtn.on{background:var(--panel2);font-weight:600}
.navbtn .dot{width:9px;height:9px;border-radius:50%;flex:0 0 9px;
  background:hsl(var(--h) var(--s) 45%)}
.navbtn .cnt{margin-left:auto;color:var(--mut);font-size:12px;
  font-variant-numeric:tabular-nums}
.navbtn .prog{color:var(--done)}
.main{flex:1;min-width:0;padding:22px 26px 80px}
.tophead{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:14px}
.tophead h2{font-size:26px;font-weight:700}
.tophead .spacer{flex:1}
.btn{border:1px solid var(--line);background:var(--panel);color:var(--ink);
  font:inherit;font-size:13.5px;padding:6px 12px;border-radius:8px;cursor:pointer}
.btn:hover{background:var(--panel2)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;align-items:center}
.filters select,.filters input[type=search]{border:1px solid var(--line);
  background:var(--panel);color:var(--ink);font:inherit;font-size:13.5px;
  padding:6px 9px;border-radius:8px;max-width:230px}
.filters .reset{color:var(--mut);font-size:13px;background:none;border:0;
  cursor:pointer;text-decoration:underline}
.tksec{margin:0 0 14px}
.tksec>summary{cursor:pointer;list-style:none;display:flex;align-items:center;
  gap:10px;padding:11px 14px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;box-shadow:var(--shadow)}
.tksec>summary::-webkit-details-marker{display:none}
.tksec>summary h3{font-size:18px;font-weight:600}
.tksec>summary .cnt{margin-left:auto;color:var(--mut);font-size:13px;
  font-variant-numeric:tabular-nums}
.tksec>summary .arr{color:var(--mut);transition:transform .15s}
.tksec[open]>summary .arr{transform:rotate(90deg)}
.tkbody{padding:10px 2px 2px}
.ugsec{margin:0 0 10px;border:1px solid var(--line);border-radius:10px;
  background:var(--panel)}
.ugsec>summary{cursor:pointer;list-style:none;display:flex;align-items:center;
  gap:8px;padding:9px 13px}
.ugsec>summary::-webkit-details-marker{display:none}
.ugsec>summary h4{font-size:15.5px;font-weight:600}
.ugsec>summary .cnt{margin-left:auto;color:var(--mut);font-size:12.5px;
  font-variant-numeric:tabular-nums}
.ugbody{padding:2px 12px 12px}
.copybtn{border:0;background:none;color:var(--mut);font-size:14px;line-height:1;
  padding:2px 5px;border-radius:6px;cursor:pointer;flex:0 0 auto}
.copybtn:hover{background:var(--panel2);color:var(--ink)}
.copybtn.ok{color:var(--done)}
.brandlbl{font-size:12px;text-transform:uppercase;letter-spacing:.07em;
  font-weight:600;color:var(--mut);margin:12px 2px 6px;
  border-bottom:1px solid var(--line);padding-bottom:3px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px}
.card{border:1px solid var(--line);border-radius:10px;padding:10px 12px;
  background:var(--panel);display:flex;flex-direction:column;gap:6px}
.card.done{opacity:.55}
.card.irr .pname{text-decoration:line-through;color:var(--mut)}
.card .top{display:flex;gap:8px;align-items:flex-start}
.pname{font-weight:600;font-size:14px;line-height:1.35;flex:1}
.pname a{color:inherit;text-decoration:none}
.pname a:hover{text-decoration:underline;color:var(--link)}
.price{font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600;
  font-size:13.5px}
.meta{color:var(--mut);font-size:12px;display:flex;flex-wrap:wrap;gap:4px 10px}
.chips{display:flex;flex-wrap:wrap;gap:4px}
.chip{background:var(--chip);color:var(--chip-ink);border-radius:20px;
  font-size:11.5px;padding:1.5px 8px;white-space:nowrap}
.chip.brand{background:var(--p3-bg);color:var(--p3);font-weight:600}
.chip.mat{background:var(--chip)}
.chip.an{background:var(--p1-bg);color:var(--p1)}
.chip.sys{background:var(--p2-bg);color:var(--p2)}
.chip.warn{background:var(--amber-bg);color:var(--amber-ink);
  border:1px solid var(--amber-line);font-weight:600}
.desc{color:var(--mut);font-size:12.5px;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden;cursor:pointer}
.desc.open{display:block;-webkit-line-clamp:unset}
.actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
  border-top:1px solid var(--line);padding-top:7px;margin-top:2px}
.prio{display:flex;gap:0;border:1px solid var(--line);border-radius:7px;
  overflow:hidden}
.prio button{border:0;background:none;color:var(--mut);font:inherit;
  font-size:11.5px;padding:3px 8px;cursor:pointer;border-right:1px solid var(--line)}
.prio button:last-child{border-right:0}
.prio button.on{font-weight:700}
.prio button.on.v1{background:var(--p1-bg);color:var(--p1)}
.prio button.on.v2{background:var(--p2-bg);color:var(--p2)}
.prio button.on.v3{background:var(--p3-bg);color:var(--p3)}
.prio button.on.v4{background:var(--irr-bg);color:var(--irr)}
.ck{display:flex;align-items:center;gap:5px;font-size:12.5px;color:var(--mut);
  cursor:pointer;user-select:none}
.ck input{accent-color:var(--done)}
.note{border:1px solid var(--line);background:var(--bg);color:var(--ink);
  font:inherit;font-size:12px;border-radius:6px;padding:3px 7px;flex:1;
  min-width:110px}
.empty{color:var(--mut);padding:30px 10px;text-align:center}
.ovl{position:fixed;inset:0;background:rgb(0 0 0 / .45);display:none;
  align-items:center;justify-content:center;z-index:50;padding:20px}
.ovl.open{display:flex}
.ovlbox{background:var(--panel);border-radius:12px;max-width:680px;width:100%;
  max-height:80vh;display:flex;flex-direction:column;padding:18px}
.ovlbox textarea{flex:1;min-height:280px;font:12px/1.4 ui-monospace,monospace;
  background:var(--bg);color:var(--ink);border:1px solid var(--line);
  border-radius:8px;padding:10px;margin:10px 0}
.statchips{display:flex;gap:6px;flex-wrap:wrap}
.statchips .chip{cursor:pointer;font-size:12px;padding:3px 10px}
.statchips .chip.on{outline:2px solid var(--link)}
button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible{
  outline:2px solid var(--link);outline-offset:1px}
@media (max-width:860px){
  .layout{display:block}
  .side{width:auto;height:auto;position:static;border-right:0;
    border-bottom:1px solid var(--line)}
}
@media (prefers-reduced-motion: reduce){*{transition:none!important}}
</style>
<script type="application/json" id="kompass-data">__DATA__</script>
<div class="layout">
<nav class="side">
  <h1>Sortiments-Kompass</h1>
  <div class="sub">Ferronato AG · __NPROD__ Produkte · mehrdimensionale Taxonomie</div>
  <div class="navlbl">Berufsgruppen</div>
  <div id="nav-gruppen"></div>
  <div class="navlbl">Weitere Einstiege</div>
  <div id="nav-extra"></div>
  <div class="navlbl">Bewertung</div>
  <div class="statchips" id="prio-stats"></div>
</nav>
<main class="main">
  <div class="tophead">
    <h2 id="viewtitle"></h2>
    <button class="copybtn" id="copy-title" data-copy="" title="Kategoriename kopieren" aria-label="Kategoriename kopieren">⧉</button>
    <span class="spacer"></span>
    <button class="btn" id="btn-export">Stand exportieren</button>
  </div>
  <div class="filters">
    <input type="search" id="f-q" placeholder="Produkt, Art.-Nr. suchen …">
    <select id="f-mat"><option value="">Material: alle</option></select>
    <select id="f-marke"><option value="">Marke: alle</option></select>
    <select id="f-an"><option value="">Antrieb: alle</option></select>
    <select id="f-prio"><option value="">Prio: alle</option>
      <option value="1">Prio 1</option><option value="2">Prio 2</option>
      <option value="3">Prio 3</option><option value="4">Irrelevant</option>
      <option value="0">Noch nicht bewertet</option></select>
    <button class="reset" id="f-reset">Filter zurücksetzen</button>
  </div>
  <div id="content"></div>
</main>
</div>
<div class="ovl" id="export-ovl" role="dialog" aria-label="Export">
  <div class="ovlbox">
    <h3>Bearbeitungsstand exportieren</h3>
    <p style="color:var(--mut);font-size:13px;margin:6px 0 0">
      Prioritäten, Abhak-Status und Korrektur-Notizen als JSON.
      Kopieren und in einer Datei ablegen, um sie zu sichern oder zu teilen.</p>
    <textarea id="export-txt" readonly></textarea>
    <div style="display:flex;gap:8px;justify-content:flex-end">
      <button class="btn" id="btn-copy">Kopieren</button>
      <button class="btn" id="btn-close">Schliessen</button>
    </div>
  </div>
</div>
<script>
'use strict';
const P = JSON.parse(document.getElementById('kompass-data').textContent);
const GRUPPEN = __GRUPPEN__;
const HUES = __HUES__;
const TK = __TK__;
const UGORD = __UGORD__;
const KEY = 'ferronato-kompass-v1';
const esc = s => String(s).replace(/[&<>"]/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

let st = {};
try { st = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { st = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
const rec = id => st[id] || {};
function setRec(id, k, v){ st[id] = st[id] || {}; st[id][k] = v;
  if (!v && v !== 0) delete st[id][k];
  if (!Object.keys(st[id]).length) delete st[id]; save(); }

let view = { typ: 'gruppe', key: GRUPPEN[0] };
let flt = { q: '', mat: '', marke: '', an: '', prio: '' };

// ---------- Hilfen
const inTk = (p, tk) => p.t === tk || (p.zt || []).includes(tk);
const inGruppe = (p, g) => p.g === g || (p.zg || []).includes(g);
const SEK = __SEKGRUPPEN__;
function passt(p){
  if (flt.mat && !p.mat.includes(flt.mat)) return false;
  if (flt.marke && p.m !== flt.marke && p.mg !== flt.marke) return false;
  if (flt.an && !p.an.includes(flt.an)) return false;
  if (flt.prio !== ''){
    const v = rec(p.id).p || 0;
    if (String(v) !== flt.prio) return false;
  }
  if (flt.q){
    const q = flt.q.toLowerCase();
    if (!(p.n.toLowerCase().includes(q) || (p.a||'').toLowerCase().includes(q))) return false;
  }
  return true;
}
function grpSort(a, b){ return b[1].length - a[1].length || a[0].localeCompare(b[0], 'de'); }

// ---------- Karten
const PRIO_LBL = {1:'Prio 1',2:'Prio 2',3:'Prio 3',4:'Irrelevant'};
function card(p){
  const r = rec(p.id);
  const chips = [];
  chips.push('<span class="chip brand">'+esc(p.m)+'</span>');
  p.mat.forEach(m => chips.push('<span class="chip mat">'+esc(m)+'</span>'));
  p.an.forEach(a => chips.push('<span class="chip an">'+esc(a)+'</span>'));
  p.auf.forEach(a => chips.push('<span class="chip">'+esc(a)+'</span>'));
  p.sys.forEach(s => chips.push('<span class="chip sys">'+esc(s)+'</span>'));
  if (p.ht) chips.push('<span class="chip">'+esc(p.ht)+'</span>');
  (p.fl||[]).forEach(f => chips.push('<span class="chip warn" title="'+esc(f)+'">Zuordnung prüfen</span>'));
  const prioBtns = [1,2,3,4].map(v =>
    '<button class="'+(r.p===v?'on v'+v:'')+'" data-prio="'+v+'" data-id="'+p.id+'">'
    + PRIO_LBL[v] + '</button>').join('');
  return '<div class="card'+(r.d?' done':'')+(r.p===4?' irr':'')+'" data-card="'+p.id+'">'
    + '<div class="top"><span class="pname"><a href="'+esc(p.u)+'" target="_blank" rel="noopener">'+esc(p.n)+'</a></span>'
    + '<span class="price">'+(p.pr ? 'CHF '+esc(p.pr) : '–')+'</span></div>'
    + '<div class="meta"><span>Art. '+esc(p.a||'?')+'</span><span>'+esc(p.t)+'</span>'
    + '<span>'+esc(p.typ)+'</span></div>'
    + '<div class="chips">'+chips.join('')+'</div>'
    + (p.b ? '<div class="desc" title="Klick: ganze Beschreibung">'+esc(p.b)+'</div>' : '')
    + '<div class="actions">'
    + '<div class="prio" role="group" aria-label="Priorität">'+prioBtns+'</div>'
    + '<label class="ck"><input type="checkbox" data-done="'+p.id+'"'+(r.d?' checked':'')+'> migriert</label>'
    + '<input class="note" data-note="'+p.id+'" placeholder="Korrektur / Notiz" value="'+esc(r.n||'')+'">'
    + '</div></div>';
}
function copyBtn(name){
  return '<button class="copybtn" data-copy="'+esc(name)+'" '
    + 'title="«'+esc(name)+'» in die Zwischenablage kopieren" '
    + 'aria-label="Kategoriename kopieren">⧉</button>';
}
function cardsByBrand(list){
  const by = {};
  list.forEach(p => { (by[p.m] = by[p.m] || []).push(p); });
  return Object.entries(by).sort(grpSort).map(([m, ps]) =>
    '<div class="brandlbl">'+esc(m)+copyBtn(m)+' · '+ps.length+'</div><div class="grid">'
    + ps.map(card).join('') + '</div>').join('');
}
function ugOrder(tk, keys){
  const ord = UGORD[tk] || [];
  return keys.sort((a, b) => {
    const ia = ord.indexOf(a), ib = ord.indexOf(b);
    if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    if (a === 'Zuordnung prüfen') return 1;
    if (b === 'Zuordnung prüfen') return -1;
    return a.localeCompare(b, 'de');
  });
}
function tkSection(tk, list, open){
  if (!list.length) return '';
  const by = {};
  list.forEach(p => { (by[p.ug] = by[p.ug] || []).push(p); });
  const ugs = ugOrder(tk, Object.keys(by)).map(ug =>
    '<details class="ugsec"><summary><h4>'+esc(ug)+'</h4>'+copyBtn(ug)
    + '<span class="cnt">'+by[ug].length+'</span></summary>'
    + '<div class="ugbody">'+cardsByBrand(by[ug])+'</div></details>').join('');
  return '<details class="tksec"'+(open?' open':'')+'><summary><span class="arr">▸</span>'
    + '<h3>'+esc(tk)+'</h3>'+copyBtn(tk)
    + '<span class="cnt">'+list.length+' Produkte</span></summary>'
    + '<div class="tkbody">'+ugs+'</div></details>';
}

// ---------- Ansichten
function render(){
  const el = document.getElementById('content');
  let html = '', title = '';
  if (view.typ === 'gruppe'){
    title = view.key;
    const hue = HUES[view.key];
    document.documentElement.style.setProperty('--h', hue[0]);
    document.documentElement.style.setProperty('--s', hue[1]+'%');
    const sek = SEK.includes(view.key);
    html = (sek ? '<p style="color:var(--mut);font-size:13px;margin:0 0 12px">'
      + 'Diese Berufsgruppe wird überwiegend über Mehrfachzuordnung befüllt: '
      + 'Die meisten Produkte behalten ihre Primärgruppe und erscheinen hier '
      + 'zusätzlich.</p>' : '')
      + TK.map(tk => tkSection(tk,
      P.filter(p => inGruppe(p, view.key) && inTk(p, tk) && passt(p)), sek)).join('');
  } else if (view.typ === 'marke'){
    title = 'Marke: ' + view.key;
    html = TK.map(tk => tkSection(tk,
      P.filter(p => (p.m === view.key || p.mg === view.key) && inTk(p, tk) && passt(p)), true)).join('');
  } else if (view.typ === 'system'){
    title = 'System: ' + view.key;
    html = TK.map(tk => tkSection(tk,
      P.filter(p => p.sys.includes(view.key) && inTk(p, tk) && passt(p)), true)).join('');
  } else if (view.typ === 'pruefen'){
    title = 'Zuordnung prüfen';
    html = TK.map(tk => tkSection(tk,
      P.filter(p => (p.fl||[]).length && inTk(p, tk) && passt(p)), true)).join('');
  } else if (view.typ === 'prio'){
    title = view.key === '0' ? 'Noch nicht bewertet' : PRIO_LBL[view.key];
    html = TK.map(tk => tkSection(tk,
      P.filter(p => String(rec(p.id).p || 0) === view.key && inTk(p, tk) && passt(p)), true)).join('');
  }
  document.getElementById('viewtitle').textContent = title;
  const ct = document.getElementById('copy-title');
  ct.dataset.copy = view.key || title;
  ct.title = '«' + (view.key || title) + '» in die Zwischenablage kopieren';
  el.innerHTML = html || '<div class="empty">Keine Produkte für diese Auswahl.</div>';
  renderNav();
}

function renderNav(){
  const done = id => rec(id).d ? 1 : 0;
  document.getElementById('nav-gruppen').innerHTML = GRUPPEN.map(g => {
    const ps = P.filter(p => inGruppe(p, g));
    const d = ps.reduce((s, p) => s + done(p.id), 0);
    const hue = HUES[g];
    return '<button class="navbtn'+(view.typ==='gruppe'&&view.key===g?' on':'')
      +'" data-gruppe="'+esc(g)+'" style="--h:'+hue[0]+';--s:'+hue[1]+'%">'
      + '<span class="dot"></span>'+esc(g)
      + '<span class="cnt">'+(d?'<span class="prog">'+d+'</span>/':'')+ps.length+'</span></button>';
  }).join('');
  const marken = {};
  P.forEach(p => { marken[p.mg] = (marken[p.mg]||0)+1; });
  const topM = Object.entries(marken).sort((a,b)=>b[1]-a[1])
    .filter(([m]) => m !== 'Ohne Markenangabe').slice(0, 14);
  const sysSet = {};
  P.forEach(p => p.sys.forEach(s => { sysSet[s] = (sysSet[s]||0)+1; }));
  const nPruef = P.filter(p => (p.fl||[]).length).length;
  document.getElementById('nav-extra').innerHTML =
    topM.map(([m, n]) => '<button class="navbtn'+(view.typ==='marke'&&view.key===m?' on':'')
      +'" data-marke="'+esc(m)+'">'+esc(m)+'<span class="cnt">'+n+'</span></button>').join('')
    + Object.entries(sysSet).sort((a,b)=>b[1]-a[1]).map(([s, n]) =>
      '<button class="navbtn'+(view.typ==='system'&&view.key===s?' on':'')
      +'" data-system="'+esc(s)+'">⚙ '+esc(s)+'<span class="cnt">'+n+'</span></button>').join('')
    + '<button class="navbtn'+(view.typ==='pruefen'?' on':'')+'" data-pruefen="1">'
    + '⚠ Zuordnung prüfen<span class="cnt">'+nPruef+'</span></button>';
  const cnt = {0:0,1:0,2:0,3:0,4:0};
  P.forEach(p => { cnt[rec(p.id).p || 0]++; });
  document.getElementById('prio-stats').innerHTML = [1,2,3,4].map(v =>
    '<span class="chip'+(view.typ==='prio'&&view.key===String(v)?' on':'')
    +'" data-priostat="'+v+'">'+PRIO_LBL[v]+' · '+cnt[v]+'</span>').join('')
    + '<span class="chip'+(view.typ==='prio'&&view.key==='0'?' on':'')
    +'" data-priostat="0">Offen · '+cnt[0]+'</span>';
}

// ---------- Filter-Selects füllen
function fillFilters(){
  const mats = {}, marken = {}, ans = {};
  P.forEach(p => { p.mat.forEach(m => mats[m]=1); marken[p.m]=1; p.an.forEach(a => ans[a]=1); });
  const fill = (id, obj) => {
    const s = document.getElementById(id);
    Object.keys(obj).sort((a,b)=>a.localeCompare(b,'de')).forEach(v => {
      const o = document.createElement('option'); o.value = v; o.textContent = v;
      s.appendChild(o);
    });
  };
  fill('f-mat', mats); fill('f-marke', marken); fill('f-an', ans);
}

// ---------- Events (delegiert)
function copyText(txt){
  try {
    navigator.clipboard.writeText(txt);
  } catch (err) {
    const ta = document.createElement('textarea');
    ta.value = txt; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e2) {}
    ta.remove();
  }
}
document.addEventListener('click', e => {
  const cb = e.target.closest('.copybtn');
  if (cb){
    e.preventDefault(); e.stopPropagation();
    copyText(cb.dataset.copy);
    cb.classList.add('ok'); cb.textContent = '✓';
    setTimeout(() => { cb.classList.remove('ok'); cb.textContent = '⧉'; }, 900);
    return;
  }
  const t = e.target.closest('[data-gruppe],[data-marke],[data-system],[data-pruefen],[data-priostat],[data-prio]');
  if (t){
    if (t.dataset.gruppe){ view = {typ:'gruppe', key:t.dataset.gruppe}; render(); }
    else if (t.dataset.marke){ view = {typ:'marke', key:t.dataset.marke}; render(); }
    else if (t.dataset.system){ view = {typ:'system', key:t.dataset.system}; render(); }
    else if (t.dataset.pruefen){ view = {typ:'pruefen'}; render(); }
    else if (t.dataset.priostat !== undefined){ view = {typ:'prio', key:t.dataset.priostat}; render(); }
    else if (t.dataset.prio){
      const id = t.dataset.id, v = +t.dataset.prio;
      setRec(id, 'p', rec(id).p === v ? 0 : v);
      const cardEl = t.closest('.card');
      cardEl.outerHTML = card(P.find(p => p.id === id));
      renderNav();
    }
    return;
  }
  const d = e.target.closest('.desc');
  if (d) d.classList.toggle('open');
});
document.addEventListener('change', e => {
  if (e.target.dataset.done !== undefined && e.target.dataset.done !== ''){
    setRec(e.target.dataset.done, 'd', e.target.checked ? 1 : 0);
    e.target.closest('.card').classList.toggle('done', e.target.checked);
    renderNav();
  }
});
document.addEventListener('input', e => {
  if (e.target.dataset.note !== undefined && e.target.dataset.note !== ''){
    setRec(e.target.dataset.note, 'n', e.target.value.trim());
  }
  if (e.target.id === 'f-q'){ flt.q = e.target.value.trim(); render(); }
});
['f-mat','f-marke','f-an','f-prio'].forEach(id =>
  document.getElementById(id).addEventListener('change', e => {
    flt[{'f-mat':'mat','f-marke':'marke','f-an':'an','f-prio':'prio'}[id]] = e.target.value;
    render();
  }));
document.getElementById('f-reset').addEventListener('click', () => {
  flt = { q:'', mat:'', marke:'', an:'', prio:'' };
  document.getElementById('f-q').value = '';
  ['f-mat','f-marke','f-an','f-prio'].forEach(id => document.getElementById(id).value = '');
  render();
});
document.getElementById('btn-export').addEventListener('click', () => {
  const out = { exportiert: new Date().toISOString(), stand: st };
  document.getElementById('export-txt').value = JSON.stringify(out, null, 1);
  document.getElementById('export-ovl').classList.add('open');
});
document.getElementById('btn-copy').addEventListener('click', () => {
  const ta = document.getElementById('export-txt');
  ta.select(); try { navigator.clipboard.writeText(ta.value); } catch (e) {}
});
document.getElementById('btn-close').addEventListener('click', () =>
  document.getElementById('export-ovl').classList.remove('open'));
document.getElementById('export-ovl').addEventListener('click', e => {
  if (e.target.id === 'export-ovl') e.target.classList.remove('open');
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.getElementById('export-ovl').classList.remove('open');
});

fillFilters();
render();
</script>
'''


def main():
    prods = payload()
    data = json.dumps(prods, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = (HTML
            .replace('__DATA__', data)
            .replace('__NPROD__', str(len(prods)))
            .replace('__GRUPPEN__', json.dumps(BERUFSGRUPPEN, ensure_ascii=False))
            .replace('__SEKGRUPPEN__', json.dumps(sorted(SEKUNDAER_GRUPPEN), ensure_ascii=False))
            .replace('__HUES__', json.dumps(HUES, ensure_ascii=False))
            .replace('__TK__', json.dumps(TAETIGKEITEN, ensure_ascii=False))
            .replace('__UGORD__', json.dumps(UG_ORDNUNG, ensure_ascii=False)))
    OUT.write_text(html, encoding='utf-8')
    print(f'{OUT.name}: {OUT.stat().st_size/1024:.0f} KB, {len(prods)} Produkte')


if __name__ == '__main__':
    main()
