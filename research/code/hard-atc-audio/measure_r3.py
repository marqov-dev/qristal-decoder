"""R3: in-domain ATC model on hard audio. Float64 posteriors (native column order) -> certctc certified mode / runner-up /
margin (C backend, 600 s budget; BudgetExceeded is recorded with the counters at cut-off) + verify(); greedy / beam-k
from the toolkit on the blank-swapped table (columns 0 and 28 swapped, as in A4). Resumable: existing posteriors reused."""
import sys, os, json, time, numpy as np
R3 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, R3)
sys.path.insert(0, os.path.join(R3, '..', 'certified-exact-decoder'))  # validation toolkit ctc.py
sys.path.insert(0, os.path.join(R3, '..', '..'))  # certctc package
from ctc import validate_ctc, validate_beam, topk_labellings, ctc_forward, collapse
from certctc import decode, verify, BudgetExceeded
import torch, soundfile as sf, torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2FeatureExtractor, Wav2Vec2CTCTokenizer
torch.set_num_threads(8)
MODEL = "Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim"; TAG = "r3"; TIME_LIMIT = 600.0
n, worst = validate_ctc(); print(f"GATE ctc_forward vs brute force: {n} labellings, worst rel err {worst:.2e} -> {'PASS' if worst < 1e-9 else 'FAIL'}")
n2, bad, w2 = validate_beam(); print(f"GATE prefix beam vs brute force: {n2} instances, {bad} wrong argmax, worst score err {w2:.2e} -> {'PASS' if bad == 0 and w2 < 1e-12 else 'FAIL'}")
if worst >= 1e-9 or bad or w2 >= 1e-12: raise SystemExit("gate failed")
fe = Wav2Vec2FeatureExtractor.from_pretrained(MODEL); tok = Wav2Vec2CTCTokenizer.from_pretrained(MODEL)
model = Wav2Vec2ForCTC.from_pretrained(MODEL).eval()
blank = model.config.pad_token_id; W = model.config.vocab_size
vocab = tok.get_vocab(); inv = {v: k for k, v in vocab.items()}; delim = tok.word_delimiter_token
assert vocab[delim] == 0 and blank == 28 and W == 31
print(f"model={MODEL} W={W} blank={blank} ({inv[blank]!r}) delim={delim!r}=0", flush=True)
perm = list(range(W)); perm[0], perm[blank] = blank, 0
def to_text(lab_native): return "".join(inv[i] for i in lab_native).replace(delim, " ").strip().lower()
def lev(a, b):
    d = np.zeros((len(a)+1, len(b)+1), dtype=int); d[:,0] = range(len(a)+1); d[0,:] = range(len(b)+1)
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1): d[i,j] = min(d[i-1,j]+1, d[i,j-1]+1, d[i-1,j-1] + (a[i-1] != b[j-1]))
    return int(d[-1,-1])
def wer(ref, hyp): r = ref.lower().split(); return lev(r, hyp.lower().split()) / max(len(r), 1)
def enc_native(text):
    lab = []
    for w in text.lower().split():
        if lab: lab.append(0)
        for ch in w:
            if ch not in vocab or vocab[ch] in (0, blank): return None
            lab.append(vocab[ch])
    return tuple(lab)
