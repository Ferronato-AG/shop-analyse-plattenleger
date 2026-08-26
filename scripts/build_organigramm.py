#!/usr/bin/env python3
# Baut die Kategorieübersicht als Organigramm (HTML) aus data/sfinal.json
# Ausgabe: deliverable/Ferronato_Kategorien_Organigramm.html
import json, collections, html, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / 'deliverable' / 'Ferronato_Kategorien_Organigramm.html'

data = json.load(open(REPO / 'data' / 'sfinal.json'))
tree = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for p in data:
    tree[p['sparte']][p['hauptkategorie']][p['unterkategorie']] += 1

ORDER = ['Plattenleger', 'Steinmetz & Bildhauer', 'GaLa-Bau & Tiefbau',
         'Gipser & Betonkosmetik', 'Autogewerbe', 'Übergreifend']
HUES = {  # Akzentfarbe pro Sparte (h, s%), gedeckt, hell- und dunkeltauglich
    'Plattenleger': (215, 60),
    'Steinmetz & Bildhauer': (28, 45),
    'GaLa-Bau & Tiefbau': (140, 40),
    'Gipser & Betonkosmetik': (270, 35),
    'Autogewerbe': (355, 55),
    'Übergreifend': (200, 10),
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
        subs = ''.join(
            f'<li>{html.escape(u)}<i>{n}</i></li>'
            for u, n in c.most_common())
        boxes.append(
            f'<div class="hk"><div class="hk-head"><span class="hk-nr">{nr}</span>'
            f'<span class="hk-name">{html.escape(name)}</span>'
            f'<span class="hk-count">{sum(c.values())}</span></div>'
            f'<ul class="subs">{subs}</ul></div>')
    cols.append(
        f'<div class="col" style="--h:{h};--s:{s}%">'
        f'<div class="sparte"><h2>{html.escape(sparte)}</h2>'
        f'<span class="sparte-count">{s_tot} Produkte</span></div>'
        f'{"".join(boxes)}</div>')

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
  display: inline-flex; flex-direction: column; gap: .2rem;
  background: var(--trunk); color: var(--trunk-ink);
  border-radius: .6rem; padding: 1rem 1.6rem;
  position: relative;
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
.root p b {{ font-family: "IBM Plex Mono", monospace; font-weight: 500; }}
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
.hk {{
  position: relative; margin-top: 1.1rem;
  background: var(--panel); border: 1px solid var(--line);
  border-left: 3px solid var(--node-border);
  border-radius: .45rem; padding: .55rem .7rem .6rem;
}}
.hk::before {{
  content: ""; position: absolute; left: 50%; top: -1.2rem; height: 1.2rem;
  border-left: 2px solid var(--node-border);
}}
.hk-head {{ display: flex; align-items: baseline; gap: .45rem; }}
.hk-nr {{
  font-family: "IBM Plex Mono", monospace; font-size: .68rem;
  color: var(--node-ink); opacity: .75;
}}
.hk-name {{ font-weight: 600; font-size: .85rem; flex: 1; }}
.hk-count {{
  font-family: "IBM Plex Mono", monospace; font-size: .68rem;
  color: hsl(0 0% 100%); background: var(--count-bg);
  border-radius: 99px; padding: .05rem .45rem; align-self: center;
}}
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
</style>
<div class="head">
  <div class="root">
    <h1>Ferronato Gesamtsortiment</h1>
    <p><b>{total}</b> Produkte · 6 Sparten · 14 Arbeitsschritte</p>
  </div>
</div>
<div class="chart-scroll">
  <div class="chart">
    {''.join(cols)}
  </div>
</div>
<p class="legend">Organigramm nach Ziel-Taxonomie: jede Sparte (wer kauft) führt ihre nummerierten
Arbeitsschritte (wonach gesucht wird), darin die Unterkategorien mit Produktzahl.
Quelle: data/sfinal.json, Stand 26.08.2026.</p>
"""
OUT.write_text(page)
print(OUT, len(page))
