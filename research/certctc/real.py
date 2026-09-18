"""Run certctc on the real posterior tables (T4 LibriSpeech .npz + T7 .npy) and write one JSON
row per table.  Greedy (Viterbi-collapse) is recomputed here; the beam-k columns of the results
table come from T2b's `real_*.jsonl` (toolkit `topk_labellings`, unchanged) via `assemble`.

    python -m certctc real [--shard i --nshards n] [--t4 DIR] [--t7 DIR] [--out FILE] [--time-limit S]
    python -m certctc assemble [--t2b DIR] [--rows GLOB]      -> markdown table on stdout
"""
import glob, json, os, sys, time

DEFAULT_SCRATCH = '/path/to/decoder-push'  # directory holding T4/posteriors_*.npz and T7/posteriors/*.npy (not redistributed)
_HERE = os.path.dirname(os.path.abspath(__file__))


def load_tables(t4_dir, t7_dir):
    import numpy as np
    tables = []
    if t4_dir and os.path.isdir(t4_dir):
        for tag in ('clean', '10dB', '5dB', '0dB'):
            f = os.path.join(t4_dir, 'posteriors_%s.npz' % tag)
            if not os.path.exists(f): continue
            z = np.load(f)
            for k in z.keys():
                if k.startswith('P'): tables.append(('T4/%s/%s' % (tag, k), z[k]))
    if t7_dir and os.path.isdir(t7_dir):
        for f in sorted(glob.glob(os.path.join(t7_dir, '*.npy'))):
            tables.append(('T7/' + os.path.basename(f)[:-4], np.load(f)))
    return tables


def greedy(P):
    import numpy as np
    arg = [int(x) for x in np.asarray(P).argmax(1)]
    return tuple(s for t, s in enumerate(arg) if (t == 0 or s != arg[t - 1]) and s != 0)


def run(args):
    import numpy as np
    from .decoder import decode, BudgetExceeded
    from .verify import verify, ctc_prob
    tables = load_tables(args.t4, args.t7)
    if not tables:
        print('no tables found under %s / %s' % (args.t4, args.t7)); return 1
    out = open(args.out, 'a')
    for i, (name, P) in enumerate(tables):
        if i % args.nshards != args.shard: continue
        P = np.asarray(P, dtype=np.float64); T, W = P.shape
        row = dict(name=name, T=T, W=W, conf_mean=float(P.max(1).mean()), blank_frac=float((P.argmax(1) == 0).mean()))
        try:
            c = decode(P, blank=0, backend=args.backend, time_limit=args.time_limit)
            v = verify(P.tolist(), c)
            row.update(status='ok', sec=c.wall_seconds, gen=c.generations_total, exp_final=c.expansions_final,
                       exp_bwd=c.expansions_backward, p1=c.p_mode, p2=c.p_runner_up, margin=c.margin, D=c.D,
                       l1=list(c.mode), l2=list(c.runner_up) if c.runner_up is not None else None,
                       verify_ok=bool(v), p1_check=v.p_mode_recomputed, p2_check=v.p_runner_up_recomputed, backend=c.backend)
        except BudgetExceeded as e:
            row.update(status=e.status, sec=e.partial['wall_seconds'], gen=e.partial['gen'], backend=e.partial['backend'])
        lg = greedy(P); row['greedy'] = dict(l=list(lg), p=ctc_prob(lg, P.tolist()), D=len(lg))
        out.write(json.dumps(row) + '\n'); out.flush()
        if row['status'] == 'ok':
            print('%-70s T=%3d status=%-8s sec=%7.1f gen=%9d expF=%5d D=%3d p*=%.3e p2=%.3e margin=%.3f verify=%s greedy/p*=%.3f' % (
                name, T, row['status'], row['sec'], row['gen'], row['exp_final'], row['D'], row['p1'], row['p2'], row['margin'],
                row['verify_ok'], row['greedy']['p'] / row['p1'] if row['p1'] > 0 else float('nan')), flush=True)
        else:
            print('%-70s T=%3d status=%-8s sec=%7.1f gen=%9d' % (name, T, row['status'], row['sec'], row['gen']), flush=True)
    return 0


def _domain(n):
    if n.startswith('T4/'): return 'LibriSpeech ' + n.split('/')[1]
    b = n[3:]
    if 'atc_uwb' in b: return 'UWB-ATCC (' + b.split('__')[0] + ')'
    if 'ami_sdm' in b: return 'AMI-SDM'
    if 'torgo_ctl' in b: return 'TORGO control'
    if 'torgo_dys' in b: return 'TORGO dysarthric (' + b.split('__')[0] + ')'
    return '?'


_ORDER = ['LibriSpeech clean', 'LibriSpeech 10dB', 'LibriSpeech 5dB', 'LibriSpeech 0dB', 'UWB-ATCC (base960h)',
          'UWB-ATCC (torgoft)', 'AMI-SDM', 'TORGO dysarthric (base960h_dys)', 'TORGO dysarthric (torgoft)', 'TORGO control']


