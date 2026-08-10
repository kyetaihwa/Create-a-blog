#!/usr/bin/env python3
import json, html, re
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / 'site.config.json').read_text(encoding='utf-8'))
posts = json.loads((ROOT / 'data/posts.json').read_text(encoding='utf-8'))
posts = [p for p in posts if p.get('published', True)]
posts.sort(key=lambda p: p['date'], reverse=True)
base = config['siteUrl'].rstrip('/')


def inline_md(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def markdown_to_html(md):
    lines = md.splitlines()
    out, paragraph = [], []

    def flush():
        nonlocal paragraph
        if paragraph:
            out.append('<p>' + '<br>'.join(inline_md(x.rstrip('  ')) for x in paragraph) + '</p>')
            paragraph = []

    for line in lines:
        if not line.strip():
            flush()
        elif line.startswith('### '):
            flush(); out.append('<h3>' + inline_md(line[4:]) + '</h3>')
        elif line.startswith('## '):
            flush(); out.append('<h2>' + inline_md(line[3:]) + '</h2>')
        elif line.startswith('# '):
            flush(); out.append('<h1>' + inline_md(line[2:]) + '</h1>')
        else:
            paragraph.append(line)
    flush()
    return '\n'.join(out)

naver = config.get('naverSiteVerification', '').strip()
google = config.get('googleSiteVerification', '').strip()
naver_meta = f'<meta name="naver-site-verification" content="{html.escape(naver)}">' if naver else ''
google_meta = f'<meta name="google-site-verification" content="{html.escape(google)}">' if google else ''
verify_meta = naver_meta + google_meta

for p in posts:
    md_path = ROOT / 'posts' / f"{p['slug']}.md"
    if not md_path.exists():
        continue
    body = markdown_to_html(md_path.read_text(encoding='utf-8'))
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(p['title'])} | {html.escape(config['siteName'])}</title><meta name="description" content="{html.escape(p.get('description',''))}"><meta name="robots" content="index,follow">{verify_meta}<link rel="canonical" href="{base}/posts/{html.escape(p['slug'])}.html"><link rel="stylesheet" href="../assets/style.css"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(p['title'])}"><meta property="og:description" content="{html.escape(p.get('description',''))}"><meta property="og:url" content="{base}/posts/{html.escape(p['slug'])}.html"></head><body><header class="site-header"><div class="wrap header-inner"><a class="brand" href="../index.html">{html.escape(config['siteName'])}</a><nav class="nav"><a href="../index.html">글 목록</a></nav></div></header><main class="wrap"><article class="post"><div class="meta">{html.escape(p['date'])} · {html.escape(p.get('category',''))}</div>{body}</article></main><footer><div class="wrap">© {datetime.now().year} {html.escape(config['siteName'])}</div></footer></body></html>'''
    (ROOT / 'posts' / f"{p['slug']}.html").write_text(page, encoding='utf-8')

cards = '\n'.join(f'<a class="post-card" href="posts/{html.escape(p["slug"])}.html"><div class="meta">{html.escape(p["date"])} · {html.escape(p.get("category",""))}</div><h2>{html.escape(p["title"])}</h2><p>{html.escape(p.get("description",""))}</p></a>' for p in posts)
index = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(config["siteName"])}</title><meta name="description" content="{html.escape(config["siteDescription"])}"><meta name="robots" content="index,follow">{verify_meta}<link rel="canonical" href="{base}/"><link rel="alternate" type="application/rss+xml" title="RSS" href="{base}/rss.xml"><link rel="stylesheet" href="assets/style.css"><meta property="og:type" content="website"><meta property="og:title" content="{html.escape(config["siteName"])}"><meta property="og:description" content="{html.escape(config["siteDescription"])}"><meta property="og:url" content="{base}/"></head><body><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html">{html.escape(config["siteName"])}</a><nav class="nav"><a href="index.html">글 목록</a><a href="rss.xml">RSS</a></nav></div></header><main class="wrap"><section class="hero"><h1>{html.escape(config["siteName"])}</h1><p>{html.escape(config["siteDescription"])}</p></section><section class="post-list">{cards}</section></main><footer><div class="wrap">© {datetime.now().year} {html.escape(config["siteName"])}</div></footer></body></html>'
(ROOT / 'index.html').write_text(index, encoding='utf-8')
urls = [('/', max((p.get('updated', p['date']) for p in posts), default=datetime.now().date().isoformat()))] + [(f"/posts/{p['slug']}.html", p.get('updated', p['date'])) for p in posts]
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{escape(base + path)}</loc><lastmod>{last}</lastmod></url>\n' for path, last in urls) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n', encoding='utf-8')
items = ''.join(f'<item><title>{escape(p["title"])}</title><link>{escape(base+"/posts/"+p["slug"]+".html")}</link><guid>{escape(base+"/posts/"+p["slug"]+".html")}</guid><pubDate>{datetime.strptime(p["date"],"%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0900")}</pubDate><description>{escape(p.get("description",""))}</description></item>' for p in posts)
(ROOT / 'rss.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{escape(config["siteName"])}</title><link>{escape(base+"/")}</link><description>{escape(config["siteDescription"])}</description><language>ko-KR</language>{items}</channel></rss>', encoding='utf-8')
print('Generated posts, index.html, sitemap.xml, robots.txt, rss.xml')
