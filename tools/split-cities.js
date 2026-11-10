/* Split the city data into the two files the app loads.

   data/core.js  loads first: borders, flags, country names, and the cities needed to draw the first map
                 (population of CORE_POP or more, every city with a photo or landmark, and the demo cities).
   data/rest.js  loads in the background: every other city, their Chinese names, and state borders.

   Run from the repository root:   node tools/split-cities.js
   It reads data/cities.js if that file is there (the old single file), otherwise it merges the two
   files back together and splits them again, so it is safe to run after editing either file.
   After running, raise the ?v= numbers for core.js and rest.js in fernweh.html and sw.js. */
const fs = require('fs'), zlib = require('zlib'), path = require('path');
const root = path.join(__dirname, '..'), D = f => path.join(root, 'data', f);
const CORE_POP = 50000;

const NAMES = ['DATA', 'TOPO', 'CT', 'ZHJ', 'FL', 'PROV', 'LM', 'ALI', 'HIDE'];
let all;
if (fs.existsSync(D('cities.js'))) {
  all = new Function(fs.readFileSync(D('cities.js'), 'utf8') + ';return {' + NAMES.join(',') + ',ADMIN}')();
} else {
  all = new Function(fs.readFileSync(D('core.js'), 'utf8') + ';return {' + NAMES.join(',') + '}')();
  const w = {}; new Function('window', fs.readFileSync(D('rest.js'), 'utf8'))(w);
  const [rows, zh, admin] = w.FW_REST;
  all.DATA += '\n' + rows; Object.assign(all.ZHJ, zh); all.ADMIN = admin;
}

const rows = all.DATA.split('\n').filter(Boolean), pop = l => +l.split('|')[5] || 0, id = l => l.split('|')[0];
rows.sort((a, b) => pop(b) - pop(a));               /* stable: equal populations keep their order */

const keep = new Set(Object.keys(all.LM));
const photos = new Function('window', fs.readFileSync(D('photos.js'), 'utf8') + ';return window.FW_PHOTOS');
for (const k in photos({})) if (/^\d+$/.test(k)) keep.add(k);
/* cities the app names in its own code: the demo, and the sample postcards */
const html = fs.readFileSync(path.join(root, 'fernweh.html'), 'utf8'), named = new Set();
for (const m of html.matchAll(/\['([^'\]]+)','([A-Z]{2})','\d{4}-\d{2}-\d{2}'/g)) named.add(m[1] + '|' + m[2]);
for (const m of html.matchAll(/lg\('([^']+)','([A-Z]{2})'/g)) named.add(m[1] + '|' + m[2]);
const seen = new Set();
for (const l of rows) { const p = l.split('|'), k = p[1] + '|' + p[2]; if (named.has(k) && !seen.has(k)) { seen.add(k); keep.add(p[0]) } }
for (const k of named) if (!seen.has(k)) console.warn('named in the app but not in the data:', k);

const core = [], rest = [];
for (const l of rows) (pop(l) >= CORE_POP || keep.has(id(l)) ? core : rest).push(l);
const coreIds = new Set(core.map(id)), zhCore = {}, zhRest = {};
for (const k in all.ZHJ) (coreIds.has(k) ? zhCore : zhRest)[k] = all.ZHJ[k];

const J = JSON.stringify, a = all;
const coreJs = `const DATA=${J(core.join('\n'))},TOPO=${J(a.TOPO)},CT=${J(a.CT)},ZHJ=${J(zhCore)},FL=${J(a.FL)},PROV=${J(a.PROV)},LM=${J(a.LM)};\nconst ALI=${J(a.ALI)},HIDE=${J(a.HIDE)};\n`;
const restJs = `window.FW_REST=[${J(rest.join('\n'))},${J(zhRest)},${J(a.ADMIN)}];\n`;
fs.writeFileSync(D('core.js'), coreJs); fs.writeFileSync(D('rest.js'), restJs);
if (fs.existsSync(D('cities.js'))) fs.unlinkSync(D('cities.js'));
const kb = s => Math.round(zlib.gzipSync(s).length / 1024) + ' KB gzipped';
console.log('core.js', core.length, 'cities,', kb(coreJs));
console.log('rest.js', rest.length, 'cities,', kb(restJs));
