"""City photos for Fernweh: find, review, merge.

  python tools/photos.py fetch  [--work DIR]            look up and download photos for the cities in tools/photos-cn.txt
  python tools/photos.py sheet  [--work DIR]            make contact sheets (sheet0.jpg, sheet1.jpg ...) to review by eye
  python tools/photos.py merge  [--work DIR] [id ...]   add the photos to data/photos.js; the ids listed are left out and deleted

How a photo is chosen: the Chinese Wikipedia page of the city gives its Wikidata item; the item must lie within
90 km of the city in our data; its picture (P18) must be a JPEG at least 1000 px wide, wider than tall, with a free
licence (CC0, CC BY, CC BY-SA, public domain). The author and licence go into data/photos.js and show on the About page.

Every batch needs a review before merging: Wikidata pictures of small places are often a railway station, a map,
or a neighbouring town. Look at the sheets, then pass the ids to drop to "merge".

After merging, run "node tools/split-cities.js" so every city with a photo is in data/core.js, and raise the ?v=
numbers for core.js and rest.js in fernweh.html and sw.js. "merge" already raises photos.js and the cache name.

The pictures are not in this repository. They live in the repository "fernweh-photos", checked out beside this one
(../fernweh-photos, or the folder named in the environment variable FERNWEH_PHOTOS), and are served from its own
GitHub Pages site; data/photos.js names that site in FW_PHOTO_BASE. After "merge", commit and push fernweh-photos
first and wait for its site, then push this repository.

Needs Python 3 with Pillow. Requests are batched and spaced out; Wikimedia answers 429 when asked too fast, and the
script waits and tries again."""
import io, json, os, re, sys, time, math, tempfile, collections, urllib.request, urllib.parse, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
PICS = os.path.join(os.environ.get('FERNWEH_PHOTOS') or os.path.join(ROOT, '..', 'fernweh-photos'), '') 
BASE = "window.FW_PHOTO_BASE='https://tantian2005.github.io/fernweh-photos/';\n"
UA = 'FernwehPhotoBuilder/1.1 (personal travel-map project; polite one-time download)'
args = sys.argv[1:]
cmd = args.pop(0) if args else ''
WORK = os.path.join(tempfile.gettempdir(), 'fernweh-photos')
if '--work' in args: i = args.index('--work'); WORK = args[i + 1]; del args[i:i + 2]
os.makedirs(WORK, exist_ok=True)
OUT = os.path.join(WORK, 'cn_new.json')
rd = lambda p: io.open(ROOT + p, encoding='utf-8', newline='').read()
def photos():
    s = rd('data/photos.js'); return json.loads(s[s.index('{'):s.rindex('}') + 1])
def load_new(): return json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}

def cities():
    """rows [id, name, cc, lat, lon, pop, zh] for China, Hong Kong, Macao and Taiwan, from core.js and rest.js"""
    dec = json.JSONDecoder(); core = rd('data/core.js'); rest = rd('data/rest.js')
    data, _ = dec.raw_decode(core, core.index('const DATA=') + 11)
    zh, _ = dec.raw_decode(core, core.index(',ZHJ=') + 5)
    more = json.loads(rest[rest.index('['):rest.rindex(']') + 1])
    zh.update(more[1]); out = []
    for l in (data + '\n' + more[0]).split('\n'):
        p = l.split('|')
        if len(p) > 5 and p[2] in ('CN', 'HK', 'MO', 'TW'):
            z = zh.get(p[0]); out.append([p[0], p[1], p[2], float(p[3]), float(p[4]), float(p[5] or 0), (z[0] if isinstance(z, list) else z) or ''])
    return out

def get(url, tries=6):
    delay = 10
    for _ in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=50) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code in (429, 503):
                w = max(int(e.headers.get('Retry-After', '0') or 0), delay); print('  waiting', w, 's', flush=True)
                time.sleep(w); delay = min(delay * 2, 180); continue
            print('  http', e.code, flush=True); return None
        except Exception as e:
            print('  error', e, flush=True); time.sleep(delay); delay = min(delay * 2, 120)
    return None
def api(host, **kw):
    kw.update(format='json', formatversion='2'); time.sleep(1.5)
    b = get(f'https://{host}/w/api.php?' + urllib.parse.urlencode(kw)); return json.loads(b) if b else {}
