"""R3: fetch every ATCO2-test-1h clip that satisfies the A4/T7 selection rule (3-8 s, >=5 words), excluding the 8 already run in A4.
Row metadata from the datasets-server /rows API (9 pages, rows/atco2_test_*.json)."""
import json, glob, os, subprocess, time, sys
rows = []
for f in sorted(glob.glob('rows/atco2_test_*.json'), key=lambda s: int(s.split('_')[-1][:-5])):
    rows += [r['row'] for r in json.load(open(f))['rows']]
assert len(rows) == 871
a4 = {m['id'] for m in json.load(open('../A4/manifest.json')) if m['domain'] == 'atc_atco2'}
cand = [r for r in rows if 3.0 <= r['duration'] <= 8.0 and len(r['text'].split()) >= 5 and r['id'] not in a4]
print('rows', len(rows), 'candidates', len(cand), 'excluded A4', len(a4), flush=True)
os.makedirs('samples/atco2_all', exist_ok=True)
man = []; tot = 0
for i, r in enumerate(cand):
    out = f"samples/atco2_all/{r['id']}.wav"
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        for attempt in range(3):
            p = subprocess.run(['curl', '-s', '-L', '-o', out, r['audio'][0]['src']])
            if p.returncode == 0 and os.path.getsize(out) > 1000: break
            time.sleep(2)
    b = os.path.getsize(out); tot += b
    man.append(dict(id=r['id'], text=r['text'], dur=r['duration'], path=out, bytes=b))
    if i % 50 == 0: print(i, out, b, f'{tot/1e6:.1f} MB', flush=True)
json.dump(man, open('atco2_candidates.json', 'w'), indent=1)
print('DONE', len(man), f'{tot/1e6:.1f} MB')
