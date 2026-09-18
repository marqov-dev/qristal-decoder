"""Estimate SNR for all 501 ATCO2 candidates (+ the 16 A4 clips for reference) and pick the 16 lowest-WADA-SNR clips."""
import json, numpy as np, soundfile as sf, sys, os
sys.path.insert(0, '.'); from snr import wada_snr, vad_snr
import torch, torchaudio
def load16(path):
    w, sr = sf.read(path, dtype='float32')
    if w.ndim > 1: w = w.mean(axis=1)
    if sr != 16000: w = torchaudio.functional.resample(torch.from_numpy(w), sr, 16000).numpy()
    return w
cand = json.load(open('atco2_candidates.json'))
for m in cand:
    w = load16(m['path']); m['wada'] = wada_snr(w); m['vad'] = vad_snr(w); m['nwords'] = len(m['text'].split()); m['peak'] = float(abs(w).max())
W = np.array([m['wada'] for m in cand]); V = np.array([m['vad'] for m in cand])
print(f"ATCO2 candidates n={len(cand)}: WADA percentiles 5/25/50/75/95 = {np.percentile(W,[5,25,50,75,95]).round(1)}; min {W.min():.1f} max {W.max():.1f}")
print(f"  VAD  percentiles 5/25/50/75/95 = {np.percentile(V,[5,25,50,75,95]).round(1)}; corr(WADA,VAD) = {np.corrcoef(W,V)[0,1]:.2f}")
print(f"  n WADA<15: {(W<15).sum()}  <10: {(W<10).sum()}  <5: {(W<5).sum()}")
import collections
bysite = collections.defaultdict(list)
for m in cand: bysite['_'.join(m['id'].split('_')[2:4])].append(m['wada'])
for k, v in sorted(bysite.items(), key=lambda kv: np.median(kv[1])): print(f"  {k:28s} n={len(v):3d} WADA median {np.median(v):5.1f} min {min(v):5.1f}")
# reference: the 16 A4 clips
a4 = json.load(open('../A4/manifest.json')); ref = []
for m in a4:
    p = m['path'] if m['path'].startswith('/') else os.path.join('../A4', m['path'])
    w = load16(p); ref.append(dict(domain=m['domain'], id=m['id'], wada=wada_snr(w), vad=vad_snr(w)))
for dom in ('atc_uwb', 'atc_atco2'):
    xs = [r['wada'] for r in ref if r['domain'] == dom]; ys = [r['vad'] for r in ref if r['domain'] == dom]
    print(f"A4 {dom}: WADA median {np.median(xs):.1f} range {min(xs):.1f}..{max(xs):.1f}; VAD median {np.median(ys):.1f}")
json.dump(ref, open('a4_snr.json', 'w'), indent=1)
cand.sort(key=lambda m: m['wada'])
sel = cand[:16]
for m in sel: m['domain'] = 'atc_atco2_hard'
json.dump(cand, open('atco2_candidates_snr.json', 'w'), indent=1)
json.dump(sel, open('selection.json', 'w'), indent=1)
print("SELECTED 16 (lowest WADA):")
for m in sel: print(f"  {m['wada']:5.1f} dB (vad {m['vad']:5.1f}) {m['dur']:.2f}s {m['nwords']:2d}w peak {m['peak']:.2f} {m['id']} | {m['text'][:70]}")
