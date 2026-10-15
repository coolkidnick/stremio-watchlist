#!/usr/bin/env python3
"""Rebuilds the Halloween Specials and TV catalog as per-show Halloween-episode metas.
Episode picks are hand curated below and each is verified live against Cinemeta (season/episode must exist).
Writes addon/catalog/series/halloween-specials-tv.json, addon/meta/series/nph-<tt>.json and patches addon/manifest.json."""
import json, os, re, sys, unicodedata, urllib.request, datetime
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ALL = 'ALL'
# imdb id: (display name, [(season, episode)] or ALL, note)
PICKS = {
 'tt0096697': ('The Simpsons', [(2,3),(3,7),(4,5),(5,5),(6,6),(7,6),(8,1),(9,4),(10,4),(11,4),(12,1),(13,1),(14,1),(15,1),(16,1),(17,4),(18,4),(19,5),(20,4),(21,4),(22,4),(23,3),(24,2),(25,2),(26,4),(27,4),(27,5),(28,4),(29,4),(30,4),(31,4),(32,4),(33,3),(34,6),(35,5),(36,5),(36,7),(37,3),(38,3),(38,4)], 'Every Treehouse of Horror and Halloween special.'),
 'tt0306274': ('What\'s New, Scooby-Doo?', [(2,14)], ''),
 'tt0292800': ('The Grim Adventures of Billy & Mandy', [(2,26)], ''),
 'tt1865718': ('Gravity Falls', [(1,12)], ''),
 'tt1710308': ('Regular Show', [(3,4),(4,3),(5,8),(6,4),(7,9),(8,19)], 'The Terror Tales of the Park Halloween anthologies.'),
 'tt0115157': ("Dexter's Laboratory", [(2,81)], ''),
 'tt0175058': ('The Powerpuff Girls', [(1,9)], ''),
 'tt0118289': ('Cow and Chicken', [(2,4)], ''),
 'tt0419315': ('Camp Lazlo', [(2,1)], ''),
 'tt4839610': ('We Bare Bears', [(3,32),(4,18)], ''),
 'tt7713450': ('Craig of the Creek', [(3,10)], ''),
 'tt1942683': ('The Amazing World of Gumball', [(2,9),(6,25)], ''),
 'tt2771780': ('Teen Titans Go!', [(2,19),(4,2),(5,8),(5,52),(6,27),(7,25),(8,1),(9,24)], ''),
 'tt0297494': ('Aqua Teen Hunger Force', [(2,15)], ''),
 'tt0437745': ('Robot Chicken', [(11,13)], ''),
 'tt0457146': ('Squidbillies', [(2,7)], ''),
 'tt2467372': ("Brooklyn Nine-Nine", [(1,6),(2,4),(3,5),(4,5),(5,4),(6,16)], 'The annual Halloween Heist episodes.'),
 'tt1439629': ('Community', [(2,6),(4,2)], ''),
 'tt1561755': ("Bob's Burgers", [(3,2),(4,2),(6,3),(7,3),(8,3),(9,4),(11,4),(12,3),(13,6),(16,3)], ''),
 'tt0182576': ('Family Guy', [(9,4)], ''),
 'tt0121955': ('South Park', [(1,7),(3,10),(10,11),(16,12),(21,6),(22,5),(23,5)], ''),
 'tt0118276': ('Buffy the Vampire Slayer', [(2,6)], ''),
 'tt0108778': ('Friends', [(8,6)], ''),
 'tt0386676': ('The Office', [(2,5),(5,5),(7,6),(8,5),(9,5)], ''),
 'tt1442437': ('Modern Family', [(2,6),(4,5),(6,6),(8,5),(9,5),(10,5),(11,5)], ''),
 'tt1266020': ('Parks and Recreation', [(2,7),(4,5),(5,5)], ''),
 'tt1587678': ('Happy Endings', [(2,5)], ''),
 'tt1826940': ('New Girl', [(2,6),(3,6)], ''),
 'tt0460649': ('How I Met Your Mother', [(1,6),(7,8)], 'The Slutty Pumpkin story.'),
 'tt0106004': ('Frasier', [(5,3)], ''),
 'tt0094540': ('Roseanne', [(2,7),(3,7),(5,7),(6,6),(8,5)], 'Roseanne was famous for its Halloween episodes.'),
 'tt0165598': ("That '70s Show", [(2,5),(3,4)], ''),
 'tt14218830': ('Abbott Elementary', [(2,6),(4,4),(5,5),(6,4)], ''),
 'tt4477976': ('Superstore', [(2,6),(3,5),(4,4),(5,6)], ''),
 'tt3487356': ('Black-ish', [(1,6),(2,6),(3,5),(5,3),(6,6)], ''),
 'tt4574334': ('Stranger Things', [(2,1),(2,2)], 'Season 2 opens on Halloween.'),
 'tt6763664': ('The Haunting of Hill House', [(1,8)], 'Halloween night.'),
 'tt0115341': ('Sabrina the Teenage Witch', [(1,5),(5,6),(6,4)], ''),
 'tt0111987': ('Goosebumps', [(1,1),(1,2),(2,10)], ''),
 'tt1844624': ('American Horror Story', [(1,4),(1,5),(4,3),(5,5)], ''),
 'tt11379026': ('Ghosts', [(1,5),(2,5),(3,4),(4,3),(5,3),(6,1),(6,2)], 'The annual Halloween episodes.'),
 'tt0057729': ('The Addams Family', [(1,7),(2,7)], ''),
 'tt0057733': ('Bewitched', [(2,7),(4,8),(6,7)], ''),
 'tt0115200': ('Hey Arnold!', [(2,11)], ''),
 'tt0206512': ('SpongeBob SquarePants', [(1,26)], ''),
 'tt0106115': ("Rocko's Modern Life", [(3,5)], ''),
 'tt0235923': ('Invader ZIM', [(1,22)], ''),
 'tt0105950': ('Beavis and Butt-Head', [(6,1)], ''),
 'tt5227038': ('Halloween Baking Championship', ALL, 'The whole show is Halloween themed.'),
 'tt6874206': ('Making It', [(1,4),(3,4)], ''),
 'tt0805669': ('Ugly Betty', [(1,5)], ''),
 'tt0460681': ('Supernatural', [(4,7)], ''),
 'tt3718778': ('Over the Garden Wall', ALL, 'The whole ten part autumn miniseries.'),
}
def ascii(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s).strip()
def fetch(tt):
    for _ in range(3):
        try:
            return json.load(urllib.request.urlopen(f'https://v3-cinemeta.strem.io/meta/series/{tt}.json', timeout=30))['meta']
        except Exception: pass
    return None