def assemble(args):
    """Merge certctc rows with T2b's beam columns; cross-check certified numbers against T2b; print markdown."""
    import statistics as st
    rows = [json.loads(l) for f in sorted(glob.glob(args.rows)) for l in open(f) if l.strip()]
    seen = set(); rows = [r for r in rows if not (r['name'] in seen or seen.add(r['name']))]
    t2b = {}
    for f in sorted(glob.glob(os.path.join(args.t2b, 'real_*.jsonl'))):
        for l in open(f):
            if l.strip(): r = json.loads(l); t2b[r['name']] = r
    rows.sort(key=lambda r: (_ORDER.index(_domain(r['name'])) if _domain(r['name']) in _ORDER else 99, r['name']))
    def ratio(r, k):
        b = t2b.get(r['name'], {}).get(k)
        if not b or r.get('p1', 0) <= 0: return float('nan')
        return b['p'] / r['p1']
    print('| table | T | D | status | sec | gen | final exp | p* (certified) | p2 (certified) | margin | verify | greedy/p* | beam-5/p* | beam-50/p* | beam-800/p* |')
    print('|---|--:|--:|---|--:|--:|--:|--:|--:|--:|---|--:|--:|--:|--:|')
    agree = 0; disagree = []; ok_rows = [r for r in rows if r['status'] == 'ok']
    for r in rows:
        nm = r['name'].replace('T7/', '').replace('base960h__', '').replace('uwb-atcc_', '').replace('AMI_EN2002a_sdm_', '')
        if r['status'] != 'ok':
            print('| %s | %d | - | %s | %.1f | %.2e | - | - | - | - | - | - | - | - | - |' % (nm, r['T'], r['status'], r['sec'], r['gen'])); continue
        g = r['greedy']['p'] / r['p1'] if r['p1'] > 0 else float('nan')
        print('| %s | %d | %d | %s | %.1f | %.2e | %d | %.3e | %.3e | %.3f | %s | %.3f | %.3f | %.3f | %.3f |' % (
            nm, r['T'], r['D'], r['status'], r['sec'], r['gen'], r['exp_final'], r['p1'], r['p2'],
            r['margin'] if r['margin'] != 'inf' else float('inf'), 'PASS' if r.get('verify_ok') else 'FAIL', g,
            ratio(r, 'beam5'), ratio(r, 'beam50'), ratio(r, 'beam800')))
        o = t2b.get(r['name'])
        if o and o.get('status') == 'ok':
            same = (abs(o['p1'] - r['p1']) <= 1e-12 * r['p1'] and abs(o['p2'] - r['p2']) <= 1e-12 * max(r['p2'], 1e-300)
                    and o['l1'] == r['l1'] and o['gen'] == r['gen'] and o['exp_final'] == r['exp_final'])
            if same: agree += 1
            else: disagree.append((r['name'], o['p1'], r['p1'], o['gen'], r['gen'], o['exp_final'], r['exp_final']))
    print('\n**Per-domain summary** (n, median T, median certified p*, p* range, median margin, decoder = mode counts, worst greedy/p*, worst beam-800/p*, worst sec, cut-offs):\n')
    print('| domain | n | T med | p* med | p* range | margin med | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | worst greedy/p* | worst beam-800/p* | worst sec | cut-offs |')
    print('|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|')
    for d in _ORDER:
        rs = [r for r in rows if _domain(r['name']) == d]
        if not rs: continue
        ok = [r for r in rs if r['status'] == 'ok']
        if not ok: continue
        def eq(k):
            if k == 'greedy': return sum(1 for r in ok if abs(r['greedy']['p'] / r['p1'] - 1) <= 1e-9)
            return sum(1 for r in ok if abs(ratio(r, k) - 1) <= 1e-9)
        ps = [r['p1'] for r in ok]; ms = [r['margin'] for r in ok if isinstance(r['margin'], (int, float))]
        print('| %s | %d | %.0f | %.2e | %.1e-%.1e | %.3f | %d/%d | %d/%d | %d/%d | %d/%d | %.3f | %.3f | %.0f | %d |' % (
            d, len(rs), st.median([r['T'] for r in rs]), st.median(ps), min(ps), max(ps), st.median(ms) if ms else float('nan'),
            eq('greedy'), len(ok), eq('beam5'), len(ok), eq('beam50'), len(ok), eq('beam800'), len(ok),
            min(r['greedy']['p'] / r['p1'] for r in ok), min(ratio(r, 'beam800') for r in ok), max(r['sec'] for r in rs), len(rs) - len(ok)))
    if ok_rows:
        worst = max(ok_rows, key=lambda r: r['sec'])
        print('\nRows: %d (ok %d, cut-offs %s). Worst wall-clock: %s T=%d %.1f s. gen/(T^2 W^2): min %.3f, median %.3f, max %.3f. verify() PASS on %d/%d.' % (
            len(rows), len(ok_rows), [r['name'] for r in rows if r['status'] != 'ok'], worst['name'], worst['T'], worst['sec'],
            min(r['gen'] / (r['T'] ** 2 * r['W'] ** 2) for r in ok_rows), st.median([r['gen'] / (r['T'] ** 2 * r['W'] ** 2) for r in ok_rows]),
            max(r['gen'] / (r['T'] ** 2 * r['W'] ** 2) for r in ok_rows), sum(1 for r in ok_rows if r.get('verify_ok')), len(ok_rows)))
    print('GATE certctc vs T2b real_*.jsonl (p*, p2, mode, generations, final expansions all identical): %d/%d agree, disagreements %d -> %s' % (
        agree, len(ok_rows), len(disagree), 'PASS' if not disagree and agree == len(ok_rows) else 'FAIL'))
    for d in disagree: print('  DIFF', d)
    return 0
