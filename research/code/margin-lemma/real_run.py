"""Plain (non-certifying) final search on real wav2vec2 posteriors (T=112, W=32: P14 at clean/10dB/5dB/0dB), with the
R1 diagnostics: K (distinct suffix modes per symbol, a priori), n_off, max K_u / R(u) on off-path expanded nodes, and
the exact margin by the second-best search. Float pipeline (the real tables are float); p* cross-checked with ctc_forward."""
import sys, os, time, numpy as np
sys.dont_write_bytecode = True
from r1core import *
TK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder')
sys.path.insert(0, TK)
from ctc import ctc_forward
S = '/path/to/decoder-push'  # directory holding T4/posteriors_*.npz (not redistributed)
names = sys.argv[1:] if len(sys.argv) > 1 else ['clean/P14', '10dB/P14', '5dB/P14', '0dB/P14']
for nm in names:
    tag, key = nm.split('/')
    z = np.load(f'{S}/T4/posteriors_{tag}.npz'); P = np.asarray(z[key], dtype=np.float64)
    tbl = P.tolist(); T, W = P.shape
    t0 = time.time()
    r = analyse(tbl, W, want_p2=True, want_diag=True)
    sec = time.time() - t0
    pf = ctc_forward(list(r['mode']), tbl)
    offs = [x for x in r['recs'] if not x['onpath']]
    print(f"T4/{nm}: T={T} W={W} D={r['D']} p*={r['p']:.4g} (ctc_forward {pf:.4g}) p2={r['p2']:.4g} margin={r['margin']:.4g} "
          f"exp_final={r['exp_final']} n_off={r['n_off']} K={r['K']} Kd(max symbol)={max(r['Kd'][1:])} "
          f"maxK_off={r['maxK_off']} maxR_off={r['maxR_off']:.3f} maxKeff_off={r['maxKeff_off']:.2f} gen={r['gen']} exp2={r['exp2']} sec={sec:.0f}", flush=True)
    print(f"   Kd per symbol: {r['Kd'][1:]}")
    for x in offs[:8]:
        print(f"   off-path u=len{len(x['u'])} last={x['u'][-3:]} B/p*={x['B']/r['p']:.4f} K_u={x['K']} support={x['support']} R={x['Sd']/x['maxc']:.3f} maxc/p*={x['maxc']/r['p']:.4f}")
