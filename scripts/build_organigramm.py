#!/usr/bin/env python3
# Baut die Kategorieübersicht als Organigramm (HTML) aus data/sfinal.json
# plus Produkt-Overlay und Abhak-Fortschritt (localStorage) für die Shop-Migration.
# Ausgabe: deliverable/Ferronato_Kategorien_Organigramm.html
import json, collections, html, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / 'deliverable' / 'Ferronato_Kategorien_Organigramm.html'

data = json.load(open(REPO / 'data' / 'sfinal.json'))
# Shop-Name der Sparte «Übergreifend» (Entscheid 2026-08-26); Datenbestand bleibt unverändert
for _p in data:
    if _p['sparte'] == 'Übergreifend':
        _p['sparte'] = 'Werkstatt & Baustelle'
raw = json.load(open(REPO / 'data' / 'all_products_raw.json'))['products']
rawmap = {p['id']: p for p in raw}

tree = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for p in data:
    tree[p['sparte']][p['hauptkategorie']][p['unterkategorie']] += 1

# Produkt-Payload: key "Sparte|Hauptkategorie" -> {Unterkategorie: [produkte]}
payload = collections.defaultdict(lambda: collections.defaultdict(list))
for p in data:
    r = rawmap.get(p['id'], {})
    try:
        alt = ' › '.join(eval(r.get('breadcrumb', '[]')))
    except Exception:
        alt = ''
    rang = str(p.get('top_rang', '')).strip()
    payload[p['sparte'] + '|' + p['hauptkategorie']][p['unterkategorie']].append({
        'id': p['id'],
        'name': p['name'] or r.get('name', ''),
        'artnr': r.get('artnr', ''),
        'preis': r.get('price_chf', ''),
        'url': r.get('url', ''),
        'alt': alt,
        'top': int(rang) if rang else 0,
        'grund': (p.get('top_grund', '') if rang else ''),
    })
for hk in payload.values():
    for lst in hk.values():
        # Top-Produkte zuerst (nach Rang), danach alphabetisch
        lst.sort(key=lambda x: (x['top'] == 0, x['top'] or 99, x['name'].lower()))

ORDER = ['Plattenleger', 'Steinmetz & Bildhauer', 'GaLa-Bau & Tiefbau',
         'Gipser & Betonkosmetik', 'Autogewerbe', 'Werkstatt & Baustelle']
HUES = {  # Akzentfarbe pro Sparte (h, s%), gedeckt, hell- und dunkeltauglich
    'Plattenleger': (215, 60),
    'Steinmetz & Bildhauer': (28, 45),
    'GaLa-Bau & Tiefbau': (140, 40),
    'Gipser & Betonkosmetik': (270, 35),
    'Autogewerbe': (355, 55),
    'Werkstatt & Baustelle': (200, 10),
}

total = len(data)
cols = []
for sparte in ORDER:
    hks = tree[sparte]
    s_tot = sum(sum(c.values()) for c in hks.values())
    h, s = HUES[sparte]
    boxes = []
    for hk in sorted(hks):
        c = hks[hk]
        nr, name = hk.split(' ', 1)
        key = sparte + '|' + hk
        n_top = sum(1 for pr in payload[key].values() for x in pr if x['top'])
        top_html = f'<span class="hk-top">★ {n_top}</span>' if n_top else ''
        subs = ''.join(
            f'<li>{html.escape(u)}<i>{n}</i></li>'
            for u, n in c.most_common())
        boxes.append(
            f'<button class="hk" type="button" data-key="{html.escape(key, quote=True)}">'
            f'<div class="hk-head"><span class="hk-nr">{nr}</span>'
            f'<span class="hk-name">{html.escape(name)}</span>'
            f'{top_html}<span class="hk-count" data-count="{sum(c.values())}">{sum(c.values())}</span></div>'
            f'<div class="hk-bar"><span></span></div>'
            f'<ul class="subs">{subs}</ul></button>')
    cols.append(
        f'<div class="col" style="--h:{h};--s:{s}%">'
        f'<div class="sparte"><h2>{html.escape(sparte)}</h2>'
        f'<span class="sparte-count">{s_tot} Produkte</span>'
        f'<span class="sparte-done" data-total="{s_tot}"></span></div>'
        f'{"".join(boxes)}</div>')

