"""Scan 1: TRUE margin (exact second-best search) vs T for A2's pinned family and the two-rate family.
Float pipeline for speed; gate: float margin/exp_final agree with the Fraction pipeline at T<=24.
Columns: T D margin exp_final exp/D gen gen/T^2 K maxK_off maxR_off maxKeff_off n_off"""
import sys, time
from fractions import Fraction
from r1core import *

fams = []
for W, rho in ((4, Fraction(1, 2)), (5, Fraction(3, 5)), (3, Fraction(1, 2))):
    for delta in (Fraction(1), Fraction(3), Fraction(10)):
        fams.append((f"pinned W={W} rho={float(rho)} delta={float(delta)}", W, lambda T, W=W, rho=rho, delta=delta: fam_pinned(T, W, rho, delta)))
for W, rho, a, b in ((3, Fraction(1, 2), Fraction(1, 4), Fraction(1, 16)), (4, Fraction(1, 2), Fraction(1, 4), Fraction(1, 16)),
                     (4, Fraction(3, 5), Fraction(3, 10), Fraction(3, 40))):
    fams.append((f"tworate W={W} rho={float(rho)} a={float(a)} b={float(b)} c=b/8", W, lambda T, W=W, rho=rho, a=a, b=b: fam_tworate(T, W, rho, a, b, b / 8)))

Ts = (10, 14, 18, 24, 32, 40, 48, 56, 64, 80)
gate_viol = 0; gate_n = 0
for name, W, mk in fams:
    print(f"## {name}")
    for T in Ts:
        tbl = mk(T); ftbl = to_float(tbl)
        t0 = time.time()
        r = analyse(ftbl, W, cap=2_000_000, cap2=2_000_000)
        sec = time.time() - t0
        if r['capped']: print(f"  T={T} CAPPED gen={r.get('gen')}"); break
        if r['p2'] is None: print(f"  T={T} second-best CAPPED"); break
        note = ''
        if T <= 24:
            re = analyse(tbl, W)
            gate_n += 1
            ok = (re['mode'] == r['mode'] and re['exp_final'] == r['exp_final'] and abs(float(re['margin']) - r['margin']) <= 1e-9 * r['margin']
                  and re['n_off'] == r['n_off'])
            if not ok: gate_viol += 1
            note = f" exact:{'ok' if ok else 'MISMATCH(exp %d vs %d, m %.6g vs %.6g)' % (re['exp_final'], r['exp_final'], float(re['margin']), r['margin'])}"
        D = r['D']
        print(f"  T={T:3d} D={D:2d} margin={r['margin']:.4f} exp_final={r['exp_final']:5d} exp/D={r['exp_final']/max(D,1):.2f} "
              f"gen={r['gen']:7d} gen/T2={r['gen']/T**2:.2f} K={r['K']} maxK_off={r['maxK_off']} maxR_off={r['maxR_off']:.3f} "
              f"maxKeff_off={r['maxKeff_off']:.2f} n_off={r['n_off']} l2={''.join(map(str,r['l2']))} sec={sec:.1f}{note}", flush=True)
        if sec > 300: break
print(f"GATE S1 float pipeline == Fraction pipeline (mode, exp_final, n_off, margin to 1e-9) at T<=24: {gate_n} cells, violations {gate_viol} -> {'PASS' if gate_viol == 0 else 'FAIL'}")
