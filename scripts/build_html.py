import json,html,collections
raw={p['id']:p for p in json.load(open('data/products_raw.json'))['products']}
F=json.load(open('data/final.json'))
F.sort(key=lambda o:(o['hauptkategorie'],o['unterkategorie'],o['top_rang'] if o['top_rang']!="" else 99,-o['top_score'],o['name']))
e=html.escape
cats=collections.OrderedDict()
for o in F: cats.setdefault(o['hauptkategorie'],[]).append(o)
data=[{"k":o['hauptkategorie'],"u":o['unterkategorie'],"r":o['top_rang'],"s":o['top_score'],"n":o['name'],"img":raw[o['id']]['image'],"d":o['zusammenfassung'],"usp":o['usp'],"sek":o['sekundaer'],"url":raw[o['id']]['url'],"sp":o['sparte_farbe'],"p":raw[o['id']]['price_chf'],"art":raw[o['id']]['artnr'],"alt":", ".join(raw[o['id']]['cat_names']) or "nur Hauptkategorie","g":o['top_grund_review'] or o['top_grund']} for o in F]
ntop=sum(1 for o in F if o['top_rang']!="")
sec=""
for k,items in cats.items():
    subs=collections.Counter(o['unterkategorie'] for o in items)
    tops=sorted([o for o in items if o['top_rang']!=""],key=lambda o:o['top_rang'])
    cards="".join(f'''<article class="card"><span class="rank">{o["top_rang"]}</span><div><h4>{e(o["name"])}</h4><p class="usp">{e(o["usp"])}</p><p class="why">{e(o["top_grund_review"] or o["top_grund"])}</p><p class="meta"><span>CHF {e(raw[o["id"]]["price_chf"])}</span><a href="{e(raw[o["id"]]["url"])}" target="_blank" rel="noopener">Shop</a></p></div></article>''' for o in tops)
    sec+=f'''<section class="cat"><header><h3>{e(k)}</h3><span class="count">{len(items)} Produkte</span></header><p class="subs">{" · ".join(f"{e(s)} ({n})" for s,n in subs.items())}</p><div class="cards">{cards}</div></section>'''
