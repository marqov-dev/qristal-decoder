"""R2 measurement: exact word-class posterior mass on the A4 in-domain ATC posteriors (16 clips) and the
T7 generic-model posteriors of the same 8 UWB-ATCC clips; comparison with beam-50 / beam-800 class rescoring."""
import sys, os, json, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fsa import all_strings_dfa, NFA
from classctc import class_posterior_np, class_posterior_py
from ctc import ctc_forward, topk_labellings, collapse
from atc_classes import ATCClasses, SPECS, build_slots, make_word_alphabet

D = '/path/to/decoder-push'  # directory holding A4/ and T7/ results and posteriors/*.npy (not redistributed)
OUT = os.path.join(D, 'R2'); BEAMS = (50, 800)
gate_fail = 0


def run(kind, results_path, post_dir, tag, domains):
    global gate_fail
    wa, inv = make_word_alphabet(kind); cl = ATCClasses(wa); W = wa.W; blank = wa.blank
    res = [r for r in json.load(open(results_path)) if r['domain'] in domains]
    sigma_star = all_strings_dfa(wa.sigma)
    perm = list(range(W)); perm[0], perm[blank] = blank, 0             # beam/forward toolkit wants blank = 0
    def lab_from_text(text): return [wa.delim if ch == ' ' else wa.char_to_id[ch] for ch in text.lower()]
    def text_of(l): return wa.text(l, inv)
    out = []
    for r in res:
        y = np.load(f"{post_dir}/{tag}__{r['domain']}__{r['id']}.npy"); T = y.shape[0]
        assert y.shape[1] == W and abs(y.sum(1) - 1).max() < 1e-9
        P = np.ascontiguousarray(y[:, perm]); tb = P.tolist()
        # --- real-table gates
        one = class_posterior_np(y, sigma_star, blank)
        mode = [perm[i] for i in r['mode']] if 'mode' in r else lab_from_text(r['mode_text'])   # A4 stores labels in permuted (blank=0) order
        p_mode_class = class_posterior_np(y, NFA.string(mode).to_dfa(wa.sigma), blank)
        p_mode_fwd = ctc_forward([perm[i] for i in mode], tb)
        g1 = abs(one - 1) < 1e-10; g2 = abs(p_mode_class - p_mode_fwd) <= 1e-12 * p_mode_fwd and abs(p_mode_fwd - r['p_star']) <= 1e-9 * r['p_star']
        print(f"GATE real table {r['id'][-34:]} T={T}: P(Sigma*)={one:.15f} -> {'PASS' if g1 else 'FAIL'}; P({{mode}})={p_mode_class:.6e} ctc_forward={p_mode_fwd:.6e} A4 p*={r['p_star']:.6e} -> {'PASS' if g2 else 'FAIL'}", flush=True)
        gate_fail += (not g1) + ((not g2) if 'mode' in r else 0)     # generic rows store only mode_text: p* check is informational there
        # --- beams (exact p(l) recomputed by ctc_forward; labels mapped back to native ids)
        beams = {}
        for b in BEAMS:
            t0 = time.perf_counter(); top = topk_labellings(tb, beam=b, k=b); dt = time.perf_counter() - t0
            beams[b] = ([([perm[i] for i in l], ctc_forward(l, tb)) for _, l in top], dt)
        row = dict(domain=r['domain'], id=r['id'], T=T, p_star=r['p_star'], p2=r['p2'], margin=r['margin'], ref=r['ref'],
                   mode_text=r['mode_text'], runnerup_text=r.get('runnerup_text'), wer_mode=r['wer_mode'], p_ref=r.get('p_ref'),
                   beam_sec={b: beams[b][1] for b in BEAMS}, beam_mass={b: sum(p for _, p in beams[b][0]) for b in BEAMS}, slots=[])
        for spec in SPECS[r['id']]:
            label, (c, k, z) = build_slots(cl, spec)
            t0 = time.perf_counter(); pc = class_posterior_np(y, c, blank); pk = class_posterior_np(y, k, blank); pz = class_posterior_np(y, z, blank); dt = time.perf_counter() - t0
            s = pc + pk + pz
            g3 = abs(s - 1) < 1e-9; gate_fail += (not g3)
            bsum = {}
            for b in BEAMS:
                hyps = beams[b][0]
                bsum[b] = dict(c=sum(p for l, p in hyps if c.accepts(l)), k=sum(p for l, p in hyps if k.accepts(l)), z=sum(p for l, p in hyps if z.accepts(l)),
                               n_c=sum(1 for l, _ in hyps if c.accepts(l)), n_k=sum(1 for l, _ in hyps if k.accepts(l)))
            top_k_hyp = None
            for l, p in beams[800][0]:
                if k.accepts(l): top_k_hyp = (text_of(l), p); break
            slot = dict(label=label, kind=spec[1], args=spec[2], Q=(c.n, k.n, z.n), p_correct=pc, p_competing=pk, p_residual=pz, sum=s,
                        cond_correct=(pc / (pc + pk) if pc + pk > 0 else None), sec=dt, beam=bsum, top_competing_hyp=top_k_hyp,
                        mode_in=('C' if c.accepts(lab_from_text(r['mode_text'])) else 'K' if k.accepts(lab_from_text(r['mode_text'])) else 'Z'),
                        ref_in=('C' if c.accepts(lab_from_text(r['ref'])) else 'K' if k.accepts(lab_from_text(r['ref'])) else 'Z'))
            row['slots'].append(slot)
            print(f"  [{label}] |Q|={c.n}/{k.n}/{z.n} P(correct)={pc:.4e} P(competing)={pk:.4e} P(residual)={pz:.4e} sum={s:.12f} {'PASS' if g3 else 'FAIL'} "
                  f"cond={slot['cond_correct'] if slot['cond_correct'] is None else round(slot['cond_correct'], 6)} | beam50 C={bsum[50]['c']:.4e} K={bsum[50]['k']:.4e} | beam800 C={bsum[800]['c']:.4e} K={bsum[800]['k']:.4e} "
                  f"| mode in {slot['mode_in']} ref in {slot['ref_in']} | top competing: {top_k_hyp} | {dt:.2f}s", flush=True)
        out.append(row)
        print(f"[{kind}] {r['id']} T={T} p*={r['p_star']:.3e} beam50 mass={row['beam_mass'][50]:.4f} ({row['beam_sec'][50]:.1f}s) beam800 mass={row['beam_mass'][800]:.4f} ({row['beam_sec'][800]:.1f}s)", flush=True)
        json.dump(out, open(f"{OUT}/results__{kind}.json", "w"), indent=1, default=str)
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('a4', 'both'):
        run('a4', f"{D}/A4/results__atcindom_annot.json", f"{D}/A4/posteriors", 'atcindom', ('atc_uwb', 'atc_atco2'))
    if which in ('generic', 'both'):
        run('generic', f"{D}/T7/results__base960h.json", f"{D}/T7/posteriors", 'base960h', ('atc_uwb',))
    print("REAL-TABLE GATES", "PASS" if gate_fail == 0 else f"FAIL ({gate_fail})")
