"""Rebuild playlist.csv (checker) and sort/songs.js (sorter) from the Music League CSV export.
Usage: python build.py [path-to-export-folder]   (default ../Rule-Britannia-League)"""
import csv, json, collections, sys, pathlib

here = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent / 'Rule-Britannia-League'
read = lambda n: list(csv.DictReader(open(src / n, encoding='utf-8')))

rounds = {r['ID']: r for r in read('rounds.csv')}
people = {r['ID']: r['Name'].strip() for r in read('competitors.csv')}
points = collections.Counter()
for v in read('votes.csv'):
    points[(v['Spotify URI'], v['Round ID'])] += int(v['Points Assigned'] or 0)

order = {rid: i for i, rid in enumerate(sorted(rounds, key=lambda k: rounds[k]['Created']))}
subs = sorted(read('submissions.csv'), key=lambda s: (order[s['Round ID']], s['Created']))

rows = []
for i, s in enumerate(subs, 1):
    name = '%02d %s' % (order[s['Round ID']] + 1, rounds[s['Round ID']]['Name'])
    rows.append([i, name, s['Title'], s['Artist(s)'], people.get(s['Submitter ID'], '?'),
                 points[(s['Spotify URI'], s['Round ID'])], s['Spotify URI'].split(':')[-1]])

(here / 'sort' / 'songs.js').write_text('const ROWS=' + json.dumps(rows, ensure_ascii=False) + ';\n', encoding='utf-8')

# Same column names as an Exportify playlist export, so either source drops in.
with open(here / 'playlist.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(['Track name', 'Artist name', 'Album', 'Playlist name', 'Type', 'ISRC', 'Spotify - id'])
    for s in subs:
        w.writerow([s['Title'], s['Artist(s)'], s['Album'], 'Rule Britannia', 'Playlist', '', s['Spotify URI'].split(':')[-1]])

print(f'{len(rows)} songs, {len(rounds)} rounds -> sort/songs.js + playlist.csv')
