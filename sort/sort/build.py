"""Rebuild songs.js from the Music League CSV export.
Usage: python build.py [path-to-export-folder]   (default ../2025-League)"""
import csv, json, collections, sys, pathlib

here = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent / '2025-League'
read = lambda n: list(csv.DictReader(open(src / n, encoding='utf-8')))

rounds = {r['ID']: r for r in read('rounds.csv')}
people = {r['ID']: r['Name'] for r in read('competitors.csv')}
points = collections.Counter()
for v in read('votes.csv'):
    points[(v['Spotify URI'], v['Round ID'])] += int(v['Points Assigned'] or 0)

order = {rid: i for i, rid in enumerate(sorted(rounds, key=lambda k: rounds[k]['Created']))}
subs = sorted(read('submissions.csv'), key=lambda s: (order[s['Round ID']], s['Created']))

rows = []
for i, s in enumerate(subs, 1):
    name = rounds[s['Round ID']]['Name']
    rows.append([i, name.split('.', 1)[1] if name.startswith('2025.') else name,
                 s['Title'], s['Artist(s)'], people.get(s['Submitter ID'], '?'),
                 points[(s['Spotify URI'], s['Round ID'])], s['Spotify URI'].split(':')[-1]])

(here / 'songs.js').write_text('const ROWS=' + json.dumps(rows, ensure_ascii=False) + ';\n', encoding='utf-8')
print(f'{len(rows)} songs, {len(rounds)} rounds -> songs.js')
