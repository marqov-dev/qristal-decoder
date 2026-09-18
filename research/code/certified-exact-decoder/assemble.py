"""Assemble section (f) from real_*.jsonl: per-row table, per-domain summary, worst wall-clock, cut-offs, beam-6400 creep resolution."""
import json, glob, os, math
S = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(S, 'real_*.jsonl'))) for l in open(f)]
_seen = set(); rows = [r for r in rows if not (r['name'] in _seen or _seen.add(r['name']))]
def dom(n):
    if n.startswith('T4/'): return 'LibriSpeech ' + n.split('/')[1]
    b = n[3:]
    if 'atc_uwb' in b: return 'UWB-ATCC (' + b.split('__')[0] + ')'
    if 'ami_sdm' in b: return 'AMI-SDM'
    if 'torgo_ctl' in b: return 'TORGO control'
    if 'torgo_dys' in b: return 'TORGO dysarthric (' + b.split('__')[0] + ')'
    return '?'
order = ['LibriSpeech clean', 'LibriSpeech 10dB', 'LibriSpeech 5dB', 'LibriSpeech 0dB', 'UWB-ATCC (base960h)', 'UWB-ATCC (torgoft)', 'AMI-SDM', 'TORGO dysarthric (base960h_dys)', 'TORGO dysarthric (torgoft)', 'TORGO control']
rows.sort(key=lambda r: (order.index(dom(r['name'])) if dom(r['name']) in order else 99, r['name']))
def ratio(r, k): return (r[k]['p'] / r['p1']) if r['p1'] > 0 else float('nan')
print("| table | T | D | status | sec | gen | final exp | p* (certified) | p₂ (certified) | margin | greedy/p* | beam-5/p* | beam-50/p* | beam-800/p* |")
print("|---|--:|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for r in rows:
    m = r['p1'] / r['p2'] if r['p2'] > 0 else float('inf')
    nm = r['name'].replace('T7/', '').replace('base960h__', '').replace('uwb-atcc_', '').replace('AMI_EN2002a_sdm_', '')
    print(f"| {nm} | {r['T']} | {r['D']} | {r['status']} | {r['sec']:.1f} | {r['gen']:.2e} | {r['exp_final']} | {r['p1']:.3e} | {r['p2']:.3e} | {m:.3f} | {ratio(r,'greedy'):.3f} | {ratio(r,'beam5'):.3f} | {ratio(r,'beam50'):.3f} | {ratio(r,'beam800'):.3f} |")
print("\n**Per-domain summary** (n, median T, median certified p*, p* range, median margin, decoder = mode counts, greedy-worst p/p*, beam-800-worst p/p*, worst sec):\n")
print("| domain | n | T med | p* med | p* range | margin med | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | worst greedy/p* | worst beam-800/p* | worst sec | cut-offs |")
print("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
import statistics as st
for d in order:
    rs = [r for r in rows if dom(r['name']) == d]
    if not rs: continue
    ok = [r for r in rs if r['status'] == 'ok']
    eq = lambda k: sum(1 for r in ok if abs(ratio(r, k) - 1) <= 1e-9)
    ps = [r['p1'] for r in ok]; ms = [r['p1']/r['p2'] for r in ok if r['p2'] > 0]
    print(f"| {d} | {len(rs)} | {st.median([r['T'] for r in rs]):.0f} | {st.median(ps):.2e} | {min(ps):.1e}–{max(ps):.1e} | {st.median(ms):.3f} | {eq('greedy')}/{len(ok)} | {eq('beam5')}/{len(ok)} | {eq('beam50')}/{len(ok)} | {eq('beam800')}/{len(ok)} | {min(ratio(r,'greedy') for r in ok):.3f} | {min(ratio(r,'beam800') for r in ok):.3f} | {max(r['sec'] for r in rs):.0f} | {len(rs)-len(ok)} |")
worst = max(rows, key=lambda r: r['sec'])
print(f"\nWorst wall-clock: {worst['name']} T={worst['T']} {worst['sec']:.0f} s (status {worst['status']}); cut-offs: {[r['name'] for r in rows if r['status'] != 'ok']}; rows: {len(rows)}")
print(f"gen/(T^2 W^2) over ok rows: min {min(r['gen']/(r['T']**2*r['W']**2) for r in rows if r['status']=='ok'):.3f} max {max(r['gen']/(r['T']**2*r['W']**2) for r in rows if r['status']=='ok'):.3f}")
# creep resolution
conv = json.load(open(os.path.join(S, 'T7', 'convergence.json')))
print("\n**Beam-6400 creep resolution:**\n")
print("| T7 table | beam-800 p1 | beam-6400 p1 | certified p* | 6400/p* | certified mode == beam-6400 D? |")
print("|---|--:|--:|--:|--:|--:|")
for k, v in conv.items():
    name = 'T7/' + os.path.basename(k)[:-4]
    r = next((r for r in rows if r['name'] == name), None)
    b800 = next((e for e in v if e['beam'] == 800), None); b64 = v[-1]
    if r and r['status'] == 'ok':
        print(f"| {os.path.basename(k)[:-4]} | {b800['p1'] if b800 else float('nan'):.4e} | {b64['p1']:.4e} (beam {b64['beam']}) | {r['p1']:.4e} | {b64['p1']/r['p1']:.4f} | D_cert={r['D']} vs D_6400={b64['D']}; p(beam-800 labelling)/p* = {ratio(r,'beam800'):.4f} |")
    else:
        print(f"| {os.path.basename(k)[:-4]} | | {b64['p1']:.4e} | {'not yet / ' + (r['status'] if r else 'pending')} | | |")
