"""Run variant 1c (C port) on every real posterior table; compare with greedy / beam-k from the toolkit.
Usage: real.py <shard> <nshards> -> real_<shard>.jsonl"""
import sys, os, json, glob, time, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctc import ctc_forward, collapse, topk_labellings
from cdecoder import decode_c
S = '/path/to/decoder-push'  # directory holding T4/posteriors_*.npz and T7/posteriors/*.npy (not redistributed)
tables = []
for tag in ('clean', '10dB', '5dB', '0dB'):
    z = np.load(f'{S}/T4/posteriors_{tag}.npz')
    for k in z.keys():
        if k.startswith('P'): tables.append((f'T4/{tag}/{k}', z[k]))
for f in sorted(glob.glob(f'{S}/T7/posteriors/*.npy')):
    tables.append(('T7/' + os.path.basename(f)[:-4], np.load(f)))
shard, nsh = int(sys.argv[1]), int(sys.argv[2])
out = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'real_{shard}.jsonl'), 'w')
for i, (name, P) in enumerate(tables):
    if i % nsh != shard: continue
    P = np.asarray(P, dtype=np.float64); T, W = P.shape
    assert abs(P.sum(1) - 1).max() < 1e-6
    tb = P.tolist()
    r = decode_c(P, time_limit=600.0)
    row = dict(name=name, T=T, W=W, status=r['status'], sec=r['sec'], gen=r['gen'], exp_final=r['exp_final'], exp_bwd=r['exp_bwd'],
               p1=r['p1'], p2=r['p2'], D=len(r['l1']), l1=list(r['l1']), l2=list(r['l2']),
               conf_mean=float(P.max(1).mean()), blank_frac=float((P.argmax(1) == 0).mean()))
    if r['status'] == 'ok':
        row['p1_check'] = ctc_forward(r['l1'], tb); row['p2_check'] = ctc_forward(r['l2'], tb) if r['l2'] else 0.0
    lg = collapse(tuple(int(x) for x in P.argmax(1))); row['greedy'] = dict(l=list(lg), p=ctc_forward(lg, tb), D=len(lg))
    for b in (5, 50, 800):
        t0 = time.perf_counter(); top = topk_labellings(tb, beam=b, k=2); dt = time.perf_counter() - t0
        lb = top[0][1]; row[f'beam{b}'] = dict(l=list(lb), p=ctc_forward(lb, tb), beam_score=top[0][0], D=len(lb), sec=dt)
    out.write(json.dumps(row) + '\n'); out.flush()
    print(f"{name:<75} T={T:>3} status={row['status']:<8} sec={row['sec']:>7.1f} gen={row['gen']:>9} expF={row['exp_final']:>4} D={row['D']:>3} p*={row['p1']:.3e} p2={row['p2']:.3e} greedy/p*={row['greedy']['p']/row['p1'] if row['p1'] else float('nan'):.3f} b5={row['beam5']['p']/row['p1'] if row['p1'] else 0:.3f} b50={row['beam50']['p']/row['p1'] if row['p1'] else 0:.3f} b800={row['beam800']['p']/row['p1'] if row['p1'] else 0:.3f}", flush=True)
