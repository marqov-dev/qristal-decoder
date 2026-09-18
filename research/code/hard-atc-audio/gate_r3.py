"""Gate: certctc pure-Python backend vs C backend on the two smallest (by T) R3 posterior tables among the clips new in R3
(A4 clips were gated in A4 with T2b/bounds.py). Identical p*, identical mode, identical generation count required."""
import sys, os, glob, json, time, numpy as np
R3 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, R3)
sys.path.insert(0, os.path.join(R3, '..', '..'))  # certctc package
from certctc import decode, verify
man = json.load(open('manifest.json')); new = [m for m in man if m['domain'] not in ('atc_uwb', 'atc_atco2')]
paths = [f"posteriors/r3__{m['domain']}__{m['id']}.npy" for m in new]
while not all(os.path.exists(p) for p in paths): time.sleep(20)
tabs = sorted(((np.load(p).shape[0], p) for p in paths))[:2]
for T, p in tabs:
    P = np.load(p)
    c = decode(P, blank=28, backend='c'); y = decode(P, blank=28, backend='python')
    ok = (c.p_mode == y.p_mode) and (c.mode == y.mode) and (c.p_runner_up == y.p_runner_up) and (c.generations_total == y.generations_total) and verify(P, y).ok
    print(f"GATE python vs C on {os.path.basename(p)[:-4]} T={T} W=31 blank=28: python p*={y.p_mode:.6e} p2={y.p_runner_up:.6e} exp={y.expansions_final} gen={y.generations_total} sec={y.wall_seconds:.1f} | C p*={c.p_mode:.6e} p2={c.p_runner_up:.6e} exp={c.expansions_final} gen={c.generations_total} sec={c.wall_seconds:.2f} -> {'PASS' if ok else 'FAIL'}", flush=True)
