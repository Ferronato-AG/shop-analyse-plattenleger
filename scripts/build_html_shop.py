import json,html,collections
raw={p['id']:p for p in json.load(open('data/all_products_raw.json'))['products']}
F=json.load(open('data/sfinal.json'))
e=html.escape
SPORDER=['Plattenleger','Steinmetz & Bildhauer','GaLa-Bau & Tiefbau','Gipser & Betonkosmetik','Autogewerbe','Übergreifend']
F.sort(key=lambda o:(SPORDER.index(o['sparte']),o['hauptkategorie'],o['unterkategorie'],o['top_rang'] if o['top_rang']!="" else 99,-o['top_score'],o['name']))
KATS=sorted(set(o['hauptkategorie'] for o in F))
data=[{"id":str(o['id']),"sp":o['sparte'],"k":o['hauptkategorie'],"u":o['unterkategorie'],"r":o['top_rang'],"s":o['top_score'],"n":o['name'],"img":raw[o['id']]['image'],"d":o['zusammenfassung'],"usp":o['usp'],"sek":o['sekundaer'],"url":f"https://shop.ferronato.ch/de/product/{o['id']}/x","p":raw[o['id']]['price_chf'],"art":raw[o['id']]['artnr'],"alt":" > ".join(raw[o['id']]['breadcrumb']),"g":o['top_grund_review'] or o.get('top_grund','')} for o in F]
ntop=sum(1 for o in F if o['top_rang']!="")
sec=""
for sp in SPORDER:
    items=[o for o in F if o['sparte']==sp]
    cats=collections.OrderedDict()
    for o in items: cats.setdefault(o['hauptkategorie'],[]).append(o)
    inner=""
    for k,its in cats.items():
        tops=sorted([o for o in its if o['top_rang']!=""],key=lambda o:o['top_rang'])[:6]
        cards="".join(f'''<article class="card"><span class="rank">{o["top_rang"]}</span><div><h4>{e(o["name"])}</h4><p class="usp">{e(o["usp"])}</p><p class="why">{e(o["top_grund_review"] or o.get("top_grund",""))}</p><p class="meta"><span>CHF {e(raw[o["id"]]["price_chf"])}</span><a href="https://shop.ferronato.ch/de/product/{o["id"]}/x" target="_blank" rel="noopener">Shop</a><button class="fb" data-id="{o["id"]}" title="Feedback zu diesem Produkt">&#9998;</button></p></div></article>''' for o in tops)
        subs=collections.Counter(o['unterkategorie'] for o in its)
        inner+=f'''<section class="cat"><header><h3>{e(k)}</h3><span class="count">{len(its)} Produkte</span></header><p class="subs">{" · ".join(f"{e(s)} ({n})" for s,n in subs.most_common())}</p><div class="cards">{cards}</div></section>'''
    sec+=f'''<details class="sparte" {"open" if sp=="Plattenleger" else ""}><summary><h2>{e(sp)}</h2><span class="count">{len(items)} Produkte</span></summary>{inner}</details>'''
