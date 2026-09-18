"""Real posteriors: certified margin p1/p2 vs final-search expansions/D, from T2b/real_*.jsonl (C decoder, certified runner-up).
Read-only. Reports the joint distribution and the cells that violate 'exp_final <= D+1'."""
import json, glob, os
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder')
rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(S, 'real_*.jsonl'))) for l in open(f)]
rows = [r for r in rows if r.get('status') == 'ok']
print(f"{len(rows)} real tables (status ok)")
print(f"{'name':28s} {'T':>4s} {'D':>3s} {'margin':>10s} {'exp_final':>9s} {'exp/D':>6s} {'exp-(D+1)':>9s} {'gen/T2W2':>8s}")
bins = {}
for r in sorted(rows, key=lambda r: r['p1'] / r['p2'] if r['p2'] else float('inf')):
    m = r['p1'] / r['p2'] if r['p2'] else float('inf'); D = r['D']; e = r['exp_final']
    print(f"{r['name']:28s} {r['T']:4d} {D:3d} {m:10.4g} {e:9d} {e/max(D,1):6.2f} {e-(D+1):9d} {r['gen']/(r['T']**2*r['W']**2):8.3f}")
    key = ('<1.01' if m < 1.01 else '<1.1' if m < 1.1 else '<1.3' if m < 1.3 else '<2' if m < 2 else '<10' if m < 10 else '>=10')
    bins.setdefault(key, []).append((e / max(D, 1), e - (D + 1), D))
print()
for key in ('<1.01', '<1.1', '<1.3', '<2', '<10', '>=10'):
    if key in bins:
        v = bins[key]
        print(f"margin {key:6s}: n={len(v):2d}  exp/D: min {min(x[0] for x in v):.2f} median {sorted(x[0] for x in v)[len(v)//2]:.2f} max {max(x[0] for x in v):.2f}"
              f"  #tables with off-path expansions (exp_final > D+1): {sum(1 for x in v if x[1] > 0)}")
