"""Combined SNR score: mean(WADA, VAD) in dB; if WADA is saturated at its table floor/ceiling (-20 or 100 dB; the
Gamma/Gaussian amplitude model is violated by clipped/AGC'd LiveATC audio) use the VAD estimate alone and flag it."""
import json, numpy as np
cand = json.load(open('atco2_candidates_snr.json'))
def comb(m):
    sat = m['wada'] <= -19.99 or m['wada'] >= 99.99
    return (m['vad'] if sat else 0.5 * (m['wada'] + m['vad'])), sat
for m in cand: m['snr'], m['wada_saturated'] = comb(m)
S = np.array([m['snr'] for m in cand])
print(f"combined SNR percentiles 5/25/50/75/95 = {np.percentile(S,[5,25,50,75,95]).round(1)}; n<15: {(S<15).sum()} n<10: {(S<10).sum()} n<5: {(S<5).sum()}; WADA saturated: {sum(m['wada_saturated'] for m in cand)}")
cand.sort(key=lambda m: m['snr']); sel = cand[:16]
for m in sel: m['domain'] = 'atc_atco2_hard'
json.dump(cand, open('atco2_candidates_snr.json', 'w'), indent=1); json.dump(sel, open('selection.json', 'w'), indent=1)
print("SELECTED 16 (lowest combined SNR):")
for m in sel: print(f"  comb {m['snr']:5.1f}  wada {m['wada']:6.1f}{'*' if m['wada_saturated'] else ' '} vad {m['vad']:5.1f}  {m['dur']:.2f}s {m['nwords']:2d}w peak {m['peak']:.2f} {m['id'].replace('atco2_test-set-1h_','')} | {m['text'][:60]}")
a4 = json.load(open('a4_snr.json'))
for r in a4: r['snr'], r['wada_saturated'] = comb(r)
json.dump(a4, open('a4_snr.json', 'w'), indent=1)
for dom in ('atc_uwb', 'atc_atco2'):
    xs = [r['snr'] for r in a4 if r['domain'] == dom]; print(f"A4 {dom} combined SNR: median {np.median(xs):.1f} range {min(xs):.1f}..{max(xs):.1f}")
