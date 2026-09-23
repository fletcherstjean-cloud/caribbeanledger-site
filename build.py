#!/usr/bin/env python3
# The Caribbean Ledger — site build. Cloudflare Pages runs: python3 build.py  (output dir: dist)
import json, re, os, base64, html, datetime, shutil

BASE = os.environ.get("SITE_BASE", "https://www.caribbeanledger.com")
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "dist")
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT + "/stories"); os.makedirs(OUT + "/images")

arts = json.load(open(os.path.join(ROOT, "content", "articles.json"), encoding="utf-8"))

# --- homepage (interactive app) and static assets ---
shutil.copyfile(os.path.join(ROOT, "app", "index.html"), os.path.join(OUT, "index.html"))
shutil.copyfile(os.path.join(ROOT, "assets", "og-card.png"), os.path.join(OUT, "og-card.png"))

def slugify(s):
    s = re.sub(r"[’'\"]", "", s or "")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:70] or "story"
used = set()
def uniq(b):
    s=b; n=2
    while s in used: s=f"{b}-{n}"; n+=1
    used.add(s); return s
MONTHS={m:i for i,m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"],1)}
def iso(f):
    m=re.match(r"([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})",(f or "").strip())
    if not m: return None
    mo=MONTHS.get(m.group(1));
    return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(2)):02d}" if mo else None
def esc(x): return html.escape(x or "", quote=True)
def wimg(slug, uri):
    m=re.match(r"data:image/(\w[\w+]*);base64,(.*)", uri, re.S)
    if not m: return None
    ext={"jpeg":"jpg","jpg":"jpg","png":"png","webp":"webp","gif":"gif","svg+xml":"svg"}.get(m.group(1),"jpg")
    fn=f"{slug}.{ext}"; open(f"{OUT}/images/{fn}","wb").write(base64.b64decode(m.group(2))); return fn
def blocks(bs):
    o=[]
    for b in (bs or []):
        t=b.get("t")
        if t=="p": o.append(f"<p>{esc(b.get('x'))}</p>")
        elif t=="h": o.append(f"<h2>{esc(b.get('x'))}</h2>")
        elif t=="stat":
            it="".join(f"<div class='stat'><span class='n'>{esc(i.get('n'))}</span><span class='l'>{esc(i.get('l'))}</span></div>" for i in b.get("items",[]))
            o.append(f"<div class='stats'>{it}</div>")
        elif t=="img": o.append(f"<figure><img src='{esc(b.get('src'))}' alt=''></figure>")
        elif t in ("q","quote"): o.append(f"<blockquote>{esc(b.get('x') or b.get('text'))}</blockquote>")
    return "\n".join(o)
