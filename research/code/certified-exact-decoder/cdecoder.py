"""ctypes wrapper for exactbwd.c (variant 1c in C).  Returns certified p*, mode, runner-up, counts."""
import ctypes, os, numpy as np, time
_here = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_here, 'libexactbwd.so'))
_lib.ctc_exact_backward.restype = ctypes.c_int
_lib.ctc_exact_backward.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_long, ctypes.c_int,
    ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_double)]
STATUS = {0: 'ok', 1: 'deadline', 2: 'gen_cap', 3: 'pool_cap'}
def decode_c(table, time_limit=600.0, gen_cap=10**12, pool_cap=400000, want_H=False):
    tb = np.ascontiguousarray(np.asarray(table, dtype=np.float64)); T, W = tb.shape
    out_p = (ctypes.c_double * 2)(); l1 = (ctypes.c_int * (T + 2))(); l2 = (ctypes.c_int * (T + 2))()
    n1 = ctypes.c_int(0); n2 = ctypes.c_int(0); stats = (ctypes.c_long * 4)()
    H = (ctypes.c_double * (W * (T + 1)))() if want_H else None
    t0 = time.perf_counter()
    st = _lib.ctc_exact_backward(tb.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), T, W, time_limit, gen_cap, pool_cap,
                                 out_p, l1, ctypes.byref(n1), l2, ctypes.byref(n2), stats, H)
    dt = time.perf_counter() - t0
    r = dict(status=STATUS[st], p1=out_p[0], p2=out_p[1], l1=tuple(l1[:n1.value]), l2=tuple(l2[:n2.value]),
             gen=stats[0], exp_final=stats[1], exp_bwd=stats[2], sec=dt, T=T, W=W)
    if want_H: r['H'] = np.frombuffer(H, dtype=np.float64).reshape(W, T + 1).copy()
    return r
