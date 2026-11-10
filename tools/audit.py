"""Static checks on fernweh.html. Run from the repository root:  python tools/audit.py

Lists names defined but never used, click actions without a handler (and handlers without a button),
CSS classes that no markup uses, English strings that still hold Chinese, and Chinese text outside tr().
The last list is long by nature (name tables); read it for new entries only."""
import io,re,sys,os
sys.stdout.reconfigure(encoding='utf-8')
s=io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fernweh.html'),encoding='utf-8').read()
css=''.join(m.group(1) for m in re.finditer(r'<style[^>]*>(.*?)</style>',s,re.S))
js=max((m.group(1) for m in re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>',s,re.S)),key=len)
html=re.sub(r'<style.*?</style>|<script.*?</script>','',s,flags=re.S)
print('sizes: css',len(css),'js',len(js),'html',len(html))

# 1. functions and top-level consts that are never used
names=set(re.findall(r'\bfunction (\w+)\(',js))
names|=set(re.findall(r'(?:^|[;\n,{}])\s*(?:const|let)\s+(\w+)=',js))
names|=set(re.findall(r',(\w+)=(?:\([^()]*\)|\w+)=>',js))
unused=[]
for n in sorted(names):
    c=len(re.findall(r'(?<![\w$.])'+re.escape(n)+r'(?![\w$])',js))
    if c<=1: unused.append(n)
print('\nNAMES USED ONCE (defined, never referenced):',len(unused)); print(' '.join(unused))

# 2. click actions: data-a values in markup vs case labels
acts=set(re.findall(r'data-a="([a-z0-9]+)"',js+html))
i=js.index("el.onclick="); blk=js[i:js.index("el.onchange=",i)]
cases=set(re.findall(r"case'(\w+)'",blk))
print('\nACTIONS with no case:',sorted(acts-cases)); print('CASES with no markup:',sorted(cases-acts))

# 3. CSS: class and id selectors that never appear in js/html
used=js+html
cls=set(re.findall(r'\.([a-zA-Z][\w-]*)',re.sub(r'url\([^)]*\)|\d\.\d|[\d.]+(px|s|em|%)','',css)))
ids=set(re.findall(r'#([a-zA-Z][\w-]*)',re.sub(r'#[0-9a-fA-F]{3,8}\b','',css)))
dead=[c for c in sorted(cls) if not re.search(r'(?<![\w-])'+re.escape(c)+r'(?![\w-])',used)]
deadi=[c for c in sorted(ids) if not re.search(r'(?<![\w-])'+re.escape(c)+r'(?![\w-])',used)]
print('\nCSS classes not in js/html:',len(dead)); print(' '.join(dead)); print('CSS ids not in js/html:',' '.join(deadi))

# 4. copy: tr() pairs whose English side has CJK, middots in strings, Chinese outside tr()
cjk=re.compile(r'[\u4e00-\u9fff]')
bad=[m.group(0)[:90] for m in re.finditer(r"tr\('((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\)",js) if cjk.search(m.group(2))]
print('\ntr() with CJK in the English side:',len(bad)); print('\n'.join(bad[:20]))
mid=[js[max(0,m.start()-50):m.start()+30].replace('\n',' ') for m in re.finditer('[·•]',js)]
print('\nmiddots/bullets in js:',len(mid)); print('\n'.join(mid[:25]))
# string literals with CJK that are not inside tr(...) first arg or known tables
lits=[]
for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'|`((?:[^`\\]|\\.)*)`|\"((?:[^\"\\\n]|\\.)*)\"",js):
    t=m.group(1) or m.group(2) or m.group(3) or ''
    if not cjk.search(t): continue
    pre=js[max(0,m.start()-4):m.start()]
    if pre.endswith('tr('): continue
    if m.group(2) is not None:
        # template: strip ${...tr('..','..')...} occurrences
        t2=re.sub(r"tr\(`(?:[^`\\]|\\.)*`,`(?:[^`\\]|\\.)*`\)|tr\('(?:[^'\\]|\\.)*','(?:[^'\\]|\\.)*'\)",'',t)
        if not cjk.search(t2): continue
        t=t2
    lits.append((m.start(),t[:70].replace('\n',' ')))
print('\nCJK string literals outside tr():',len(lits))
for a,t in lits[:120]: print(a,t)

# 5. misc
for pat in [r'console\.\w+\(',r'\bdebugger\b',r'TODO|FIXME|XXX',r'alert\(',r'confirm\(',r'innerHTML\s*=',r'localStorage\.\w+\(',r'setInterval\(',r'eval\(|new Function']:
    print(pat,len(re.findall(pat,js)))
print('aria- in file',len(re.findall('aria-',s)),' | tr() calls',len(re.findall(r'\btr\(',js)),' | functions',len(re.findall(r'\bfunction \w+\(',js)))
