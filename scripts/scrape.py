#!/usr/bin/env python3
"""Scrapt Kategorie Plattenleger (216) inkl. Unterkategorien von shop.ferronato.ch."""
import re, html, json, sys, time, concurrent.futures as cf
import urllib.request as ur
BASE="https://shop.ferronato.ch"
OUT=sys.argv[1] if len(sys.argv)>1 else "data/products_raw.json"
UA={"User-Agent":"Mozilla/5.0"}
def get(url):
    for i in range(3):
        try:
            return ur.urlopen(ur.Request(url,headers=UA),timeout=60).read().decode("utf-8","ignore")
        except Exception as e:
            time.sleep(2)
    return ""
def clean(seg):
    seg=re.sub(r'<script.*?</script>','',seg,flags=re.S)
    t=re.sub(r'<br\s*/?>','\n',seg); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    return [l.strip() for l in t.split('\n') if l.strip()]
# 1. Kategorien-Baum unter 216
root=get(f"{BASE}/de/category/216/plattenleger")
i=root.find('href="/de/category/216/plattenleger"'); j=root.find('href="/de/category/224/',i)
tree=re.findall(r'href="(/de/category/(\d+)/[^"]+)"[^>]*>([^<]+)<',root[i:j])
cats={cid:(html.unescape(name).strip(),path) for path,cid,name in tree}
print("Kategorien:",cats,file=sys.stderr)
# 2. Produkt-IDs je Kategorie
prod_cats={}
for cid,(name,path) in cats.items():
    p=1
    while True:
        h=get(f"{BASE}{path}?pagenum={p}")
        ids=re.findall(r'/de/product/(\d+)/[^"?]*\?CatID=%s'%cid,h)
        m=re.search(r'var Pages = (\d+)',h); pages=int(m.group(1)) if m else 1
        for pid in ids: prod_cats.setdefault(pid,set()).add(cid)
        print(name,p,"/",pages,len(ids),file=sys.stderr)
        if p>=pages or not ids: break
        p+=1
print("Produkte total:",len(prod_cats),file=sys.stderr)
# 3. Produktseiten
def scrape(pid):
    h=get(f"{BASE}/de/product/{pid}/x")
    m=re.search(r'id="ProductPic%s"[^>]*src="([^"]+)"[^>]*alt="([^"]*)"'%pid,h)
    img=BASE+m.group(1) if m else ""; name=html.unescape(m.group(2)) if m else ""
    # Beschreibungsblock: von Produktbild bis Warenkorb
    k=h.find('id="ProductPic%s"'%pid); seg=h[k:k+30000] if k>0 else h
    lines=clean(seg)
    # breadcrumb
    bc=re.findall(r'SectionTitleText[^>]*>(?:<a[^>]*>)?([^<]+)<',h[:k] if k>0 else h)
    txt="\n".join(lines)
    art=re.search(r'Art\.:\s*\n?\s*([^\n]+)',txt); price=re.findall(r'CHF\s*([\d\'\.]+)',txt)
    avail=re.search(r'Verfügbarkeit:\s*\n?\s*([^\n]+)',txt)
    # Beschreibung = Zeilen nach Name bis "Art.:"
    desc=[]
    started=False
    for l in lines:
        if not started:
            if l==name: started=True
            continue
        if l.startswith('Art.:') or l.startswith('Verfügbarkeit') or l.startswith('CHF') or l in('–','+','In den Warenkorb','Auf Wunschliste','Variante wählen'): 
            if l.startswith('Art.:'): break
            continue
        desc.append(l)
    # Varianten (select options)
    variants=[html.unescape(v).strip() for v in re.findall(r'<option[^>]*>([^<]+)</option>',seg)]
    variants=[v for v in variants if v and 'wählen' not in v.lower()]
    return dict(id=pid,url=f"{BASE}/de/product/{pid}/{name and re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')}?CatID=216",
        name=name,image=img,breadcrumb=[html.unescape(b).strip() for b in bc],
        description="\n".join(desc)[:3000],artnr=art.group(1).strip() if art else "",
        price_chf=price[0] if price else "",availability=avail.group(1).strip() if avail else "",
        variants=variants[:30],categories=sorted(prod_cats[pid]))
with cf.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(scrape,sorted(prod_cats)))
json.dump({"categories":{k:v[0] for k,v in cats.items()},"products":res},open(OUT,"w"),ensure_ascii=False,indent=1)
print("done",len(res),file=sys.stderr)