page=f'''<title>Ferronato Sortiments-Kompass</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#F7F6F2;--sur:#FFFFFF;--ink:#1B2430;--mut:#5C6675;--line:#DDE0E4;--acc:#1F3A5F;--hi:#D9641E;--hibg:#FBEDE3;--th:#EEF1F5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#14181E;--sur:#1C222A;--ink:#E8EAEE;--mut:#9AA3AF;--line:#2C343E;--acc:#8FB3E0;--hi:#F08A45;--hibg:#33241A;--th:#232B35}}}}
:root[data-theme="dark"]{{--bg:#14181E;--sur:#1C222A;--ink:#E8EAEE;--mut:#9AA3AF;--line:#2C343E;--acc:#8FB3E0;--hi:#F08A45;--hibg:#33241A;--th:#232B35}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif;margin:0;padding:2rem 1.5rem 6rem}}
main{{max-width:1240px;margin:0 auto}}
h1{{font-size:1.9rem;font-weight:600;margin:0 0 .25rem;text-wrap:balance}}
.lead{{color:var(--mut);max-width:70ch;margin:0}}
.kpi{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}} .kpi div{{background:var(--sur);border:1px solid var(--line);padding:.75rem 1rem;min-width:9rem}} .kpi b{{display:block;font:500 1.6rem/1.1 "IBM Plex Mono",monospace;color:var(--acc)}} .kpi span{{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}}
.sparte{{background:var(--sur);border:1px solid var(--line);margin-bottom:.8rem}} .sparte summary{{cursor:pointer;display:flex;align-items:baseline;gap:1rem;padding:.8rem 1.1rem}} .sparte summary h2{{margin:0;font-size:1.2rem;font-weight:600;border:0;padding:0;display:inline}} .sparte[open] summary{{border-bottom:1px solid var(--line)}}
.cat{{padding:.8rem 1.1rem;border-bottom:1px solid var(--line)}} .cat:last-child{{border-bottom:0}} .cat header{{display:flex;justify-content:space-between;align-items:baseline;gap:1rem}} .cat h3{{margin:0;font-size:1rem;font-weight:600}} .count{{font-family:"IBM Plex Mono",monospace;font-size:.8rem;color:var(--mut)}} .subs{{font-size:.8rem;color:var(--mut);margin:.2rem 0 .8rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:.7rem}} .card{{display:flex;gap:.6rem;border:1px solid var(--line);border-left:3px solid var(--hi);padding:.6rem .7rem;background:var(--bg)}} .rank{{font:500 1.1rem/1 "IBM Plex Mono",monospace;color:var(--hi);min-width:1.2rem}} .card h4{{margin:0 0 .2rem;font-size:.92rem;font-weight:600}} .usp{{margin:0;font-size:.85rem}} .why{{margin:.25rem 0 0;font-size:.78rem;color:var(--mut)}} .meta{{margin:.35rem 0 0;font-size:.78rem;display:flex;gap:.8rem;align-items:center;font-family:"IBM Plex Mono",monospace}} a{{color:var(--acc)}}
h2.tbl{{font-size:1.25rem;font-weight:600;margin:2.5rem 0 1rem;border-bottom:2px solid var(--acc);padding-bottom:.35rem}}
.tools{{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:.75rem;align-items:center}} .tools input,.tools select{{font:inherit;padding:.4rem .6rem;border:1px solid var(--line);background:var(--sur);color:var(--ink)}} .tools label{{font-size:.85rem;display:flex;gap:.3rem;align-items:center}}
.hint{{font-size:.85rem;color:var(--mut);margin:0 0 .6rem}}
.wrap{{overflow-x:auto;border:1px solid var(--line);background:var(--sur)}} table{{border-collapse:collapse;font-size:.8rem;min-width:1750px}} th{{position:sticky;top:0;background:var(--th);text-align:left;padding:.5rem;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--line);white-space:nowrap}} td{{padding:.45rem .5rem;border-bottom:1px solid var(--line);vertical-align:top;max-width:26rem}} td.num{{font-family:"IBM Plex Mono",monospace;text-align:right;white-space:nowrap}} tr.top td:nth-child(2){{background:var(--hibg)}} .pill{{display:inline-block;background:var(--hi);color:#fff;font:500 .7rem/1 "IBM Plex Mono",monospace;padding:.2rem .35rem}} .foot{{color:var(--mut);font-size:.8rem;margin-top:1rem}}
.fb{{font:inherit;cursor:pointer;border:1px solid var(--line);background:var(--sur);color:var(--mut);padding:.15rem .45rem;line-height:1}} .fb.has{{background:var(--hi);border-color:var(--hi);color:#fff}}
#fbbar{{position:fixed;left:0;right:0;bottom:0;background:var(--acc);color:#fff;display:none;justify-content:center;gap:1rem;align-items:center;padding:.6rem 1rem;font-size:.9rem;z-index:40}} #fbbar.show{{display:flex}} #fbbar button{{font:inherit;cursor:pointer;border:1px solid #fff;background:transparent;color:#fff;padding:.35rem .8rem}} #fbbar button.pri{{background:var(--hi);border-color:var(--hi)}}
#ovl{{position:fixed;inset:0;background:rgba(10,14,20,.55);display:none;align-items:center;justify-content:center;z-index:50;padding:1rem}} #ovl.show{{display:flex}}
.panel{{background:var(--sur);color:var(--ink);border:1px solid var(--line);max-width:560px;width:100%;max-height:90vh;overflow:auto;padding:1.2rem 1.4rem}} .panel h3{{margin:0 0 .2rem;font-size:1.05rem}} .panel .sub{{color:var(--mut);font-size:.8rem;font-family:"IBM Plex Mono",monospace;margin:0 0 .9rem}}
.panel fieldset{{border:1px solid var(--line);margin:0 0 .8rem;padding:.6rem .8rem}} .panel legend{{font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);padding:0 .3rem}} .panel label{{display:flex;gap:.4rem;align-items:center;font-size:.9rem;margin:.15rem 0}}
.panel select,.panel textarea{{font:inherit;width:100%;box-sizing:border-box;padding:.4rem .5rem;border:1px solid var(--line);background:var(--bg);color:var(--ink);margin:.25rem 0 .5rem}}
.pbtn{{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:.4rem}} .pbtn button{{font:inherit;cursor:pointer;padding:.45rem .9rem;border:1px solid var(--line);background:var(--sur);color:var(--ink)}} .pbtn button.pri{{background:var(--acc);border-color:var(--acc);color:#fff}} .pbtn button.del{{color:var(--hi)}}
#ptext{{width:100%;box-sizing:border-box;height:16rem;font:.78rem/1.4 "IBM Plex Mono",monospace}}
input:focus,select:focus,a:focus,summary:focus,button:focus,textarea:focus{{outline:2px solid var(--hi);outline-offset:2px}}
</style>
<main>
<h1>Ferronato Sortiments-Kompass</h1>
<p class="lead">Gesamter Shop (shop.ferronato.ch, Stand 21.08.2026): alle Kategorien gescrapt, nach Sparte und Arbeitsschritt neu sortiert, Top-Produkte pro Kategorie. Relevanz-Gewichtung gemäss Kundenfeedback: Verbrauchsmaterial und Systeme (Proxxon/Distar, Colour Bond, Jollynator, Trockenbohrkronen) vor Maschinen.</p>
<div class="kpi"><div><b>{len(F)}</b><span>Produkte</span></div><div><b>6</b><span>Sparten</span></div><div><b>14</b><span>Hauptkategorien</span></div><div><b>{ntop}</b><span>Top-Produkte</span></div><div><b>120</b><span>alte Shop-Kategorien</span></div></div>
{sec}
<h2 class="tbl">Alle Produkte</h2>
<p class="hint">Feedback geben: &#9998; beim Produkt anklicken, Einstufung erfassen. Unten erscheint eine Leiste, dort «Anpassungs-Prompt erstellen» wählen, Text kopieren und an BEYONDER senden.</p>
<div class="tools"><input id="q" type="search" placeholder="Suchen (Name, Text, Art.-Nr.)" size="30"><select id="fs"><option value="">Alle Sparten</option>{"".join(f'<option>{e(s)}</option>' for s in SPORDER)}</select><select id="fk"><option value="">Alle Hauptkategorien</option>{"".join(f'<option>{e(k)}</option>' for k in KATS)}</select><label><input type="checkbox" id="ft"> nur Top</label><span id="cnt" class="count"></span></div>
<div class="wrap"><table><thead><tr><th>FB</th><th>Sparte</th><th>Hauptkategorie</th><th>Unterkategorie</th><th>Top</th><th>Rel.</th><th>Produktname</th><th>Bild</th><th>Beschreibung</th><th>Feature / USP</th><th>Sekundäre Info</th><th>Link</th><th>CHF</th><th>Art.-Nr.</th><th>Alter Shop-Pfad</th></tr></thead><tbody id="tb"></tbody></table></div>
<p class="foot">Quelle: shop.ferronato.ch, 120 Kategorien. Preise exkl. MwSt. Relevanz 1 bis 5: Verbrauchsmaterial/System hoch, Maschinen mittel, Ersatzteile tief; Kunden-Bestseller als Anker.</p>
</main>
<div id="fbbar"><span id="fbn"></span><button class="pri" id="fbgen">Anpassungs-Prompt erstellen</button><button id="fbclr">Alles löschen</button></div>
<div id="ovl"><div class="panel" id="panel"></div></div>
'''
js=r'''<script>
const D=%%DATA%%,SPARTEN=%%SP%%,KATS=%%KATS%%;
const BYID={};for(const r of D)BYID[r.id]=r;
const LS='ferronato-fb';
let FB={};try{FB=JSON.parse(localStorage.getItem(LS)||'{}')}catch(e){FB={}}
const $=id=>document.getElementById(id);
const tb=$('tb'),q=$('q'),fs=$('fs'),fk=$('fk'),ft=$('ft'),cnt=$('cnt'),ovl=$('ovl'),panel=$('panel');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function save(){localStorage.setItem(LS,JSON.stringify(FB));bar();markCards();render()}
function bar(){const n=Object.keys(FB).length;$('fbbar').classList.toggle('show',n>0);$('fbn').textContent=n+(n===1?' Rückmeldung erfasst':' Rückmeldungen erfasst')}
function markCards(){document.querySelectorAll('.card .fb').forEach(b=>b.classList.toggle('has',!!FB[b.dataset.id]))}
function render(){const s=q.value.toLowerCase(),sp=fs.value,k=fk.value,t=ft.checked;let n=0,h='';
for(const r of D){if(sp&&r.sp!==sp)continue;if(k&&r.k!==k)continue;if(t&&r.r==='')continue;if(s&&!(r.n+' '+r.d+' '+r.art+' '+r.usp).toLowerCase().includes(s))continue;n++;if(n>800)continue;
h+=`<tr class="${r.r!==''?'top':''}"><td><button class="fb${FB[r.id]?' has':''}" data-id="${r.id}" title="Feedback zu diesem Produkt">&#9998;</button></td><td>${esc(r.sp)}</td><td>${esc(r.k)}</td><td>${esc(r.u)}</td><td>${r.r!==''?'<span class="pill">Top '+r.r+'</span>':''}</td><td class="num">${r.s}</td><td><b>${esc(r.n)}</b></td><td><a href="${esc(r.img)}" target="_blank" rel="noopener">Bild</a></td><td>${esc(r.d)}</td><td>${esc(r.usp)}</td><td>${esc(r.sek)}</td><td><a href="${esc(r.url)}" target="_blank" rel="noopener">Shop</a></td><td class="num">${esc(r.p)}</td><td class="num">${esc(r.art)}</td><td>${esc(r.alt)}</td></tr>`}
tb.innerHTML=h;cnt.textContent=(n>800?'800 angezeigt von ':'')+n+' Treffern ('+D.length+' total)'}
q.oninput=fs.onchange=fk.onchange=ft.onchange=render;
function opts(list,sel){return '<option value="">unverändert</option>'+list.map(x=>`<option${x===sel?' selected':''}>${esc(x)}</option>`).join('')}
function openFb(id){const r=BYID[id];if(!r)return;const f=FB[id]||{};
panel.innerHTML=`<h3>${esc(r.n)}</h3><p class="sub">Art. ${esc(r.art)} · aktuell: ${esc(r.sp)} &gt; ${esc(r.k)}${r.r!==''?' · Top '+r.r:''}</p>
<fieldset><legend>Top-Produkt</legend>
<label><input type="radio" name="ptop" value="" ${!f.top?'checked':''}> keine Angabe</label>
<label><input type="radio" name="ptop" value="top" ${f.top==='top'?'checked':''}> ist ein Top-Produkt</label>
<label><input type="radio" name="ptop" value="kein" ${f.top==='kein'?'checked':''}> ist KEIN Top-Produkt</label>
</fieldset>
<fieldset><legend>Kategorie verschieben</legend>
<label for="psp">Neue Sparte</label><select id="psp">${opts(SPARTEN,f.sp)}</select>
<label for="pk">Neue Hauptkategorie</label><select id="pk">${opts(KATS,f.k)}</select>
<label for="pnote">Neue Unterkategorie / Bemerkung (optional)</label><textarea id="pnote" rows="2">${esc(f.note||'')}</textarea>
</fieldset>
<div class="pbtn"><button class="pri" id="psave">Speichern</button><button id="pcancel">Abbrechen</button>${FB[id]?'<button class="del" id="pdel">Feedback löschen</button>':''}</div>`;
ovl.classList.add('show');
$('psave').onclick=()=>{const top=panel.querySelector('input[name=ptop]:checked').value,sp=$('psp').value,k=$('pk').value,note=$('pnote').value.trim();
if(!top&&!sp&&!k&&!note){delete FB[id]}else{FB[id]={top,sp,k,note,n:r.n,art:r.art}}
save();close()};
$('pcancel').onclick=close;
const d=$('pdel');if(d)d.onclick=()=>{delete FB[id];save();close()}}
function close(){ovl.classList.remove('show')}
ovl.onclick=ev=>{if(ev.target===ovl)close()};
document.addEventListener('keydown',ev=>{if(ev.key==='Escape')close()});
document.addEventListener('click',ev=>{const b=ev.target.closest('button.fb');if(b)openFb(b.dataset.id)});
function buildPrompt(){const ids=Object.keys(FB);let out='Passe die Ferronato-Sortimentsanalyse gemäss folgendem Kundenfeedback an.\nAktualisiere data/sfinal.json, die Excel-Datei (deliverable/ferronato_gesamtshop_produkte.xlsx) und die HTML-Seite (deliverable/Ferronato_Sortiments_Kompass.html) und pushe die Änderungen ins Repo Ferronato-AG/shop-analyse-plattenleger.\n\n';
ids.forEach((id,i)=>{const f=FB[id];out+=(i+1)+'. [ID '+id+', Art. '+f.art+'] '+f.n+'\n';
if(f.top==='top')out+='   - Top-Produkt: ja, als Top-Produkt führen\n';
if(f.top==='kein')out+='   - Top-Produkt: nein, aus den Top-Produkten entfernen\n';
if(f.sp&&f.k)out+='   - Verschieben nach: '+f.sp+' > '+f.k+'\n';
else if(f.sp)out+='   - Neue Sparte: '+f.sp+'\n';
else if(f.k)out+='   - Neue Hauptkategorie: '+f.k+'\n';
if(f.note)out+='   - Bemerkung: '+f.note+'\n'});
return out}
$('fbgen').onclick=()=>{const p=buildPrompt();
panel.innerHTML=`<h3>Anpassungs-Prompt</h3><p class="sub">${Object.keys(FB).length} Rückmeldungen</p><textarea id="ptext" readonly>${esc(p)}</textarea><p class="hint" id="pstat">Text kopieren und per E-Mail an BEYONDER (chris@beyonder.ch) senden.</p><div class="pbtn"><button class="pri" id="pcopy">In Zwischenablage kopieren</button><button id="pcancel">Schliessen</button></div>`;
ovl.classList.add('show');
$('pcancel').onclick=close;
$('pcopy').onclick=()=>{const ta=$('ptext');ta.select();
(navigator.clipboard?navigator.clipboard.writeText(p):Promise.reject()).then(()=>{$('pstat').textContent='Kopiert. Per E-Mail an BEYONDER (chris@beyonder.ch) senden.'}).catch(()=>{try{document.execCommand('copy');$('pstat').textContent='Kopiert. Per E-Mail an BEYONDER (chris@beyonder.ch) senden.'}catch(e){$('pstat').textContent='Bitte Text manuell markieren und kopieren.'}})}};
$('fbclr').onclick=()=>{panel.innerHTML=`<h3>Alle Rückmeldungen löschen?</h3><p class="sub">${Object.keys(FB).length} Rückmeldungen gehen verloren.</p><div class="pbtn"><button class="del" id="pyes">Ja, löschen</button><button id="pcancel">Abbrechen</button></div>`;ovl.classList.add('show');$('pyes').onclick=()=>{FB={};save();close()};$('pcancel').onclick=close};
render();bar();markCards();
</script>'''
import json as _j
js=js.replace('%%DATA%%',_j.dumps(data,ensure_ascii=False)).replace('%%SP%%',_j.dumps(SPORDER,ensure_ascii=False)).replace('%%KATS%%',_j.dumps(KATS,ensure_ascii=False))
open('deliverable/Ferronato_Sortiments_Kompass.html','w').write(page+js); print(len(page+js))