products_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

page = f"""<title>Ferronato Kategorien-Organigramm</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root {{
  --bg: hsl(210 15% 96%);
  --panel: hsl(0 0% 100%);
  --ink: hsl(215 25% 15%);
  --muted: hsl(215 12% 45%);
  --line: hsl(215 15% 78%);
  --trunk: hsl(215 25% 25%);
  --trunk-ink: hsl(0 0% 100%);
  --ok: hsl(150 55% 34%);
  --ok-bg: hsl(150 45% 92%);
  --overlay-dim: hsl(215 30% 10% / .55);
  --top-ink: hsl(40 80% 30%);
  --top-border: hsl(40 70% 62%);
  --top-bg: hsl(45 85% 94%);
  --node-bg: hsl(var(--h) var(--s) 94%);
  --node-border: hsl(var(--h) var(--s) 72%);
  --node-ink: hsl(var(--h) var(--s) 26%);
  --count-bg: hsl(var(--h) var(--s) 32%);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: hsl(215 20% 10%);
    --panel: hsl(215 18% 14%);
    --ink: hsl(210 15% 90%);
    --muted: hsl(215 10% 62%);
    --line: hsl(215 12% 30%);
    --trunk: hsl(215 20% 88%);
    --trunk-ink: hsl(215 25% 12%);
    --ok: hsl(150 50% 55%);
    --ok-bg: hsl(150 35% 18%);
    --overlay-dim: hsl(215 30% 4% / .65);
    --top-ink: hsl(45 75% 65%);
    --top-border: hsl(42 50% 40%);
    --top-bg: hsl(42 45% 15%);
    --node-bg: hsl(var(--h) calc(var(--s) * .5) 17%);
    --node-border: hsl(var(--h) calc(var(--s) * .6) 34%);
    --node-ink: hsl(var(--h) calc(var(--s) * .8) 78%);
    --count-bg: hsl(var(--h) calc(var(--s) * .7) 50%);
  }}
}}
:root[data-theme="dark"] {{
  --bg: hsl(215 20% 10%);
  --panel: hsl(215 18% 14%);
  --ink: hsl(210 15% 90%);
  --muted: hsl(215 10% 62%);
  --line: hsl(215 12% 30%);
  --trunk: hsl(215 20% 88%);
  --trunk-ink: hsl(215 25% 12%);
  --ok: hsl(150 50% 55%);
  --ok-bg: hsl(150 35% 18%);
  --overlay-dim: hsl(215 30% 4% / .65);
  --top-ink: hsl(45 75% 65%);
  --top-border: hsl(42 50% 40%);
  --top-bg: hsl(42 45% 15%);
  --node-bg: hsl(var(--h) calc(var(--s) * .5) 17%);
  --node-border: hsl(var(--h) calc(var(--s) * .6) 34%);
  --node-ink: hsl(var(--h) calc(var(--s) * .8) 78%);
  --count-bg: hsl(var(--h) calc(var(--s) * .7) 50%);
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--bg); color: var(--ink);
  font-family: "IBM Plex Sans", system-ui, sans-serif;
  margin: 0; padding: 2.5rem 0 4rem;
}}
.head {{ text-align: center; padding: 0 1.25rem; }}
.root {{
  display: inline-flex; flex-direction: column; gap: .35rem;
  background: var(--trunk); color: var(--trunk-ink);
  border-radius: .6rem; padding: 1rem 1.6rem;
  position: relative; min-width: 22rem;
}}
.root::after {{
  content: ""; position: absolute; left: 50%; top: 100%;
  height: 1.5rem; border-left: 2px solid var(--line);
}}
.root h1 {{
  font-family: Archivo, system-ui, sans-serif; font-weight: 800;
  font-size: 1.45rem; margin: 0; letter-spacing: -.01em; text-wrap: balance;
}}
.root p {{ margin: 0; font-size: .85rem; opacity: .8; }}
.root p b, .root p i {{ font-family: "IBM Plex Mono", monospace; font-weight: 500; font-style: normal; }}
.total-bar {{
  height: .35rem; border-radius: 99px; background: hsl(0 0% 100% / .25); overflow: hidden;
}}
.total-bar span {{ display: block; height: 100%; width: 0; background: hsl(150 55% 55%); }}
.chart-scroll {{ overflow-x: auto; margin-top: 1.5rem; }}
.chart {{
  display: flex; align-items: flex-start; justify-content: center;
  min-width: max-content; margin: 0 auto; padding: 0 1.25rem;
}}
.col {{
  position: relative; width: 15.5rem; flex: none;
  padding: 1.5rem .45rem 0;
  display: flex; flex-direction: column;
}}
.col::before, .col::after {{
  content: ""; position: absolute; top: 0; width: 50%; height: 1.5rem;
  border-top: 2px solid var(--line);
}}
.col::before {{ right: 50%; border-right: 2px solid var(--line); }}
.col::after {{ left: 50%; }}
.col:first-child::before {{ border-top: none; }}
.col:last-child::after {{ border-top: none; }}
.sparte {{
  background: var(--node-bg); border: 1px solid var(--node-border);
  border-top: 3px solid var(--count-bg);
  border-radius: .5rem; padding: .6rem .8rem; text-align: center;
}}
.sparte h2 {{
  font-family: Archivo, system-ui, sans-serif; font-weight: 700;
  font-size: 1rem; margin: 0; color: var(--node-ink); text-wrap: balance;
}}
.sparte-count {{
  font-family: "IBM Plex Mono", monospace; font-size: .74rem; color: var(--muted);
}}
.sparte-done {{
  display: block; font-family: "IBM Plex Mono", monospace;
  font-size: .7rem; color: var(--ok);
}}
.hk {{
  position: relative; margin-top: 1.1rem;
  background: var(--panel); border: 1px solid var(--line);
  border-left: 3px solid var(--node-border);
  border-radius: .45rem; padding: .55rem .7rem .6rem;
  font: inherit; color: inherit; text-align: left; cursor: pointer;
  display: block; width: 100%;
}}
.hk:hover {{ border-color: var(--node-border); }}
.hk:focus-visible {{ outline: 2px solid var(--count-bg); outline-offset: 2px; }}
.hk::before {{
  content: ""; position: absolute; left: 50%; top: -1.2rem; height: 1.2rem;
  border-left: 2px solid var(--node-border);
}}
.hk.done {{ border-left-color: var(--ok); }}
.hk-head {{ display: flex; align-items: baseline; gap: .45rem; }}
.hk-nr {{
  font-family: "IBM Plex Mono", monospace; font-size: .68rem;
  color: var(--node-ink); opacity: .75;
}}
.hk-name {{ font-weight: 600; font-size: .85rem; flex: 1; }}
.hk-count {{
  font-family: "IBM Plex Mono", monospace; font-size: .68rem;
  color: hsl(0 0% 100%); background: var(--count-bg);
  border-radius: 99px; padding: .05rem .45rem; align-self: center; white-space: nowrap;
}}
.hk.done .hk-count {{ background: var(--ok); }}
.hk-bar {{
  height: .22rem; border-radius: 99px; background: var(--line);
  overflow: hidden; margin-top: .4rem;
}}
.hk-bar span {{ display: block; height: 100%; width: 0; background: var(--ok); }}
.subs {{
  list-style: none; margin: .45rem 0 0; padding: .45rem 0 0;
  border-top: 1px dashed var(--line);
  display: flex; flex-direction: column; gap: .18rem;
}}
.subs li {{
  font-size: .74rem; color: var(--muted);
  display: flex; justify-content: space-between; gap: .5rem;
}}
.subs li i {{
  font-style: normal; font-family: "IBM Plex Mono", monospace;
  font-size: .68rem; color: var(--node-ink);
}}
.legend {{
  margin: 2.5rem auto 0; padding: 1.25rem 1.25rem 0; border-top: 1px solid var(--line);
  font-size: .8rem; color: var(--muted); max-width: 65ch; text-align: center;
}}
/* Overlay */
.overlay {{
  position: fixed; inset: 0; background: var(--overlay-dim);
  display: none; align-items: flex-start; justify-content: center;
  padding: 3rem 1rem; z-index: 10;
}}
.overlay.open {{ display: flex; }}
.dialog {{
  background: var(--bg); color: var(--ink);
  border: 1px solid var(--line); border-radius: .7rem;
  width: min(52rem, 100%); max-height: calc(100vh - 6rem);
  display: flex; flex-direction: column; overflow: hidden;
}}
.dlg-head {{
  display: flex; align-items: center; gap: .75rem;
  padding: .9rem 1.25rem; border-bottom: 1px solid var(--line);
  background: var(--panel);
}}
.dlg-head h3 {{
  font-family: Archivo, system-ui, sans-serif; font-weight: 700;
  font-size: 1.05rem; margin: 0; flex: 1;
}}
.dlg-head .dlg-progress {{
  font-family: "IBM Plex Mono", monospace; font-size: .78rem; color: var(--muted);
}}
.dlg-close {{
  font: inherit; background: none; border: 1px solid var(--line); color: var(--ink);
  border-radius: .4rem; padding: .3rem .7rem; cursor: pointer;
}}
.dlg-close:hover {{ border-color: var(--muted); }}
.dlg-body {{ overflow-y: auto; padding: .5rem 1.25rem 1.5rem; }}
.grp {{ margin-top: 1.1rem; }}
.grp-head {{
  display: flex; align-items: baseline; gap: .6rem;
  position: sticky; top: 0; background: var(--bg); padding: .4rem 0;
}}
.grp-head h4 {{ margin: 0; font-size: .9rem; }}
.grp-head .grp-progress {{
  font-family: "IBM Plex Mono", monospace; font-size: .72rem; color: var(--muted); flex: 1;
}}
.grp-all {{
  font: inherit; font-size: .72rem; background: none; cursor: pointer;
  border: 1px solid var(--line); color: var(--muted);
  border-radius: .35rem; padding: .12rem .5rem;
}}
.grp-all:hover {{ color: var(--ink); border-color: var(--muted); }}
.prod {{
  display: flex; align-items: flex-start; gap: .65rem;
  padding: .45rem .55rem; border-radius: .4rem;
  border: 1px solid transparent;
}}
.prod:hover {{ background: var(--panel); }}
.prod.checked {{ background: var(--ok-bg); }}
.prod.top {{ border-color: var(--top-border); background: var(--top-bg); }}
.prod.top.checked {{ background: var(--ok-bg); }}
.p-top {{
  display: inline-block; font-family: "IBM Plex Mono", monospace;
  font-size: .66rem; font-weight: 500; color: var(--top-ink);
  border: 1px solid var(--top-border); border-radius: .3rem;
  padding: .04rem .38rem; margin-right: .4rem; vertical-align: 1px;
  white-space: nowrap;
}}
.hk-top {{
  font-size: .66rem; color: var(--top-ink); font-family: "IBM Plex Mono", monospace;
  align-self: center; white-space: nowrap;
}}
.prod.checked .p-name {{ text-decoration: line-through; color: var(--muted); }}
.prod input {{ margin-top: .25rem; accent-color: var(--ok); width: 1rem; height: 1rem; flex: none; }}
.prod label {{ flex: 1; cursor: pointer; min-width: 0; }}
.p-name {{ font-size: .85rem; font-weight: 500; }}
.p-meta {{
  font-size: .72rem; color: var(--muted); margin-top: .1rem;
  display: flex; flex-wrap: wrap; gap: .25rem .8rem;
}}
.p-meta b {{ font-family: "IBM Plex Mono", monospace; font-weight: 500; }}
.p-alt {{ font-size: .7rem; color: var(--muted); opacity: .8; margin-top: .05rem; }}
.p-link {{
  flex: none; font-size: .72rem; color: var(--node-ink, var(--ink));
  border: 1px solid var(--line); border-radius: .35rem;
  padding: .15rem .5rem; text-decoration: none; margin-top: .15rem;
}}
.p-link:hover {{ border-color: var(--muted); }}
@media (prefers-reduced-motion: no-preference) {{
  .hk-bar span, .total-bar span {{ transition: width .25s ease; }}
}}
</style>
<div class="head">
  <div class="root">
    <h1>Ferronato Gesamtsortiment</h1>
    <p><b>{total}</b> Produkte · 6 Sparten · 14 Arbeitsschritte · <i id="total-done">0 migriert</i></p>
    <div class="total-bar"><span id="total-bar"></span></div>
  </div>
</div>
<div class="chart-scroll">
  <div class="chart">
    {''.join(cols)}
  </div>
</div>
<p class="legend">Migrations-Werkzeug: Klick auf einen Arbeitsschritt öffnet die Produktliste.
Abgehakte Produkte gelten als in die neue Shop-Struktur überführt; der Stand wird lokal im Browser
gespeichert (localStorage, pro Gerät). Enthalten sind alle Produkte; mit ★ markierte sind die
Top-Produkte (Rang 1-6 je Sparte und Arbeitsschritt aus dem Bestseller-Scoring), sie stehen in
ihrer Unterkategorie zuoberst. Quelle: data/sfinal.json, Stand 26.08.2026.</p>

<div class="overlay" id="overlay">
  <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dlg-title">
    <div class="dlg-head">
      <h3 id="dlg-title"></h3>
      <span class="dlg-progress" id="dlg-progress"></span>
      <button class="dlg-close" type="button" id="dlg-close">Schliessen · Esc</button>
    </div>
    <div class="dlg-body" id="dlg-body"></div>
  </div>
</div>

<script type="application/json" id="products-data">{products_json}</script>
<script>
(function () {{
  var DATA = JSON.parse(document.getElementById('products-data').textContent);
  var KEY = 'ferronato-migration-v1';

  function loadState() {{
    try {{ return JSON.parse(localStorage.getItem(KEY)) || {{}}; }}
    catch (e) {{ return {{}}; }}
  }}
  function saveState(st) {{
    try {{ localStorage.setItem(KEY, JSON.stringify(st)); }} catch (e) {{}}
  }}
  var state = loadState();

  var TOTALS = {{}}; var GRAND = 0;
  Object.keys(DATA).forEach(function (k) {{
    var n = 0;
    Object.keys(DATA[k]).forEach(function (u) {{ n += DATA[k][u].length; }});
    TOTALS[k] = n; GRAND += n;
  }});

  function doneIn(key) {{
    var n = 0;
    Object.keys(DATA[key]).forEach(function (u) {{
      DATA[key][u].forEach(function (p) {{ if (state[p.id]) n++; }});
    }});
    return n;
  }}

  function refreshChart() {{
    var grandDone = 0;
    var sparteDone = {{}};
    document.querySelectorAll('.hk').forEach(function (btn) {{
      var key = btn.dataset.key;
      var d = doneIn(key), t = TOTALS[key];
      grandDone += d;
      var sp = key.split('|')[0];
      sparteDone[sp] = (sparteDone[sp] || 0) + d;
      btn.querySelector('.hk-count').textContent = d ? d + '/' + t : String(t);
      btn.querySelector('.hk-bar span').style.width = (t ? (100 * d / t) : 0) + '%';
      btn.classList.toggle('done', d === t && t > 0);
    }});
    document.querySelectorAll('.col').forEach(function (col) {{
      var sp = col.querySelector('h2').textContent;
      var el = col.querySelector('.sparte-done');
      var d = sparteDone[sp] || 0;
      el.textContent = d ? d + '/' + el.dataset.total + ' migriert' : '';
    }});
    document.getElementById('total-done').textContent = grandDone + ' von ' + GRAND + ' migriert';
    document.getElementById('total-bar').style.width = (100 * grandDone / GRAND) + '%';
  }}

  var overlay = document.getElementById('overlay');
  var body = document.getElementById('dlg-body');
  var currentKey = null;

  function esc(s) {{
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }}

  function refreshDialog() {{
    if (!currentKey) return;
    var d = doneIn(currentKey), t = TOTALS[currentKey];
    document.getElementById('dlg-progress').textContent = d + ' / ' + t + ' migriert';
    Object.keys(DATA[currentKey]).forEach(function (u) {{
      var grp = body.querySelector('[data-grp="' + CSS.escape(u) + '"]');
      if (!grp) return;
      var n = 0;
      DATA[currentKey][u].forEach(function (p) {{ if (state[p.id]) n++; }});
      grp.querySelector('.grp-progress').textContent = n + ' / ' + DATA[currentKey][u].length;
      grp.querySelector('.grp-all').textContent = n === DATA[currentKey][u].length ? 'alle zurücksetzen' : 'alle abhaken';
    }});
  }}

  function openOverlay(key) {{
    currentKey = key;
    var parts = key.split('|');
    document.getElementById('dlg-title').textContent = parts[0] + ' · ' + parts[1];
    var subs = Object.keys(DATA[key]).sort(function (a, b) {{
      return DATA[key][b].length - DATA[key][a].length || a.localeCompare(b, 'de');
    }});
    var out = subs.map(function (u) {{
      var rows = DATA[key][u].map(function (p) {{
        var meta = [];
        if (p.artnr) meta.push('<b>' + esc(p.artnr) + '</b>');
        if (p.preis) meta.push('CHF ' + esc(p.preis));
        var topBadge = p.top ? '<span class="p-top" title="' + esc(p.grund) + '">★ Top ' + p.top + '</span>' : '';
        return '<div class="prod' + (state[p.id] ? ' checked' : '') + (p.top ? ' top' : '') + '" data-id="' + esc(p.id) + '">' +
          '<input type="checkbox" id="p' + esc(p.id) + '"' + (state[p.id] ? ' checked' : '') + '>' +
          '<label for="p' + esc(p.id) + '"><div class="p-name">' + topBadge + esc(p.name) + '</div>' +
          '<div class="p-meta">' + meta.join(' ') + '</div>' +
          (p.alt ? '<div class="p-alt">Alt: ' + esc(p.alt) + '</div>' : '') + '</label>' +
          (p.url ? '<a class="p-link" href="' + esc(p.url) + '" target="_blank" rel="noopener">Shop ↗</a>' : '') +
          '</div>';
      }}).join('');
      return '<div class="grp" data-grp="' + esc(u) + '">' +
        '<div class="grp-head"><h4>' + esc(u) + '</h4>' +
        '<span class="grp-progress"></span>' +
        '<button class="grp-all" type="button"></button></div>' + rows + '</div>';
    }}).join('');
    body.innerHTML = out;
    overlay.classList.add('open');
    body.scrollTop = 0;
    refreshDialog();
  }}

  function closeOverlay() {{
    overlay.classList.remove('open');
    currentKey = null;
  }}

  document.querySelectorAll('.hk').forEach(function (btn) {{
    btn.addEventListener('click', function () {{ openOverlay(btn.dataset.key); }});
  }});
  document.getElementById('dlg-close').addEventListener('click', closeOverlay);
  overlay.addEventListener('click', function (e) {{ if (e.target === overlay) closeOverlay(); }});
  document.addEventListener('keydown', function (e) {{
    if (e.key === 'Escape' && overlay.classList.contains('open')) closeOverlay();
  }});

  body.addEventListener('change', function (e) {{
    var row = e.target.closest('.prod');
    if (!row) return;
    var id = row.dataset.id;
    if (e.target.checked) state[id] = 1; else delete state[id];
    row.classList.toggle('checked', !!e.target.checked);
    saveState(state);
    refreshDialog();
    refreshChart();
  }});
  body.addEventListener('click', function (e) {{
    var btn = e.target.closest('.grp-all');
    if (!btn || !currentKey) return;
    var grp = btn.closest('.grp');
    var u = grp.dataset.grp;
    var list = DATA[currentKey][u];
    var allDone = list.every(function (p) {{ return state[p.id]; }});
    list.forEach(function (p) {{
      if (allDone) delete state[p.id]; else state[p.id] = 1;
    }});
    saveState(state);
    grp.querySelectorAll('.prod').forEach(function (row) {{
      var on = !allDone;
      row.classList.toggle('checked', on);
      row.querySelector('input').checked = on;
    }});
    refreshDialog();
    refreshChart();
  }});

  refreshChart();
}})();
</script>
"""
OUT.write_text(page)
print(OUT, len(page))
