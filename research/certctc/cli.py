"""certctc command line.

    python -m certctc decode table.npy [--blank 0] [--json out.json] [--backend auto|c|python] [--time-limit S] [--gen-cap N] [--key K]
    python -m certctc bench [--gen-cap 5000000] [--time-limit 60] [--W 5,32] [--T 16,32,64,128] [--out bench.jsonl]
    python -m certctc real   [--shard i --nshards n] [--t4 DIR] [--t7 DIR] [--out real_rows.jsonl]
    python -m certctc assemble [--rows 'certctc/real_rows*.jsonl'] [--t2b T2b]

`decode` accepts .npy, .npz (with --key), .json (list of rows) or whitespace text (numpy.loadtxt).
"""
import argparse, json, os, sys


def _load_table(path, key=None):
    import numpy as np
    if path.endswith('.npy'): return np.load(path)
    if path.endswith('.npz'):
        z = np.load(path)
        if key is None:
            keys = list(z.keys())
            if len(keys) != 1: raise SystemExit('npz has keys %s; pass --key' % keys)
            key = keys[0]
        return z[key]
    if path.endswith('.json'): return np.asarray(json.load(open(path)), dtype=np.float64)
    return np.loadtxt(path)


def cmd_decode(args):
    from .decoder import decode
    from .verify import verify
    P = _load_table(args.table, args.key)
    cert = decode(P, blank=args.blank, backend=args.backend, time_limit=args.time_limit, max_generations=args.gen_cap)
    rep = verify(P.tolist(), cert)
    print(cert.summary())
    print('verify(): %s%s' % ('PASS' if rep else 'FAIL', '' if rep else ' ' + '; '.join(rep.problems)))
    if args.json:
        with open(args.json, 'w') as f: f.write(cert.to_json(indent=1) + '\n')
        print('certificate written to', args.json)
    return 0 if rep else 2


def main(argv=None):
    ap = argparse.ArgumentParser(prog='certctc', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('decode'); d.add_argument('table'); d.add_argument('--blank', type=int, default=0)
    d.add_argument('--json'); d.add_argument('--backend', default='auto'); d.add_argument('--time-limit', type=float, default=None)
    d.add_argument('--gen-cap', type=int, default=None); d.add_argument('--key', default=None)
    b = sub.add_parser('bench'); b.add_argument('--gen-cap', type=int, default=5_000_000); b.add_argument('--time-limit', type=float, default=60.0)
    b.add_argument('--W', default='5,32'); b.add_argument('--T', default='16,32,64,128'); b.add_argument('--seed', type=int, default=7)
    b.add_argument('--out', default=None); b.add_argument('--backend', default='auto')
    r = sub.add_parser('real'); r.add_argument('--shard', type=int, default=0); r.add_argument('--nshards', type=int, default=1)
    from .real import DEFAULT_SCRATCH
    r.add_argument('--t4', default=os.path.join(DEFAULT_SCRATCH, 'T4')); r.add_argument('--t7', default=os.path.join(DEFAULT_SCRATCH, 'T7', 'posteriors'))
    r.add_argument('--out', default='real_rows.jsonl'); r.add_argument('--time-limit', type=float, default=600.0); r.add_argument('--backend', default='auto')
    a = sub.add_parser('assemble'); a.add_argument('--rows', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'real_rows*.jsonl'))
    a.add_argument('--t2b', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'code', 'certified-exact-decoder'))
    args = ap.parse_args(argv)
    if args.cmd == 'decode': return cmd_decode(args)
    if args.cmd == 'bench':
        from .bench import run; return run(args)
    if args.cmd == 'real':
        from .real import run; return run(args)
    if args.cmd == 'assemble':
        from .real import assemble; return assemble(args)


if __name__ == '__main__':
    sys.exit(main())