man = json.load(open(os.path.join(R3, 'manifest.json'))); out_path = os.path.join(R3, f"results__{TAG}.json")
results = json.load(open(out_path)) if os.path.exists(out_path) else []; done = {r['id'] for r in results}
for m in man:
    if m['id'] in done: continue
    pp = os.path.join(R3, f"posteriors/{TAG}__{m['domain']}__{m['id']}.npy")
    if os.path.exists(pp): probs = np.load(pp)
    else:
        wav, sr = sf.read(m['path'] if m['path'].startswith('/') else os.path.join(R3, m['path']), dtype="float32")
        if wav.ndim > 1: wav = wav.mean(axis=1)
        if sr != 16000: wav = torchaudio.functional.resample(torch.from_numpy(wav), sr, 16000).numpy()
        inp = fe(wav, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad(): logits = model(inp.input_values).logits[0]
        probs = torch.softmax(logits.double(), dim=-1).numpy(); np.save(pp, probs)
    T = probs.shape[0]; P = np.ascontiguousarray(probs[:, perm]); tb = P.tolist(); assert abs(P.sum(1) - 1).max() < 1e-9
    conf = P.max(axis=1)
    row = dict(domain=m['domain'], id=m['id'], ref=m['text'], synthetic=m['synthetic'], nominal_snr=m.get('nominal_snr'), snr=m['snr'], wada=m['wada'], vad=m['vad'],
               T=T, W=W, blank=blank, dur=round(m['dur'], 2), conf_mean=float(conf.mean()), conf_median=float(np.median(conf)), frac_conf_lt_0_9=float((conf < 0.9).mean()))
    try:
        cert = decode(probs, blank=blank, backend='c', time_limit=TIME_LIMIT); vr = verify(probs, cert)
        mode_n, l2_n = cert.mode, cert.runner_up; mode = tuple(perm[i] for i in mode_n); l2 = tuple(perm[i] for i in l2_n)
        row.update(status='ok', dec_sec=cert.wall_seconds, gen=cert.generations_total, exp_final=cert.expansions_final, exp_bwd=cert.expansions_backward,
                   verify_ok=bool(vr.ok), verify_rel_err=max(vr.rel_err_mode, vr.rel_err_runner_up), p_star=cert.p_mode, p2=cert.p_runner_up, margin=cert.margin, D=cert.D,
                   mode=list(mode), l2=list(l2), mode_text=to_text(mode_n), runnerup_text=to_text(l2_n))
    except BudgetExceeded as e:
        row.update(status=e.status, dec_sec=e.partial.get('wall_seconds'), gen=e.partial.get('gen'), exp_final=e.partial.get('exp_final'), exp_bwd=e.partial.get('exp_bwd'), verify_ok=None, p_star=None, p2=None, margin=None, D=None, mode=None, l2=None, mode_text=None, runnerup_text=None)
        mode = None
    greedy = collapse([int(i) for i in P.argmax(axis=1)]); p_greedy = ctc_forward(greedy, tb); greedy_text = to_text(tuple(perm[i] for i in greedy))
    beams = {}
    for b in (5, 50, 800):
        t0 = time.perf_counter(); top = topk_labellings(tb, beam=b, k=2); dt = time.perf_counter() - t0
        lb = top[0][1]; pb = ctc_forward(lb, tb); tb_text = to_text(tuple(perm[i] for i in lb))
        beams[b] = dict(l=list(lb), p=pb, ratio=(pb / row['p_star'] if mode else None), D=len(lb), eq_mode=(lb == mode) if mode else None, sec=dt, text=tb_text, wer=wer(m['text'], tb_text))
    pstar = row['p_star']
    if mode is None: pstar = max(p_greedy, max(v['p'] for v in beams.values())); row['p_best_found'] = pstar
    ref_l = enc_native(m['text']); p_ref = ctc_forward(tuple(perm[i] for i in ref_l), tb) if ref_l else None
    row.update(p_greedy=p_greedy, greedy_over_pstar=p_greedy / pstar, greedy_eq_mode=(greedy == mode) if mode else None, beams=beams, greedy_text=greedy_text,
               p_ref=p_ref, p_ref_over_pstar=(p_ref / pstar if p_ref else None), wer_greedy=wer(m['text'], greedy_text),
               wer_mode=(wer(m['text'], row['mode_text']) if mode else None), gate_pstar_lt_1_over_D=((row['p_star'] < 1.0 / max(row['D'], 1)) if mode else None),
               char_edits_mode_vs_l2=(lev(row['mode_text'], row['runnerup_text']) if mode else None), one_char_edit=((lev(row['mode_text'], row['runnerup_text']) == 1) if mode else None),
               word_edits_mode_vs_l2=(lev(row['mode_text'].split(), row['runnerup_text'].split()) if mode else None),
               ref_in_top2=(m['text'].split() in (row['mode_text'].split(), row['runnerup_text'].split())) if mode else None)
    results.append(row); json.dump(results, open(out_path, "w"), indent=1, default=str)
    if mode:
        print(f"[{m['domain']}] snr={m['snr']:.1f} T={T} D={row['D']} conf={row['conf_mean']:.3f} lt0.9={row['frac_conf_lt_0_9']:.2f} status=ok dec={row['dec_sec']:.1f}s gen={row['gen']} verify={row['verify_ok']} "
              f"p*={row['p_star']:.3e} p2={row['p2']:.3e} margin={row['margin']:.2f} 1/D={1/row['D']:.2e} greedy/p*={row['greedy_over_pstar']:.3f} b5={beams[5]['ratio']:.3f} b50={beams[50]['ratio']:.3f} b800={beams[800]['ratio']:.3f} "
              f"greedy{'=' if row['greedy_eq_mode'] else '≠'}mode WER mode={row['wer_mode']:.2f} greedy={row['wer_greedy']:.2f} b50={beams[50]['wer']:.2f} 1char={row['one_char_edit']} p(ref)/p*={row['p_ref_over_pstar'] if row['p_ref_over_pstar'] is None else '%.1e' % row['p_ref_over_pstar']} b800sec={beams[800]['sec']:.1f}", flush=True)
        print(f"    ref : {m['text']}\n    mode: {row['mode_text']}\n    2nd : {row['runnerup_text']}" + (f"\n    grdy: {greedy_text}" if not row['greedy_eq_mode'] else "") + (f"\n    b50 : {beams[50]['text']}" if not beams[50]['eq_mode'] else ""), flush=True)
    else:
        print(f"[{m['domain']}] snr={m['snr']:.1f} T={T} conf={row['conf_mean']:.3f} STATUS={row['status']} after {row['dec_sec']:.0f}s gen={row['gen']} exp_final={row['exp_final']} exp_bwd={row['exp_bwd']} best found p={pstar:.3e} greedy/p={row['greedy_over_pstar']:.3f} b5={beams[5]['p']/pstar:.3f} b50={beams[50]['p']/pstar:.3f} b800={beams[800]['p']/pstar:.3f} WER greedy={row['wer_greedy']:.2f} b50={beams[50]['wer']:.2f}", flush=True)
        print(f"    ref : {m['text']}\n    grdy: {greedy_text}\n    b800: {beams[800]['text']}", flush=True)
print("saved", out_path)