cat, dropped, total = [], [], 0
for tt, (name, picks, note) in PICKS.items():
    m = fetch(tt)
    if not m: dropped.append(f'{name} (no Cinemeta data)'); continue
    idx = {(v['season'], v['episode'] if 'episode' in v else v['number']): v for v in m.get('videos', []) if v.get('season')}
    keys = sorted(idx) if picks == ALL else picks
    vids = []
    for k in keys:
        v = idx.get(k)
        if not v: dropped.append(f'{name} S{k[0]}E{k[1]} (not in Cinemeta)'); continue
        t = ascii(v.get('name') or v.get('title') or f'Episode {k[1]}')
        vid = {'id': f'{tt}:{k[0]}:{k[1]}', 'title': t, 'name': t, 'season': k[0], 'episode': k[1], 'number': k[1]}
        if v.get('released'): vid['released'] = v['released']
        o = ascii(v.get('overview') or v.get('description') or '')
        if o: vid['overview'] = o[:400]
        if v.get('thumbnail'): vid['thumbnail'] = v['thumbnail']
        vids.append(vid)
    if not vids: dropped.append(f'{name} (no verified episodes)'); continue
    nid = 'nph-' + tt
    title = f'{name}: Halloween Episodes'
    desc = ascii(f'{len(vids)} Halloween episode{"s" if len(vids)!=1 else ""} of {name}. {note}')
    meta = {'id': nid, 'type': 'series', 'name': title, 'poster': f'https://images.metahub.space/poster/medium/{tt}/img',
            'posterShape': 'poster', 'background': f'https://images.metahub.space/background/medium/{tt}/img',
            'description': desc, 'genres': ['Halloween'], 'releaseInfo': ascii(str(m.get('releaseInfo') or m.get('year') or '')),
            'videos': vids, 'behaviorHints': {'defaultVideoId': vids[0]['id']}}
    os.makedirs(f'{ROOT}/addon/meta/series', exist_ok=True)
    json.dump({'meta': meta}, open(f'{ROOT}/addon/meta/series/{nid}.json', 'w'), separators=(',', ':')); 
    cat.append({k: meta[k] for k in ('id','type','name','poster','posterShape','description','genres','releaseInfo')})
    total += len(vids)
json.dump({'metas': cat}, open(f'{ROOT}/addon/catalog/series/halloween-specials-tv.json', 'w'), separators=(',', ':'))
mp = f'{ROOT}/addon/manifest.json'; man = json.load(open(mp))
man['resources'] = ['catalog', {'name': 'meta', 'types': ['series'], 'idPrefixes': ['nph-']}]
now = datetime.datetime.now(); man['version'] = f'1.261015.{now.hour*60+now.minute}'
json.dump(man, open(mp, 'w'), indent=2); open(mp, 'a').write('\n')
print('shows', len(cat), 'episodes', total); print('dropped/unverified:', dropped)
