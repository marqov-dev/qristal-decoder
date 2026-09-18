"""End-to-end gate: stdlib exact-backward on the two smallest real tables vs the C port."""
import sys, os, glob, numpy as np, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
from cdecoder import decode_c
S = '/path/to/decoder-push'  # directory holding T4/posteriors_*.npz and T7/posteriors/*.npy (not redistributed)
tables = []
for tag in ('clean', '10dB', '5dB', '0dB'):
    z = np.load(f'{S}/T4/posteriors_{tag}.npz')
    for k in z.keys():
        if k.startswith('P'): tables.append((f'T4/{tag}/{k}', z[k]))
for f in sorted(glob.glob(f'{S}/T7/posteriors/*.npy')): tables.append(('T7/' + os.path.basename(f)[:-4], np.load(f)))
tables.sort(key=lambda x: x[1].shape[0])
for name, P in tables[:2]:
    tb = P.astype(np.float64).tolist(); T, W = P.shape
    rc = decode_c(P)
    cnt = Counter(); t0 = time.perf_counter(); rp = decode_exact_backward(tb, cap=10**7, cnt=cnt); dt = time.perf_counter() - t0
    ok = (not rp[4]) and abs(rp[0] - rc['p1']) <= 1e-12 * rc['p1'] and rp[1] == rc['l1']
    print(f"GATE stdlib vs C on real table {name} T={T} W={W}: stdlib p*={rp[0]:.6e} exp={rp[2]} gen={cnt.gen} sec={dt:.0f} | C p*={rc['p1']:.6e} exp={rc['exp_final']} gen={rc['gen']} sec={rc['sec']:.1f} -> {'PASS' if ok else 'FAIL'}", flush=True)