def hav(a, b, c, d):
    r = math.pi / 180; p = (c - a) * r; q = (d - b) * r
    return 12742 * math.asin(math.sqrt(math.sin(p / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin(q / 2) ** 2))
chunks = lambda a, n: [a[i:i + n] for i in range(0, len(a), n)]
SUF = ('市', '县', '旗', '区')

def fetch():
    from PIL import Image
    rows = cities(); have = set(photos()); byzh = {}
    for r in rows:
        if r[6]: byzh.setdefault(r[6], []).append(r)
    def find(n):
        for k in [n] + [n + x for x in SUF] + ([n[:-1]] if n[-1] in SUF else []):
            if k in byzh: return max(byzh[k], key=lambda r: r[5])
        b = n[:-1] if n[-1] in SUF and len(n) > 2 else n
        c = [r for k, v in byzh.items() if k.startswith(b) and len(b) >= 2 and '自治' in k for r in v]
        return max(c, key=lambda r: r[5]) if c else None
    res = {k: v for k, v in load_new().items() if 's' in v}; todo, seen, miss = [], set(), []
    def add(r):
        if r and r[0] not in have and r[0] not in seen and r[0] not in res: seen.add(r[0]); todo.append(r)
    for n in io.open(ROOT + 'tools/photos-cn.txt', encoding='utf-8').read().split():
        r = find(n); add(r)
        if not r: miss.append(n)
    provinces = set('湖北 河南 新疆 海南'.split())   # rows that stand for a whole province
    for r in sorted((r for r in rows if r[5] >= 300000 and r[6] not in provinces), key=lambda r: -r[5]): add(r)
    print('not in the data:', ' '.join(miss)); print('to fetch', len(todo), flush=True)
    def titles(r):
        zh = r[6]; base = zh[:-1] if zh[-1] in SUF and len(zh) > 2 else zh; out = [zh]
        for t in (base + '市', base + '县', base):
            if t not in out: out.append(t)
        return out
    # 1. zh.wikipedia: titles -> Wikidata items
    t2q = {}
    for ch in chunks(sorted({t for r in todo for t in titles(r)}), 45):
        q = api('zh.wikipedia.org', action='query', titles='|'.join(ch), prop='pageprops', redirects='1', converttitles='1').get('query', {}); fwd = {}
        for k in ('converted', 'normalized', 'redirects'):
            for m in q.get(k, []): fwd[m['from']] = m['to']
        pages = {p['title']: p for p in q.get('pages', []) if not p.get('missing')}
        for t in ch:
            x = t
            for _ in range(4): x = fwd.get(x, x)
            pp = (pages.get(x) or {}).get('pageprops', {})
            if pp.get('wikibase_item') and 'disambiguation' not in pp: t2q[t] = (pp['wikibase_item'], x)
        print('titles', len(t2q), flush=True)
    # 2. Wikidata: same place? which picture? English title
    ent = {}
    for ch in chunks(sorted({q for q, _ in t2q.values()}), 45):
        ent.update(api('www.wikidata.org', action='wbgetentities', ids='|'.join(ch), props='claims|sitelinks', sitefilter='enwiki').get('entities', {}))
        print('items', len(ent), flush=True)
    val = lambda e, p: [c['mainsnak']['datavalue']['value'] for c in e.get('claims', {}).get(p, []) if c.get('mainsnak', {}).get('datavalue')]
    cand = {}
    for r in todo:
        why = 'no page'
        for t in titles(r):
            e = ent.get(t2q[t][0]) if t in t2q else None
            if not e: continue
            co = val(e, 'P625')
            if not co: why = 'no coordinates'; continue
            if hav(r[3], r[4], co[0]['latitude'], co[0]['longitude']) > 90: why = 'another place'; continue
            files = val(e, 'P18') + val(e, 'P948') + val(e, 'P4291')
            if not files: why = 'no picture'; continue
            cand[r[0]] = (r, files[:4], (e.get('sitelinks', {}).get('enwiki') or {}).get('title') or t2q[t][1]); why = None; break
        if why: res[r[0]] = {'skip': why}; print('skip', r[6], why)
    # 3. Commons: licence and size
    free = re.compile(r'^(CC0|CC BY|CC-BY|Public domain|PD|Attribution)', re.I)
    bad = re.compile(r'montage|collage|mosaic|composite|compilation|\bmap\b|_map|map_|flag|logo|locator|location|emblem|地图|位置|区划|行政|\.svg$|\.png$|\.gif$|\.tiff?$', re.I)
    info = {}
    for ch in chunks(sorted({f for _, fs, _ in cand.values() for f in fs}), 40):
        q = api('commons.wikimedia.org', action='query', titles='|'.join('File:' + f for f in ch), prop='imageinfo', iiprop='url|size|mime|extmetadata', iiurlwidth='1280').get('query', {})
        fwd = {m['from']: m['to'] for m in q.get('normalized', [])}; pages = {p['title']: p for p in q.get('pages', [])}
        for f in ch:
            p = pages.get(fwd.get('File:' + f, 'File:' + f))
            if p and p.get('imageinfo'): info[f] = p['imageinfo'][0]
        print('files', len(info), flush=True)
    # 4. download
    n = 0
    for cid, (r, files, title) in cand.items():
        pick = None
        for f in files:
            ii = info.get(f)
            if not ii or bad.search(f.replace(' ', '_')) or ii.get('mime') != 'image/jpeg' or ii.get('width', 0) < 1000: continue
            m = ii.get('extmetadata', {}); lic = (m.get('LicenseShortName') or {}).get('value', '')
            if not free.search(lic) or ii['width'] < ii['height'] * 1.15 or ii['width'] > ii['height'] * 2.7: continue
            pick = (f, ii, lic, m); break
        if not pick: res[cid] = {'skip': 'nothing free, large and wide'}; print('skip', r[6]); continue
        f, ii, lic, m = pick
        au = re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', (m.get('Artist') or {}).get('value', ''))).strip()[:80]
        time.sleep(2.5); img = get(ii.get('thumburl') or ii['url'])
        try: im = Image.open(io.BytesIO(img)).convert('RGB')
        except Exception: res[cid] = {'skip': 'download failed'}; print('skip', r[6], 'download failed'); continue
        if im.width > 1024: im = im.resize((1024, round(im.height * 1024 / im.width)), Image.LANCZOS)
        im.save(PICS + f'png/{cid}.webp', 'WEBP', quality=78, method=5)
        W, H = im.size; tw = min(W, H * 4 / 3); th = tw * 3 / 4
        im.crop(((W - tw) / 2, (H - th) / 2, (W + tw) / 2, (H + th) / 2)).resize((480, 360), Image.LANCZOS).save(PICS + f'png/thumb/{cid}.webp', 'WEBP', quality=72, method=6)
        res[cid] = {'s': f'png/thumb/{cid}.webp', 'h': f'png/{cid}.webp', 't': title, 'p': ii.get('descriptionurl') or '', 'a': au, 'l': lic, 'zh': r[6], 'f': f}
        n += 1; print(f'[{n}] ok', r[6], lic, f[:60], flush=True)
        json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('done:', sum(1 for v in res.values() if 's' in v), 'photos,', sum(1 for v in res.values() if 'skip' in v), 'skipped')

def sheet():
    from PIL import Image, ImageDraw, ImageFont
    ok = [(k, v) for k, v in load_new().items() if 's' in v and os.path.exists(PICS + v['s'])]
    W, H, C, per = 240, 180, 8, 48
    try: f = ImageFont.truetype('msyh.ttc', 13)
    except Exception: f = ImageFont.load_default()
    for p in range(0, len(ok), per):
        ch = ok[p:p + per]; rows = (len(ch) + C - 1) // C
        im = Image.new('RGB', (C * W, rows * (H + 20)), 'white'); d = ImageDraw.Draw(im)
        for i, (k, v) in enumerate(ch):
            x, y = (i % C) * W, (i // C) * (H + 20)
            im.paste(Image.open(PICS + v['s']).convert('RGB').resize((W - 4, H - 4)), (x + 2, y + 2)); d.text((x + 3, y + H - 1), f"{k[-5:]} {v.get('zh', '')} {v['t'][:14]}", fill='black', font=f)
        o = os.path.join(WORK, f'sheet{p // per}.jpg'); im.save(o, quality=82); print(o, len(ch))

def merge():
    drop = set(args); P = photos(); n0 = len(P); new = load_new()
    for k, v in new.items():
        if 's' not in v or k in P: continue
        if k in drop or any(k.endswith(x) and len(x) >= 5 for x in drop):
            for f in (v['s'], v['h']):
                if os.path.exists(PICS + f): os.remove(PICS + f)
            continue
        if os.path.exists(PICS + v['s']) and os.path.exists(PICS + v['h']): P[k] = {x: v[x] for x in ('s', 'h', 't', 'p', 'a', 'l')}
    io.open(ROOT + 'data/photos.js', 'w', encoding='utf-8', newline='').write('window.FW_PHOTOS=' + json.dumps(P, ensure_ascii=False, separators=(',', ':')) + ';\n' + BASE)
    def bump(path, pat, fmt):
        t = rd(path); t2, k = re.subn(pat, lambda m: fmt % (int(m[1]) + 1), t); assert k >= 1, (path, pat)
        io.open(ROOT + path, 'w', encoding='utf-8', newline='').write(t2)
    bump('fernweh.html', r'photos\.js\?v=(\d+)', 'photos.js?v=%d'); bump('sw.js', r'photos\.js\?v=(\d+)', 'photos.js?v=%d'); bump('sw.js', r"CACHE = 'fernweh-v(\d+)'", "CACHE = 'fernweh-v%d'")
    print('photos', n0, '->', len(P)); print('next: node tools/split-cities.js, raise ?v= for core.js and rest.js; push fernweh-photos before this repository')

{'fetch': fetch, 'sheet': sheet, 'merge': merge}.get(cmd, lambda: print(__doc__))()
