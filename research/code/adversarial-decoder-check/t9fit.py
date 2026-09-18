import json, glob, math, collections
rows = [json.loads(l) for f in sorted(glob.glob('log_*.jsonl')) for l in open(f)]
def key(r): return (r['fam'], json.dumps({k: v for k, v in sorted(r['kw'].items()) if k not in ('cap','gcap','graves')}), r['W'])
groups = collections.defaultdict(list)
for r in rows: groups[key(r)].append(r)
def fit(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    den = sum((x-mx)**2 for x in xs)
    if den == 0: return float('nan'), float('nan')
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/den
    return math.exp(my - b*mx), b
print(f"{'family':<14} {'kw':<28} {'W':>2} {'n':>3} {'capped':>6} | gen = A*(1/p*)^alpha {'alpha':>6} | gen = C*T^beta {'beta':>5} | max gen/(0.1 T^2 W^2) | max expF/D | worst T")
for k, rs in sorted(groups.items()):
    ok = [r for r in rs if not r['capped'] and r.get('p')]
    capped = sum(1 for r in rs if r['capped'])
    if len(ok) < 2: 
        print(f"{k[0]:<14} {k[1]:<28} {k[2]:>2} {len(rs):>3} {capped:>6} | (too few uncapped)"); continue
    xs = [math.log(1/r['p']) for r in ok]; ys = [math.log(r['gen']) for r in ok]
    A, a = fit(xs, ys); C, b = fit([math.log(r['T']) for r in ok], ys)
    ratio = max(r['gen']/(0.1*r['T']**2*r['W']**2) for r in ok); rr = max(ok, key=lambda r: r['gen']/(0.1*r['T']**2*r['W']**2))
    ed = max(r['exp_final']/max(r['D'],1) for r in ok)
    print(f"{k[0]:<14} {k[1]:<28} {k[2]:>2} {len(rs):>3} {capped:>6} | {A:9.3g} {a:>6.2f} | {C:9.3g} {b:>5.2f} | {ratio:8.1f} (T={rr['T']}) | {ed:6.1f} | T={max(r['T'] for r in ok)}")
print("\n--- per-family vs Graves at T in {16,32,64,128} (first-run instances, gcap=2e5 gens unless noted); gen counts, geometric mean over instances ---")
def gm(xs): return math.exp(sum(math.log(max(x,1)) for x in xs)/len(xs))
for k, rs in sorted(groups.items()):
    have = [r for r in rs if 'g_gen' in r]
    if not have: continue
    byT = collections.defaultdict(list)
    for r in have: byT[r['T']].append(r)
    line = []
    for T in sorted(byT):
        rr = byT[T]
        e = gm([r['gen'] for r in rr]); ec = sum(r['capped'] for r in rr)
        g = gm([r['g_gen'] for r in rr]); gc = sum(r['g_capped'] for r in rr)
        law = 0.1*T*T*k[2]**2
        line.append(f"T={T}: exactbwd {e:.3g}{'(CAP)' if ec else ''} [{e/law:.1f}x law] vs Graves {g:.3g}{'(CAP)' if gc else ''}")
    print(f"{k[0]:<14} {k[1]:<26} W={k[2]}: " + " | ".join(line))
