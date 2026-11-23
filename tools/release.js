/* Raise the version numbers before a release, so that browsers fetch what changed.

     node tools/release.js patch      fixes and small changes      (1.0.0 -> 1.0.1)
     node tools/release.js minor      new features                 (1.0.3 -> 1.1.0)
     node tools/release.js major      a large change of the whole  (1.4.2 -> 2.0.0)
     node tools/release.js 1.2.0      a version you name
     node tools/release.js --check    show what would change, write nothing (add it to any of the above)
   The level has to be given: decide it for each release from what changed, and tell the user. A version written as 1.0 counts as 1.0.0.

   What it does:
   - data/core.js, data/rest.js, data/photos.js: when a file differs from the last release, its ?v= number goes up by one
     in fernweh.html and sw.js. The last release is remembered in tools/versions.json (a hash and a number for each file).
   - APPV and APPD in fernweh.html (shown on the About page) become the new version and today's date.
   - CACHE in sw.js gets the next number, which makes installed copies take the new page.

   Order when photos changed: push the photo repository first, wait for its site, then push this one. */
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const root = path.join(__dirname, '..'), F = f => path.join(root, f), check = process.argv.includes('--check');
const args = process.argv.slice(2), want = args.find(a => /^\d+\.\d+\.\d+$/.test(a)), level = args.find(a => /^(patch|minor|major)$/.test(a));
if (!want && !level) { console.error('Give the level: patch, minor or major (or a version such as 1.2.0)'); process.exit(1) }
const vfile = F('tools/versions.json'), V = fs.existsSync(vfile) ? JSON.parse(fs.readFileSync(vfile, 'utf8')) : {};
let html = fs.readFileSync(F('fernweh.html'), 'utf8'), sw = fs.readFileSync(F('sw.js'), 'utf8');
const log = [];

for (const f of ['core.js', 'rest.js', 'photos.js']) {
  const hash = crypto.createHash('sha1').update(fs.readFileSync(F('data/' + f))).digest('hex').slice(0, 12);
  const cur = +(new RegExp(f.replace('.', '\\.') + '\\?v=(\\d+)').exec(html) || [])[1];
  if (!cur) throw new Error('no ?v= for ' + f + ' in fernweh.html');
  const old = V[f];
  if (old && old.hash !== hash && old.v === cur) {
    const re = new RegExp(f.replace('.', '\\.') + '\\?v=' + cur + '(?!\\d)', 'g'), to = f + '?v=' + (cur + 1);
    html = html.replace(re, to); sw = sw.replace(re, to); V[f] = { hash, v: cur + 1 }; log.push(`data/${f}: ?v=${cur} -> ${cur + 1}`);
  } else { V[f] = { hash, v: cur }; if (!old) log.push(`data/${f}: recorded at ?v=${cur}`) }
}

/* --record: only note the data files as they are now (used once, when this script was added) */
if (process.argv.includes('--record')) { fs.writeFileSync(vfile, JSON.stringify(V, null, 1) + '\n'); console.log(log.join('\n') || 'recorded'); process.exit(0) }

const av = /const APPV='([\d.]+)',APPD='([\d-]+)'/.exec(html), cv = /const CACHE = 'fernweh-v(\d+)'/.exec(sw);
if (!av || !cv) throw new Error('APPV or CACHE not found');
const [maj, min = 0, pat = 0] = av[1].split('.').map(Number),
  next = want || (level === 'major' ? `${maj + 1}.0.0` : level === 'minor' ? `${maj}.${min + 1}.0` : `${maj}.${min}.${pat + 1}`);
const d = new Date(), today = new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
html = html.replace(av[0], `const APPV='${next}',APPD='${today}'`);
sw = sw.replace(cv[0], `const CACHE = 'fernweh-v${+cv[1] + 1}'`);
log.push(`version ${av[1]} -> ${next} (${today})`, `cache fernweh-v${cv[1]} -> fernweh-v${+cv[1] + 1}`);

console.log(log.join('\n'));
if (check) console.log('(check only: nothing written)');
else { fs.writeFileSync(F('fernweh.html'), html); fs.writeFileSync(F('sw.js'), sw); fs.writeFileSync(vfile, JSON.stringify(V, null, 1) + '\n') }
