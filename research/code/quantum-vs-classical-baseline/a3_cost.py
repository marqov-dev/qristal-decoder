"""A3: quantum argmax route (T3 model, imported unmodified from T3/c7_cost.py) vs the NEW classical exact
baseline (T2b variant 1c, measured generations on 70 real posteriors, T9's O(W*T)-per-node correction).
Units: one b-bit fixed-point multiply-add == one Toffoli-equivalent (T3's convention; generous to quantum)."""
import sys, json, glob, os, math, statistics as st
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(R, 'quantum-argmax-construction'))
import c7_cost as m                     # T3 model, unmodified
assert (m.c, m.W, m.Kdet, m.kappa) == (1.8, 32, 12, 2.0)
OUT = os.path.dirname(os.path.abspath(__file__))

rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(R, 'certified-exact-decoder', 'real_*.jsonl'))) for l in open(f)]
seen = set(); rows = [r for r in rows if not (r['name'] in seen or seen.add(r['name']))]
assert len(rows) == 70, len(rows)
assert all(r['status'] == 'ok' for r in rows)

def dom(n):
    if n.startswith('T4/'): return {'clean': 'clean', '10dB': '10 dB', '5dB': '5 dB', '0dB': '0 dB'}[n.split('/')[1]]
    b = n[3:]
    if 'atc_uwb' in b: return 'UWB-ATCC'
    if 'ami_sdm' in b: return 'AMI'
    if 'torgo_ctl' in b: return 'TORGO ctl'
    if 'torgo_dys' in b: return 'TORGO dys'
    raise ValueError(n)
ORDER = ['clean', '10 dB', '5 dB', '0 dB', 'UWB-ATCC', 'AMI', 'TORGO dys', 'TORGO ctl']
rows.sort(key=lambda r: (ORDER.index(dom(r['name'])), r['name']))

PER_GEN = 3            # multiply-adds per (frame, child-symbol) cell of one node build (assumption; T9: O(W*T) per node)
L_TREE = 3.2e3         # N58: Montanaro descent polylog n*log n*log W at D=130 (cheaper of the two quoted; Jarret-Wan 5.6e3)

res = []
for r in rows:
    T, W, D, gen, p1, p2 = r['T'], r['W'], r['D'], r['gen'], r['p1'], r['p2']
    assert W == 32 or D == 1, (r["name"], W)   # the 14 D=1 torgoft rows carry W=33 (collapsed model); they are listed, not costed
    flag = ''
    if not p2 or p2 <= 0 or p2 >= p1:
        mg, flag = 1.001, 'm=1.001 (p2 missing/equal)'
    else:
        mg = p1 / p2
    q = m.quantum(p1, mg, T, D)                              # G=21/sqrt(p*), uncompute x2
    qo = m.quantum(p1, mg, T, D, uncompute=1, G_const=9)     # T3's most-optimistic lower bound (not a valid circuit)
    C_old, C_old_node = m.classical(p1, T)                    # 1.8/p* * 3*(W-1)*T  and  1.8/p* * 3*T
    C_new = gen * PER_GEN * W * T                             # new baseline, multiply-adds
    C_node = gen                                              # node-only: 1 unit per generation
    # F11 tree-search route, reconstructed (see report): sqrt(|T_p*| * D) * L * per-oracle, |T_p*| = c/p*
    Q_tree = math.sqrt(m.c / p1 * D) * L_TREE * (q['per_oracle'] + T * (W + 4 * math.ceil(math.log2(W))))
    res.append(dict(name=r['name'], dom=dom(r['name']), T=T, D=D, degenerate=(D == 1), p1=p1, p2=p2, m=mg, flag=flag,
                    gen=gen, sec=r['sec'], b=q['b'], S=q['S'], G=q['G'], C_cell=m.C_cell(q['b']), per_oracle=q['per_oracle'],
                    Q=q['total'], Q_opt=qo['total'], qubits=q['qubits_pebble'], C_new=C_new, C_old=C_old, C_old_node=C_old_node,
                    C_node=C_node, Q_tree=Q_tree,
                    sp_old=C_old / q['total'], sp_new=C_new / q['total'], sp_opt=C_new / qo['total'], sp_node=C_node / q['total'],
                    sp_tree=C_new / Q_tree, t_1MHz=q['total'] / 1e6, t_1GHz=q['total'] / 1e9))
json.dump(res, open(os.path.join(OUT, 'a3_rows.json'), 'w'), indent=1)

