"""ctypes loader for the C core, compiled on demand with `cc` (falls back to None if unavailable).

The C core is compiled with `-ffp-contract=off` so that every sum is rounded exactly as in the
pure-Python mirror; the test suite gates the two backends bit-identical.
"""
import ctypes, os, subprocess, sys, time

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, '_core', 'certctc.c')
_BUILD = os.path.join(_HERE, '_core', 'build')
_LIB = os.path.join(_BUILD, 'libcertctc.so')
_CFLAGS = ['-O2', '-ffp-contract=off', '-fno-fast-math', '-shared', '-fPIC']

_lib = None
_load_error = None
STATUS = {0: 'ok', 1: 'deadline', 2: 'gen_cap', 3: 'pool_cap'}


def build(force=False):
    """Compile the C core if the library is missing or older than the source. Raises on failure."""
    os.makedirs(_BUILD, exist_ok=True)
    if not force and os.path.exists(_LIB) and os.path.getmtime(_LIB) >= os.path.getmtime(_SRC):
        return _LIB
    cc = os.environ.get('CC', 'cc')
    cmd = [cc] + _CFLAGS + ['-o', _LIB, _SRC]
    subprocess.run(cmd, check=True, capture_output=True)
    return _LIB


def load():
    """Return the loaded ctypes library, or None if the C backend cannot be built/loaded."""
    global _lib, _load_error
    if _lib is not None: return _lib
    if _load_error is not None: return None
    try:
        build()
        lib = ctypes.CDLL(_LIB)
        lib.certctc_decode.restype = ctypes.c_int
        lib.certctc_decode.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_long, ctypes.c_long,
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_long),
            ctypes.POINTER(ctypes.c_double)]
        _lib = lib
        return lib
    except Exception as e:      # no compiler, compile error, load error -> pure-Python fallback
        _load_error = e
        return None


def load_error():
    return _load_error


def decode_c(table, time_limit=float('inf'), gen_cap=None, pool_cap=None, want_H=True):
    """table: numpy (T, W) float64 array or list of lists, blank = column 0. Same result dict as
    `_pysearch.decode_python` (status is an int code)."""
    import numpy as np
    lib = load()
    if lib is None: raise RuntimeError('C backend unavailable: %r' % (_load_error,))
    tb = np.ascontiguousarray(np.asarray(table, dtype=np.float64)); T, W = tb.shape
    if gen_cap is None: gen_cap = 2 ** 62
    if pool_cap is None: pool_cap = min(gen_cap + 16, 50_000_000)
    if time_limit == float('inf'): time_limit = 1e18
    out_p = (ctypes.c_double * 2)(); l1 = (ctypes.c_int * (T + 2))(); l2 = (ctypes.c_int * (T + 2))()
    n1 = ctypes.c_int(0); n2 = ctypes.c_int(0); stats = (ctypes.c_long * 4)()
    H = (ctypes.c_double * (W * (T + 1)))() if want_H else None
    st = lib.certctc_decode(tb.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), T, W, float(time_limit),
                            int(gen_cap), int(pool_cap), out_p, l1, ctypes.byref(n1), l2, ctypes.byref(n2), stats, H)
    r = dict(status=int(st), p1=out_p[0], p2=out_p[1], l1=tuple(l1[:n1.value]), l2=tuple(l2[:n2.value]),
             gen=int(stats[0]), exp_final=int(stats[1]), exp_bwd=int(stats[2]), H=None)
    if want_H:
        Hm = np.frombuffer(H, dtype=np.float64).reshape(W, T + 1)
        r['H'] = [list(map(float, row)) for row in Hm]
    return r
