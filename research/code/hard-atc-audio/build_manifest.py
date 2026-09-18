"""R3 manifest: (i) the 16 A4 clips (8 UWB-ATCC test + 8 ATCO2 test; >=15 dB) re-run through the R3 pipeline,
(ii) 8 real ATCO2 clips sampled (seed 0) from the 10-15 dB band, (iii) the 16 lowest-SNR real ATCO2 clips,
(iv) SYNTHETIC: the 8 A4 ATCO2 clips passed through a VHF-channel degradation at nominal 10 and 5 dB SNR.
Degradation recipe (degrade()): band-limit 300-3400 Hz (torchaudio highpass_biquad 300 Hz + lowpass_biquad 3400 Hz,
Q=0.707, each applied twice = 4th order); additive white Gaussian noise passed through the same band-limit and scaled so
that (mean power of speech-active 20 ms frames of the band-limited clip) / (noise power) = nominal SNR -- speech-active
= frames with power > 10x the mean of the quietest 20 % of frames; then mild hard clipping at 0.7x the peak of the noisy
signal. The clip's own channel noise is part of the 'signal', so the effective SNR is below nominal; the measured
(WADA / VAD / combined) SNR of the degraded file is what is reported."""
import json, os, sys, numpy as np, soundfile as sf, torch, torchaudio
sys.path.insert(0, '.'); from snr import wada_snr, vad_snr
def load16(path):
    w, sr = sf.read(path, dtype='float32')
    if w.ndim > 1: w = w.mean(axis=1)
    if sr != 16000: w = torchaudio.functional.resample(torch.from_numpy(w), sr, 16000).numpy()
    return w.astype(np.float32)
def comb(wada, vad):
    sat = wada <= -19.99 or wada >= 99.99
    return (vad if sat else 0.5 * (wada + vad)), sat
def bandlimit(x):
    t = torch.from_numpy(np.asarray(x, dtype=np.float32))
    for _ in range(2):
        t = torchaudio.functional.highpass_biquad(t, 16000, 300.0, 0.707)
        t = torchaudio.functional.lowpass_biquad(t, 16000, 3400.0, 0.707)
    return t.numpy()
def degrade(w, snr_db, seed):
    x = bandlimit(w).astype(np.float64)
    n = 320; nf = len(x) // n
    p = (x[:nf*n].reshape(nf, n) ** 2).mean(axis=1) + 1e-12
    N = np.sort(p)[:max(1, int(0.2 * nf))].mean(); sp = p[p > 10 * N]
    if len(sp) < 0.1 * nf: sp = np.sort(p)[-max(1, int(0.3 * nf)):]
    Ps = sp.mean()
    rng = np.random.default_rng(seed); noise = bandlimit(rng.standard_normal(len(x)).astype(np.float32)).astype(np.float64)
    noise *= np.sqrt(Ps / 10 ** (snr_db / 10) / (noise ** 2).mean())
    y = x + noise; c = 0.7 * np.abs(y).max(); y = np.clip(y, -c, c)
    return (y / max(np.abs(y).max(), 1e-9) * 0.9).astype(np.float32)
man = []
a4 = json.load(open('../A4/manifest.json')); a4snr = {r['id']: r for r in json.load(open('a4_snr.json'))}
for m in a4:
    p = m['path'] if m['path'].startswith('/') else os.path.normpath(os.path.join('../A4', m['path']))
    s = a4snr[m['id']]
    man.append(dict(domain=m['domain'], band_src='real', id=m['id'], text=m['text'], dur=m['dur'], path=p, wada=s['wada'], vad=s['vad'], snr=s['snr'], wada_saturated=s['wada_saturated'], synthetic=False))
cand = json.load(open('atco2_candidates_snr.json'))
mid = [c for c in cand if 10.0 <= c['snr'] < 15.0]
rng = np.random.default_rng(0); idx = sorted(rng.choice(len(mid), 8, replace=False).tolist())
for i in idx:
    c = mid[i]; man.append(dict(domain='atc_atco2_mid', band_src='real', id=c['id'], text=c['text'], dur=c['dur'], path=c['path'], wada=c['wada'], vad=c['vad'], snr=c['snr'], wada_saturated=c['wada_saturated'], synthetic=False))
for c in json.load(open('selection.json')):
    man.append(dict(domain='atc_atco2_hard', band_src='real', id=c['id'], text=c['text'], dur=c['dur'], path=c['path'], wada=c['wada'], vad=c['vad'], snr=c['snr'], wada_saturated=c['wada_saturated'], synthetic=False))
os.makedirs('samples/synth', exist_ok=True)
for k, m in enumerate([m for m in a4 if m['domain'] == 'atc_atco2']):
    src = os.path.normpath(os.path.join('../A4', m['path'])); w = load16(src)
    for nominal in (10, 5):
        y = degrade(w, nominal, seed=1000 * nominal + k)
        out = f"samples/synth/{m['id']}__vhf{nominal}dB.wav"; sf.write(out, y, 16000)
        wa, va = wada_snr(y), vad_snr(y); s, sat = comb(wa, va)
        man.append(dict(domain=f'atc_atco2_synth{nominal}', band_src=f'synthetic nominal {nominal} dB', id=m['id'] + f'__vhf{nominal}dB', src_id=m['id'], text=m['text'], dur=m['dur'], path=out, wada=wa, vad=va, snr=s, wada_saturated=sat, synthetic=True, nominal_snr=nominal))
json.dump(man, open('manifest.json', 'w'), indent=1)
import collections
print('manifest', len(man), collections.Counter(m['domain'] for m in man))
for m in man: print(f"{m['domain']:18s} snr {m['snr']:5.1f} (wada {m['wada']:6.1f}{'*' if m['wada_saturated'] else ' '} vad {m['vad']:5.1f}) {m['dur']:.2f}s {len(m['text'].split()):2d}w {m['id'][-60:]}")