def e(x, d=2): return f"{x:.{d}e}"
def short(n): return n.replace('T7/', '').replace('base960h__', '').replace('uwb-atcc_', '').replace('AMI_EN2002a_sdm_', '').replace('atc_uwb__', '').replace('torgo_dys__', '').replace('torgo_ctl__', '')
live = [x for x in res if not x['degenerate']]
degen = [x for x in res if x['degenerate']]
L = []
L.append("## Per-row table (56 non-degenerate rows, sorted by domain)\n")
L.append("Columns: T, D, certified p* (= p1), margin m = p*/p₂, b = register bits, Q = quantum argmax Toffolis (T3 model), logical qubits (checkpointed, 2⌈√T⌉·S·b), gen = measured classical generations (T2b variant 1c, C port), C_new = gen·3·W·T multiply-adds, C_old = 1.8/p*·3·(W−1)·T (T3's Graves baseline), speedup_old = C_old/Q (what T3 reported), speedup_new = C_new/Q, classical measured seconds, quantum seconds at 1 MHz and 1 GHz logical Toffoli rate.\n")
L.append("| domain | table | T | D | p* | m | b | Q (Toffoli) | qubits | gen | C_new | C_old | speedup_old | **speedup_new** | cls sec | Q @1 MHz (s) | Q @1 GHz (s) |")
L.append("|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for x in live:
    L.append(f"| {x['dom']} | {short(x['name'])} | {x['T']} | {x['D']} | {e(x['p1'],3)} | {x['m']:.3f}{' ⚑' if x['flag'] else ''} | {x['b']} | {e(x['Q'])} | {e(x['qubits'])} | {e(x['gen'])} | {e(x['C_new'])} | {e(x['C_old'])} | {e(x['sp_old'])} | **{e(x['sp_new'])}** | {x['sec']:.1f} | {e(x['t_1MHz'])} | {e(x['t_1GHz'])} |")
L.append("\n⚑ = p₂ missing or equal to p*, m set to 1.001. (No row needed it: all 70 have 0 < p₂ < p*.)\n" if not any(x['flag'] for x in res) else "\n⚑ = p₂ missing or equal to p*, m set to 1.001.\n")
L.append("## Degenerate rows (D = 1, `torgoft` collapsed model; listed, not costed)\n")
L.append("| table | T | D | p* | m | gen | cls sec |")
L.append("|---|--:|--:|--:|--:|--:|--:|")
for x in degen:
    L.append(f"| {short(x['name'])} | {x['T']} | {x['D']} | {e(x['p1'],3)} | {x['m']:.3f} | {e(x['gen'])} | {x['sec']:.1f} |")
L.append("\n## Per-domain summary (non-degenerate rows)\n")
L.append("| domain | n | T med | D med | p* med | p* min | m med | b range | Q med (Toffoli) | Q max | speedup_old med | **speedup_new med** | **speedup_new best** | rows Q < C_new | rows Q < C_old |")
L.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for d in ORDER:
    xs = [x for x in live if x['dom'] == d]
    if not xs: continue
    L.append(f"| {d} | {len(xs)} | {st.median([x['T'] for x in xs]):.0f} | {st.median([x['D'] for x in xs]):.0f} | {e(st.median([x['p1'] for x in xs]))} | {e(min(x['p1'] for x in xs))} | {st.median([x['m'] for x in xs]):.3f} | {min(x['b'] for x in xs)}–{max(x['b'] for x in xs)} | {e(st.median([x['Q'] for x in xs]))} | {e(max(x['Q'] for x in xs))} | {e(st.median([x['sp_old'] for x in xs]))} | **{e(st.median([x['sp_new'] for x in xs]))}** | **{e(max(x['sp_new'] for x in xs))}** | {sum(x['Q'] < x['C_new'] for x in xs)}/{len(xs)} | {sum(x['Q'] < x['C_old'] for x in xs)}/{len(xs)} |")
xs = live
L.append(f"| **all** | {len(xs)} | {st.median([x['T'] for x in xs]):.0f} | {st.median([x['D'] for x in xs]):.0f} | {e(st.median([x['p1'] for x in xs]))} | {e(min(x['p1'] for x in xs))} | {st.median([x['m'] for x in xs]):.3f} | {min(x['b'] for x in xs)}–{max(x['b'] for x in xs)} | {e(st.median([x['Q'] for x in xs]))} | {e(max(x['Q'] for x in xs))} | {e(st.median([x['sp_old'] for x in xs]))} | **{e(st.median([x['sp_new'] for x in xs]))}** | **{e(max(x['sp_new'] for x in xs))}** | {sum(x['Q'] < x['C_new'] for x in xs)}/{len(xs)} | {sum(x['Q'] < x['C_old'] for x in xs)}/{len(xs)} |")
best = max(live, key=lambda x: x['sp_new']); worst = min(live, key=lambda x: x['sp_new'])
L.append(f"\nBest row for quantum: {best['name']} (p* = {e(best['p1'],3)}, m = {best['m']:.3f}, b = {best['b']}): speedup_new = {e(best['sp_new'])} (Q = {e(best['Q'])} vs C_new = {e(best['C_new'])}); speedup_old was {e(best['sp_old'])}.")
L.append(f"Worst row for quantum: {worst['name']}: speedup_new = {e(worst['sp_new'])}.")
L.append(f"Median C_new/C_old over the 56 rows: {e(st.median([x['C_new']/x['C_old'] for x in live]))}; min {e(min(x['C_new']/x['C_old'] for x in live))}, max {e(max(x['C_new']/x['C_old'] for x in live))} (C_old > C_new only on {sum(x['C_old'] > x['C_new'] for x in live)} rows, all with p* below ≈1e-9).")
L.append("\n## Wall-clock framing\n")
L.append(f"Classical: measured seconds from the rows (T2b C port, single thread, 4 shards concurrently — times above ~45 s include contention). Range {min(x['sec'] for x in live):.1f}–{max(x['sec'] for x in live):.1f} s, median {st.median([x['sec'] for x in live]):.1f} s, total for the 56 rows {sum(x['sec'] for x in live):.0f} s.")
L.append(f"Quantum: Q Toffolis executed serially (the argmax route is inherently sequential: G Grover iterations, each a full reversible forward recursion) at 1 MHz and 1 GHz logical Toffoli rate. Median Q = {e(st.median([x['Q'] for x in live]))} → {st.median([x['t_1MHz'] for x in live]):.3g} s at 1 MHz ({st.median([x['t_1MHz'] for x in live])/3.156e7:.3g} years), {st.median([x['t_1GHz'] for x in live]):.3g} s at 1 GHz. Fastest quantum row (largest p*): {min(x['Q'] for x in live):.3g} Toffolis = {min(x['t_1MHz'] for x in live):.3g} s at 1 MHz. Slowest: {max(x['Q'] for x in live):.3g} Toffolis = {max(x['t_1MHz'] for x in live)/3.156e7:.3g} years at 1 MHz, {max(x['t_1GHz'] for x in live)/3.156e7:.3g} years at 1 GHz.")
n1 = sum(x['t_1MHz'] < x['sec'] for x in live); n2 = sum(x['t_1GHz'] < x['sec'] for x in live)
L.append(f"Rows where quantum wall-clock beats the measured classical seconds: {n1}/56 at 1 MHz, {n2}/56 at 1 GHz.")
L.append("\n## Sensitivity\n")
L.append(f"(a) Most quantum-favourable variant T3 listed (no certificate G = 9/√p*, no uncomputation — a lower bound, not a valid circuit): rows with Q_opt < C_new: {sum(x['Q_opt'] < x['C_new'] for x in live)}/56; best speedup {e(max(x['sp_opt'] for x in live))} ({max(live, key=lambda x: x['sp_opt'])['name']}); median {e(st.median([x['sp_opt'] for x in live]))}. Q_opt/Q = {e(live[0]['Q_opt']/live[0]['Q'])} on every row (constant factor 9/42).")
L.append(f"(b) Classical charged node-only (1 unit per generation, C_node = gen): rows with Q < C_node: {sum(x['Q'] < x['C_node'] for x in live)}/56; best speedup_node {e(max(x['sp_node'] for x in live))}; median {e(st.median([x['sp_node'] for x in live]))}.")
L.append(f"(c) Both at once (lower-bound circuit vs node-only classical): rows with Q_opt < gen: {sum(x['Q_opt'] < x['C_node'] for x in live)}/56; best {e(max(x['C_node']/x['Q_opt'] for x in live))}.")
L.append(f"(d) F11 tree-search route (reconstruction, see notes): rows with Q_tree < C_new: {sum(x['Q_tree'] < x['C_new'] for x in live)}/56; best speedup {e(max(x['sp_tree'] for x in live))}; Q_tree/Q_argmax median {e(st.median([x['Q_tree']/x['Q'] for x in live]))}.")
open(os.path.join(OUT, 'a3_tables.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
