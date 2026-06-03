#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

BASE_URL = 'https://ideaproject.agency'
ROOT = Path(__file__).parent

def make_url(loc, lastmod=None):
    url = ET.Element('url')
    loc_el = ET.SubElement(url, 'loc')
    loc_el.text = loc
    if lastmod:
        lm = ET.SubElement(url, 'lastmod')
        lm.text = lastmod
    return url

def format_lastmod(path: Path):
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).date().isoformat()

def build_urls():
    urls = []

    # HTML files in root (excluding this script and sitemap itself)
    for f in ROOT.glob('*.html'):
        rel = f.name
        if rel == 'sitemap.xml':
            continue
        if rel == 'index.html':
            loc = BASE_URL + '/'
        else:
            loc = f"{BASE_URL}/{rel}"
        urls.append((loc, format_lastmod(f)))

    # All HTML under pages/
    pages_dir = ROOT / 'pages'
    if pages_dir.exists():
        for f in pages_dir.rglob('*.html'):
            # skip assets directories just in case
            if 'assets' in f.parts:
                continue
            rel = f.relative_to(ROOT).as_posix()
            parts = Path(rel).parts
            # If file is an index.html, map to the directory URL with trailing slash
            if f.name == 'index.html':
                parent = f.parent.relative_to(ROOT).as_posix()
                loc = f"{BASE_URL}/{parent}/"
            else:
                loc = f"{BASE_URL}/{rel}"
            urls.append((loc, format_lastmod(f)))

    # Deduplicate while preserving order
    seen = set()
    out = []
    for loc, lastmod in urls:
        if loc in seen:
            continue
        seen.add(loc)
        out.append((loc, lastmod))
    return out

def write_sitemap(urls):
    urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for loc, lastmod in urls:
        urlset.append(make_url(loc, lastmod))

    tree = ET.ElementTree(urlset)
    # Pretty-printing: indent
    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(urlset)
    out_path = ROOT / 'sitemap.xml'
    tree.write(out_path, encoding='utf-8', xml_declaration=True)
    print(f'Wrote {out_path}')

def main():
    urls = build_urls()
    write_sitemap(urls)

if __name__ == '__main__':
    main()
