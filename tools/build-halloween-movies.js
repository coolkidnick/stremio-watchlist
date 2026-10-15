#!/usr/bin/env node
// Builds the two Halloween catalogs (static JSON) and patches addon/manifest.json. Does not touch other catalogs.
'use strict';
const fs = require('fs'), path = require('path');
const { series, movies } = {series:[],movies:require('./halloween-movies-data.js')};
const root = path.join(__dirname, '..');
const norm = s => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/^the /,'').replace(/[^a-z0-9]+/g,' ').trim();
const override = {
  "Rick and Morty":"Adult Swim. Sci-fi dark comedy with plenty of horror parody episodes. Adult humor.",
  "Ed, Edd n Eddy":"Cartoon Network. Has Halloween episodes. Silly and cozy.",
  "Adventure Time":"Cartoon Network. Has Halloween episodes. Whimsical and sometimes spooky.",
  "Futurama":"Has Halloween episodes. Funny sci-fi.",
  "Bob's Burgers":"Has Halloween episodes, including Full Bars. Cozy and funny.",
  "The Office":"Has Halloween episodes, including a Halloween costume contest in season 2. Cozy and funny.",
  "Gravity Falls":"Has the Summerween episode with the Summerween Trickster. Funny, cozy and mildly creepy.",
  "Rugrats":"Has Halloween episodes. Nostalgic and cozy.",
  "Parks and Recreation":"Has Halloween episodes, including Greg Pikitis and Halloween Surprise. Warm and funny.",
  "How I Met Your Mother":"Has Halloween episodes, including the Slutty Pumpkin story. Romantic comedy.",
  "Seinfeld":"Classic New York comedy. Has Halloween appearances. Cozy.",
  "Ugly Betty":"Has Halloween episodes. Fun and campy.",
  "Bones":"Has Halloween episodes. Procedural fun.",
  "Hemlock Grove":"Dark gothic series. Scary and gory.",
};
// Hand-verified ids added at Nick's request: [id, name, year, description]
const manualMovies = [
  ['tt0103874','Bram Stoker\'s Dracula',1992,'Lavish, gothic and romantic vampire horror. Scary-lite and campy in places. Date night yes.'],
  ['tt0110148','Interview with the Vampire',1994,'Gothic, lush and brooding vampire drama. Moody, not too gory. Date night yes.'],
  ['tt0114369','Se7en',1995,'Very dark, rainy city serial killer thriller. Grim and intense, not cozy. Date night only if you both like dark thrillers.'],
  ['tt0128801','Under Wraps',1997,'Disney Halloween TV movie about kids and a living mummy. Campy, cozy and silly. Date night yes for nostalgia.'],
];
const bad = d => /^(dup|placeholder)$/.test(d) || /Hocus Pocus-/.test(d) ;
const typeOk = { movie:['movie','tvMovie','video'], series:['tvSeries','tvMiniSeries'] };
const FIXED={"Hausu|1977":'tt0076162',"Bram Stoker's Dracula|1992":'tt0103874',"Interview with the Vampire|1994":'tt0110148',"Se7en|1995":'tt0114369'};
async function resolve(title, year, kind) {
  if (FIXED[title+'|'+year]) return {id:FIXED[title+'|'+year], name:title, y:year};
  const q = encodeURIComponent(title.toLowerCase().replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim());
  for (let t=0;t<3;t++) try {
    const r = await fetch(`https://v3.sg.media-imdb.com/suggestion/x/${q}.json`);
    const j = await r.json();
    for (const c of j.d||[]) {
      if (!/^tt\d+$/.test(c.id||'')) continue;
      if (!typeOk[kind].includes(c.qid)) continue;
      if (norm(c.l) !== norm(title)) continue;
      if (Math.abs((c.y||0) - year) > (kind==='series'?1:0)) continue;
      return { id: c.id, name: c.l, y: c.y };
    }
    return null;
  } catch(e) { await new Promise(r=>setTimeout(r,1000)); }
  return null;
}
async function build(list, kind, prefix) {
  const metas = [], dropped = [], seen = new Set();
  const items = list.filter(([t,y,d]) => !bad(d));
  for (const [t,y,d] of items) {
    const r = await resolve(t,y,kind);
    if (!r) { dropped.push(`${t} (${y})`); continue; }
    if (seen.has(r.id)) continue; seen.add(r.id);
    metas.push({ id:r.id, type:kind, name:r.name, poster:`https://images.metahub.space/poster/medium/${r.id}/img`, posterShape:'poster', description: override[t]||d, genres:['Halloween'], releaseInfo:String(r.y) });
  }
  return { metas, dropped };
}
(async () => {
  const m = await build(movies,'movie');
  m.metas.forEach(x=>x.genres=['Halloween']);
  const p1=path.join(root,'addon/catalog/movie/halloween-movies.json');
  fs.writeFileSync(p1,JSON.stringify({metas:m.metas})+'\n');
  const mp = path.join(root,'addon/manifest.json'); const man = JSON.parse(fs.readFileSync(mp,'utf8'));
  const d=new Date(); man.version='1.261015.'+(d.getHours()*60+d.getMinutes());
  fs.writeFileSync(mp, JSON.stringify(man,null,2)+'\n');
  console.log('count',m.metas.length); console.log('dropped:',m.dropped.join('; '));
})();