page=f'''<title>Ferronato Plattenleger-Sortiment</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#F7F6F2;--sur:#FFFFFF;--ink:#1B2430;--mut:#5C6675;--line:#DDE0E4;--acc:#1F3A5F;--hi:#D9641E;--hibg:#FBEDE3;--th:#EEF1F5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#14181E;--sur:#1C222A;--ink:#E8EAEE;--mut:#9AA3AF;--line:#2C343E;--acc:#8FB3E0;--hi:#F08A45;--hibg:#33241A;--th:#232B35}}}}
:root[data-theme="dark"]{{--bg:#14181E;--sur:#1C222A;--ink:#E8EAEE;--mut:#9AA3AF;--line:#2C343E;--acc:#8FB3E0;--hi:#F08A45;--hibg:#33241A;--th:#232B35}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif;margin:0;padding:2rem 1.5rem 4rem}}
main{{max-width:1240px;margin:0 auto}}
h1{{font-size:1.9rem;font-weight:600;margin:0 0 .25rem;text-wrap:balance}} h2{{font-size:1.25rem;font-weight:600;margin:2.5rem 0 1rem;border-bottom:2px solid var(--acc);padding-bottom:.35rem}}
.lead{{color:var(--mut);max-width:65ch;margin:0}}
.kpi{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}} .kpi div{{background:var(--sur);border:1px solid var(--line);padding:.75rem 1rem;min-width:9rem}} .kpi b{{display:block;font:500 1.6rem/1.1 "IBM Plex Mono",monospace;color:var(--acc)}} .kpi span{{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}}
.cat{{background:var(--sur);border:1px solid var(--line);padding:1rem 1.25rem;margin-bottom:1rem}} .cat header{{display:flex;justify-content:space-between;align-items:baseline;gap:1rem}} .cat h3{{margin:0;font-size:1.05rem;font-weight:600}} .count{{font-family:"IBM Plex Mono",monospace;font-size:.8rem;color:var(--mut)}} .subs{{font-size:.82rem;color:var(--mut);margin:.25rem 0 .9rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:.75rem}} .card{{display:flex;gap:.6rem;border:1px solid var(--line);border-left:3px solid var(--hi);padding:.6rem .7rem;background:var(--bg)}} .rank{{font:500 1.1rem/1 "IBM Plex Mono",monospace;color:var(--hi);min-width:1.2rem}} .card h4{{margin:0 0 .2rem;font-size:.92rem;font-weight:600}} .usp{{margin:0;font-size:.85rem}} .why{{margin:.25rem 0 0;font-size:.78rem;color:var(--mut)}} .meta{{margin:.35rem 0 0;font-size:.78rem;display:flex;gap:.8rem;font-family:"IBM Plex Mono",monospace}} a{{color:var(--acc)}}
.tools{{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:.75rem;align-items:center}} .tools input,.tools select{{font:inherit;padding:.4rem .6rem;border:1px solid var(--line);background:var(--sur);color:var(--ink)}} .tools label{{font-size:.85rem;display:flex;gap:.3rem;align-items:center}}
.wrap{{overflow-x:auto;border:1px solid var(--line);background:var(--sur)}} table{{border-collapse:collapse;font-size:.8rem;min-width:1600px}} th{{position:sticky;top:0;background:var(--th);text-align:left;padding:.5rem;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--line);white-space:nowrap}} td{{padding:.45rem .5rem;border-bottom:1px solid var(--line);vertical-align:top;max-width:26rem}} td.num{{font-family:"IBM Plex Mono",monospace;text-align:right;white-space:nowrap}} tr.top td:first-child{{background:var(--hibg)}} .pill{{display:inline-block;background:var(--hi);color:#fff;font:500 .7rem/1 "IBM Plex Mono",monospace;padding:.2rem .35rem}} .foot{{color:var(--mut);font-size:.8rem;margin-top:1rem}}
input:focus,select:focus,a:focus{{outline:2px solid var(--hi);outline-offset:2px}}
</style>
<main>
<h1>Ferronato Plattenleger-Sortiment</h1>
<p class="lead">Kategorie «Plattenleger» (shop.ferronato.ch, Stand 18.08.2026) mit allen Unterkategorien gescrapt, nach Arbeitsschritt des Plattenlegers neu sortiert, Top-Produkte pro Kategorie markiert. Excel liegt unter <code>shop-plattenleger/data/ferronato_plattenleger_produkte.xlsx</code>.</p>
<div class="kpi"><div><b>{len(F)}</b><span>Produkte</span></div><div><b>{len(cats)}</b><span>Hauptkategorien neu</span></div><div><b>{sum(len(set(o["unterkategorie"] for o in v)) for v in cats.values())}</b><span>Unterkategorien</span></div><div><b>{ntop}</b><span>Top-Produkte</span></div><div><b>152</b><span>vorher ohne Unterkategorie</span></div></div>
<h2>Neue Struktur und Top-Produkte</h2>
{sec}
<h2>Alle Produkte</h2>
<div class="tools"><input id="q" type="search" placeholder="Suchen (Name, Text, Art.-Nr.)" size="34"><select id="fk"><option value="">Alle Hauptkategorien</option>{"".join(f'<option>{e(k)}</option>' for k in cats)}</select><label><input type="checkbox" id="ft"> nur Top</label><span id="cnt" class="count"></span></div>
<div class="wrap"><table><thead><tr><th>Hauptkategorie</th><th>Unterkategorie</th><th>Top</th><th>Rel.</th><th>Produktname</th><th>Bild</th><th>Beschreibung</th><th>Feature / USP</th><th>Sekundäre Info</th><th>Link</th><th>Sparte/Farbe</th><th>CHF</th><th>Art.-Nr.</th><th>Alte Shop-Kategorie</th></tr></thead><tbody id="tb"></tbody></table></div>
<p class="foot">Quelle: shop.ferronato.ch/de/category/216/plattenleger inkl. 12 Unterkategorien. Preise exkl. MwSt. Relevanz 1 bis 5 aus Sicht Plattenleger (Kaufhäufigkeit, Alltag, Marke, Preis-Leistung).</p>
</main>
<script>
const D={json.dumps(data,ensure_ascii=False)};
const tb=document.getElementById('tb'),q=document.getElementById('q'),fk=document.getElementById('fk'),ft=document.getElementById('ft'),cnt=document.getElementById('cnt');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
function render(){{const s=q.value.toLowerCase(),k=fk.value,t=ft.checked;let n=0,h='';
for(const r of D){{if(k&&r.k!==k)continue;if(t&&r.r==='')continue;if(s&&!(r.n+' '+r.d+' '+r.art+' '+r.usp).toLowerCase().includes(s))continue;n++;
h+=`<tr class="${{r.r!==''?'top':''}}"><td>${{esc(r.k)}}</td><td>${{esc(r.u)}}</td><td>${{r.r!==''?'<span class="pill">Top '+r.r+'</span>':''}}</td><td class="num">${{r.s}}</td><td><b>${{esc(r.n)}}</b></td><td><a href="${{esc(r.img)}}" target="_blank" rel="noopener">Bild</a></td><td>${{esc(r.d)}}</td><td>${{esc(r.usp)}}</td><td>${{esc(r.sek)}}</td><td><a href="${{esc(r.url)}}" target="_blank" rel="noopener">Shop</a></td><td>${{esc(r.sp)}}</td><td class="num">${{esc(r.p)}}</td><td class="num">${{esc(r.art)}}</td><td>${{esc(r.alt)}}</td></tr>`}}
tb.innerHTML=h;cnt.textContent=n+' von '+D.length}}
q.oninput=fk.onchange=ft.onchange=render;render();
</script>'''
open('docs/uebersicht.html','w').write(page); print(len(page))
