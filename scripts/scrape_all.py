#!/usr/bin/env python3
"""Scrapt den ganzen Shop: alle Kategorien aus der Navigation, alle Produkte."""
import re, html, json, sys, time, concurrent.futures as cf
import urllib.request as ur
BASE="https://shop.ferronato.ch"
UA={"User-Agent":"Mozilla/5.0"}
def get(url):
    for i in range(3):
        try: return ur.urlopen(ur.Request(url,headers=UA),timeout=60).read().decode("utf-8","ignore")
        except Exception: time.sleep(2)
    return ""
root=get(f"{BASE}/de")
cats={}  # cid -> (name, path)
for path,cid,name in re.findall(r'href="(/de/category/(\d+)/[^"]+)"[^>]*>([^<]+)<',root):
    n=html.unescape(name).strip()
    if n and cid not in cats: cats[cid]=(n,path.split('?')[0])
print("Kategorien:",len(cats),file=sys.stderr)
prod_cats={}
def list_cat(item):
    cid,(name,path)=item
    out=set(); p=1; pages=1
    while p<=pages:
        h=get(f"{BASE}{path}?pagenum={p}")
        m=re.search(r'var Pages = (\d+)',h); pages=int(m.group(1)) if m else 1
        ids=set(re.findall(r'/de/product/(\d+)/[^"?]*\?CatID=%s"'%cid,h))
        out|=ids
        if not ids: break
        p+=1
    return cid,out
with cf.ThreadPoolExecutor(10) as ex:
    for cid,ids in ex.map(list_cat,cats.items()):
        for pid in ids: prod_cats.setdefault(pid,set()).add(cid)
        print(cats[cid][0],len(ids),file=sys.stderr)
print("Produkte total:",len(prod_cats),file=sys.stderr)
def scrape(pid):
    h=get(f"{BASE}/de/product/{pid}/x")
    m=re.search(r'id="ProductPic%s"[^>]*src="([^"]+)"[^>]*alt="([^"]*)"'%pid,h)
    img=BASE+m.group(1) if m else ""; name=html.unescape(m.group(2)) if m else ""
    bc=[html.unescape(b).strip() for b in re.findall(r'SectionTitleText"[^>]*>([^<]+)</a>',h)]
    k=h.find('id="ProductPic%s"'%pid); seg=h[k:k+30000] if k>0 else h
    seg=re.sub(r'<script.*?</script>|<style.*?</style>','',seg,flags=re.S)
    t=re.sub(r'<br\s*/?>','\n',seg); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    txt="\n".join(lines)
    art=re.search(r'Art\.:\s*\n?\s*([^\n]+)',txt); price=re.findall(r'CHF\s*([\d\'\.]+)',txt)
    avail=re.search(r'Verfügbarkeit:\s*\n?\s*([^\n]+)',txt)
    desc=[]; started=False; CSS=re.compile(r'[{}]|!important|^\s*(width|position|max-width|background|top|left|z-index|display|padding|margin|border|color|font)\s*:')
    incss=False
    for l in lines:
        if not started:
            if l==name: started=True
            continue
        if l.startswith('Art.:'): break
        if '{' in l: incss=True
        if incss:
            if '}' in l: incss=False
            continue
        if CSS.search(l) or re.match(r'^[.#][\w\-]',l) or l in('–','+','In den Warenkorb','Auf Wunschliste','Variante wählen') or l.startswith('Verfügbarkeit') or l.startswith('CHF'): continue
        desc.append(l)
    variants=[html.unescape(v).strip() for v in re.findall(r'<option[^>]*>([^<]+)</option>',seg)]
    variants=[v for v in variants if v and 'wählen' not in v.lower()]
    return dict(id=pid,url=f"{BASE}/de/product/{pid}/x",name=name,image=img,breadcrumb=bc,
        description="\n".join(desc)[:3000],artnr=art.group(1).strip() if art else "",
        price_chf=price[0] if price else "",availability=avail.group(1).strip() if avail else "",
        variants=variants[:30],cat_names=sorted({cats[c][0] for c in prod_cats[pid]}))
with cf.ThreadPoolExecutor(10) as ex:
    res=[]
    for i,r in enumerate(ex.map(scrape,sorted(prod_cats))):
        res.append(r)
        if i%200==0: print(i,file=sys.stderr)
json.dump({"categories":{k:v[0] for k,v in cats.items()},"products":res},open("data/all_products_raw.json","w"),ensure_ascii=False,indent=1)
print("done",len(res),file=sys.stderr)