CSS=""":root{--paper:#FBF6E9;--ink:#211E17;--ink2:#4A4436;--muted:#7C7460;--navy:#0F1B2D;--gold:#8F6E2E;--rule:#E4DAC0}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Georgia,'Times New Roman',serif;line-height:1.6}
.wrap{max-width:720px;margin:0 auto;padding:0 20px}header.mast{border-bottom:2px solid var(--navy);margin-bottom:28px}
.mast .wrap{padding:18px 20px;display:flex;justify-content:space-between;align-items:baseline}
.mast a.brand{font-weight:bold;font-size:22px;color:var(--navy);text-decoration:none}.mast .tag{font-family:Arial,sans-serif;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
.eyebrow{font-family:Arial,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}
h1{font-size:34px;line-height:1.15;margin:0 0 14px;color:var(--navy)}.stand{font-size:19px;color:var(--ink2);margin:0 0 16px}
.byline{font-family:Arial,sans-serif;font-size:13px;color:var(--muted);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;margin-bottom:22px}
.hero{width:100%;border-radius:4px;margin-bottom:22px}article p{font-size:18px;margin:0 0 18px}article h2{font-size:23px;color:var(--navy);margin:28px 0 12px}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:22px 0;padding:18px;background:#fff;border:1px solid var(--rule);border-radius:4px}
.stat .n{display:block;font-size:26px;font-weight:bold;color:var(--gold)}.stat .l{display:block;font-family:Arial,sans-serif;font-size:12px;color:var(--muted);line-height:1.4}
figure{margin:20px 0}figure img{width:100%;border-radius:4px}blockquote{border-left:3px solid var(--gold);margin:20px 0;padding:4px 0 4px 18px;font-size:20px;color:var(--ink2)}
footer{border-top:2px solid var(--navy);margin-top:40px;padding:22px 0 40px;font-family:Arial,sans-serif;font-size:13px;color:var(--muted)}footer a{color:var(--gold)}
.readapp{display:inline-block;margin-top:8px;font-family:Arial,sans-serif;font-size:13px}"""
sm=[("/","1.0",None)]; idx=[]
for a in arts:
    hd=a.get("headline")
    if not hd: continue
    slug=uniq(slugify(a.get("id") or hd)); url=f"{BASE}/stories/{slug}.html"
    stand=a.get("stand",""); desc=(stand or hd)[:200]; sec=a.get("sec",""); sub=a.get("sub","")
    eye=a.get("eyebrow") or (f"{sec} · {sub}" if sub else sec); by=a.get("byline") or "The Caribbean Ledger"
    filed=a.get("filed",""); pub=iso(filed); imgfn=wimg(slug,a["img"]) if a.get("img") else None
    img_abs=f"{BASE}/images/{imgfn}" if imgfn else f"{BASE}/og-card.png"
    hero=f"<img class='hero' src='../images/{imgfn}' alt='{esc(hd)}'>" if imgfn else ""
    person = by and 'ledger' not in by.lower() and 'desk' not in by.lower() and ' ' in by
    ld={"@context":"https://schema.org","@type":"NewsArticle","headline":hd[:110],"description":desc,"image":[img_abs],
        "mainEntityOfPage":{"@type":"WebPage","@id":url},"author":{"@type":"Person" if person else "Organization","name":by if person else "The Caribbean Ledger"},
        "publisher":{"@type":"Organization","name":"The Caribbean Ledger","logo":{"@type":"ImageObject","url":f"{BASE}/og-card.png"}},"articleSection":sec or "News"}
    if pub: ld["datePublished"]=pub; ld["dateModified"]=pub
    doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(hd)} — The Caribbean Ledger</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="The Caribbean Ledger"><meta property="og:title" content="{esc(hd)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img_abs}">
{f'<meta property="article:published_time" content="{pub}">' if pub else ''}<meta property="article:section" content="{esc(sec)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(hd)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{img_abs}">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script><style>{CSS}</style></head><body>
<header class="mast"><div class="wrap"><a class="brand" href="{BASE}/">The Caribbean Ledger</a><span class="tag">Every island · One Caribbean</span></div></header>
<div class="wrap"><article><div class="eyebrow">{esc(eye)}</div><h1>{esc(hd)}</h1>{f'<p class="stand">{esc(stand)}</p>' if stand else ''}
<div class="byline">{esc(by)}{(' · '+esc(filed)) if filed else ''}</div>{hero}{blocks(a.get('blocks'))}
<a class="readapp" href="{BASE}/">Read more at The Caribbean Ledger &rsaquo;</a></article>
<footer><div>The Caribbean Ledger · Published by St. Jean &amp; Co.</div><div><a href="{BASE}/">Home</a> · <a href="{BASE}/stories/">All stories</a></div></footer></div></body></html>"""
    open(f"{OUT}/stories/{slug}.html","w",encoding="utf-8").write(doc)
    sm.append((f"/stories/{slug}.html","0.8",pub)); idx.append((hd,f"/stories/{slug}.html",sec,filed))
lis="\n".join(f"<li><a href='.{u[len('/stories'):]}'>{esc(h)}</a> <span class='m'>{esc(s)}{(' · '+esc(f)) if f else ''}</span></li>" for h,u,s,f in idx)
open(f"{OUT}/stories/index.html","w",encoding="utf-8").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>All stories — The Caribbean Ledger</title><meta name="description" content="Every story from The Caribbean Ledger."><link rel="canonical" href="{BASE}/stories/">
<style>{CSS} li{{margin:8px 0;list-style:none}}ul{{padding:0}}.m{{font-family:Arial;font-size:12px;color:var(--muted)}}</style></head><body>
<header class="mast"><div class="wrap"><a class="brand" href="{BASE}/">The Caribbean Ledger</a><span class="tag">All stories</span></div></header>
<div class="wrap"><h1>All stories</h1><ul>{lis}</ul><footer><a href="{BASE}/">Home</a></footer></div></body></html>""")
sm.append(("/stories/","0.6",None))
today=datetime.date.today().isoformat()
rows=[f"  <url><loc>{BASE}{loc}</loc><lastmod>{lm or today}</lastmod><priority>{pr}</priority></url>" for loc,pr,lm in sm]
open(f"{OUT}/sitemap.xml","w",encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(rows)+"\n</urlset>\n")
open(f"{OUT}/robots.txt","w",encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
print("BUILD OK — pages:", len(idx), "images:", len(os.listdir(OUT+'/images')))
