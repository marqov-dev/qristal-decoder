"""Scaling-law fits: log(exp) = a + b*log(1/p*) per decoder over all uncapped cells of the given JSONs."""
import json, math, sys, os
here = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sys.argv[1:]:
    rows += json.load(open(os.path.join(here, f)))
decs = sorted({r['dec'] for r in rows}, key=lambda d: ['graves','childF','graves+beam','dfsBB+beam','bidir','policy','exactbwd'].index(d))
def fit(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs)
    a = my - b*mx
    ss = sum((y-my)**2 for y in ys); sr = sum((y-(a+b*x))**2 for x, y in zip(xs, ys))
    return a, b, 1 - sr/ss if ss else 1.0
print(f"{'decoder':<12} {'cells':>5} {'exp = A*(1/p*)^b':>22} {'R^2':>6} | {'gen = A*(1/p*)^b':>22} {'R^2':>6}  (cells with 1/p* >= 30, uncapped)")
for d in decs:
    rs = [r for r in rows if r['dec'] == d and r['caps'] == 0 and 1/r['pstar'] >= 30]
    if len(rs) < 3: continue
    xs = [math.log(1/r['pstar']) for r in rs]
    a, b, r2 = fit(xs, [math.log(r['exp']) for r in rs]); a2, b2, r22 = fit(xs, [math.log(r['gen']) for r in rs])
    print(f"{d:<12} {len(rs):>5} {math.exp(a):>10.2f} * (1/p*)^{b:.3f} {r2:>6.3f} | {math.exp(a2):>10.2f} * (1/p*)^{b2:.3f} {r22:>6.3f}")
print("\nexp vs D (depth of the mode) for the two tightest decoders:")
for d in ('policy', 'exactbwd'):
    rs = [r for r in rows if r['dec'] == d and r['caps'] == 0]
    print(f"  {d:<9} exp/D over cells: " + " ".join(f"{r['exp']/r['D']:.1f}" for r in rs))
