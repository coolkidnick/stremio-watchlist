#!/usr/bin/env node
/*
 * build-addon.js: build the static Stremio add-on (addon/manifest.json + catalog JSON files)
 * using exactly the same engine as index.html (it loads the <script id="app-core"> block).
 *
 * Usage:
 *   node build-addon.js [export.json] [--out addon] [--limit 100] [--seen library.json|library.txt ...] [--version 1.2.3]
 *
 *   export.json  a Picture House export (Settings > Backup or "Export data for build-addon.js").
 *                Omit it to build from the default state (taste profile + 20 starter picks).
 *   --seen FILE  extra titles to treat as seen: a plain title list or Stremio library JSON.
 *                Only used for filtering; nothing from it is written to the add-on.
 */
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');

function loadCore(htmlPath) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const m = html.match(/<script id="app-core">([\s\S]*?)<\/script>/);
  if (!m) throw new Error('Could not find <script id="app-core"> in ' + htmlPath);
  const sandbox = { console };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(m[1], sandbox, { filename: 'app-core.js' });
  return sandbox.PictureHouse;
}

function main(argv) {
  const args = { seen: [], out: path.join(__dirname, 'addon'), limit: 100, input: null, version: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') args.out = path.resolve(argv[++i]);
    else if (a === '--limit') args.limit = parseInt(argv[++i], 10);
    else if (a === '--seen') args.seen.push(argv[++i]);
    else if (a === '--version') args.version = argv[++i];
    else if (a === '-h' || a === '--help') { console.log(fs.readFileSync(__filename, 'utf8').split('*/')[0]); return; }
    else args.input = a;
  }
  const C = loadCore(path.join(__dirname, 'index.html'));
  let state;
  if (args.input) state = C.importData(JSON.parse(fs.readFileSync(args.input, 'utf8')));
  else state = C.initialState();
  const exclude = [];
  for (const f of args.seen) {
    const parsed = C.parseLibrary(fs.readFileSync(f, 'utf8'));
    exclude.push(...parsed.items);
    console.log(`--seen ${path.basename(f)}: ${parsed.items.length} titles (used for filtering only)`);
  }
  const d = new Date();
  const version = args.version || `1.${d.getUTCFullYear() % 100}${String(d.getUTCMonth() + 1).padStart(2, '0')}${String(d.getUTCDate()).padStart(2, '0')}.${d.getUTCHours() * 60 + d.getUTCMinutes()}`;
  const { files, counts } = C.buildAddon(state, { limit: args.limit, version, excludeItems: exclude });
  // clean previous catalog output
  fs.rmSync(path.join(args.out, 'catalog'), { recursive: true, force: true });
  for (const [rel, obj] of Object.entries(files)) {
    const p = path.join(args.out, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, JSON.stringify(obj, null, rel === 'manifest.json' ? 2 : 0) + '\n');
  }
  console.log(`Wrote ${Object.keys(files).length} files to ${args.out} (manifest v${version})`);
  console.log(Object.entries(counts).map(([k, v]) => `  ${k}: ${v}`).join('\n'));
  return { files, counts };
}

if (require.main === module) main(process.argv.slice(2));
module.exports = { loadCore, main };
