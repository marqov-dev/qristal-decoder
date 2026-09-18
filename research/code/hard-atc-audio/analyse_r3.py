import json, numpy as np, collections
R = json.load(open('results__r3.json'))
def band(s): return '>=15' if s >= 15 else ('10-15' if s >= 10 else ('5-10' if s >= 5 else '<5'))
for r in R: r['band'] = band(r['snr'])
med = lambda xs: float(np.median(xs)) if xs else float('nan')
def fmt_p(x): return '%.1e' % x
def summarise(rows, label):
    ok = [r for r in rows if r['status'] == 'ok']
    n = len(rows)
    def cnt(key): return f"{sum(1 for r in ok if r[key])}/{len(ok)}"
    def bcnt(b): return f"{sum(1 for r in ok if r['beams'][str(b)]['eq_mode'])}/{len(ok)}"
    wm = [r['wer_mode'] for r in ok]; wg = [r['wer_greedy'] for r in rows]; wb = [r['beams']['50']['wer'] for r in rows]
    nw = lambda r: len(r['ref'].split())
    corpus = lambda key_rows, f: sum(f(r) * nw(r) for r in key_rows) / max(sum(nw(r) for r in key_rows), 1)
    return (f"| {label} | {n} | {med([r['snr'] for r in rows]):.1f} ({min(r['snr'] for r in rows):.1f}–{max(r['snr'] for r in rows):.1f}) | {np.mean([r['conf_mean'] for r in rows]):.3f} / {np.mean([r['frac_conf_lt_0_9'] for r in rows]):.2f} | "
            f"{fmt_p(med([r['p_star'] for r in ok]))} ({fmt_p(min(r['p_star'] for r in ok))}–{fmt_p(max(r['p_star'] for r in ok))}) | {cnt('gate_pstar_lt_1_over_D')} | {med([r['margin'] for r in ok]):.2f} ({min(r['margin'] for r in ok):.2f}–{max(r['margin'] for r in ok):.1f}) | {sum(1 for r in ok if r['margin'] < 1.2)}/{len(ok)} | "
            f"{cnt('greedy_eq_mode')} | {bcnt(5)} | {bcnt(50)} | {bcnt(800)} | {np.mean(wm):.3f} ({corpus(ok, lambda r: r['wer_mode']):.3f}) | {np.mean(wg):.3f} ({corpus(rows, lambda r: r['wer_greedy']):.3f}) | {np.mean(wb):.3f} | "
            f"{cnt('one_char_edit')} | {cnt('ref_in_top2')} | {med([r['dec_sec'] for r in ok]):.1f} ({max(r['dec_sec'] for r in ok):.0f}) | {sum(1 for r in rows if r['status'] != 'ok')} |")
hdr = ("| set | n | SNR median (range) | conf mean / frac<0.9 | p\\* median (range) | gate p\\*<1/D | margin median (range) | margin<1.2 | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | WER mode mean (corpus) | WER greedy mean (corpus) | WER beam-50 mean | runner-up 1-char edit | ref in top-2 | C dec s median (max) | budget-exceeded |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
print("### Per SNR band, REAL audio only (combined WADA/VAD estimate)\n"); print(hdr)
for b in ('>=15', '10-15', '5-10', '<5'):
    rows = [r for r in R if not r['synthetic'] and r['band'] == b]
    if rows: print(summarise(rows, f"real {b} dB"))
print("\n### Per SNR band, SYNTHETIC VHF degradation of the 8 A4 ATCO2 clips\n"); print(hdr)
for b in ('10-15', '5-10', '<5'):
    rows = [r for r in R if r['synthetic'] and r['band'] == b]
    if rows: print(summarise(rows, f"synthetic {b} dB"))
print("\n### Per set\n"); print(hdr)
for d in ('atc_uwb', 'atc_atco2', 'atc_atco2_mid', 'atc_atco2_hard', 'atc_atco2_synth10', 'atc_atco2_synth5'):
    rows = [r for r in R if r['domain'] == d]
    if rows: print(summarise(rows, d))
print("\n### Per clip\n")
print("| set | clip | SNR (wada/vad) | T | D | conf / frac<0.9 | p\\* | 1/D | p₂ | margin | greedy/p\\* | b5/p\\* | b50/p\\* | b800/p\\* | p(ref)/p\\* | WER mode | WER greedy | WER b50 | 1-char | C dec s | gen | b800 s |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in R:
    b = r['beams']; sid = r['id'].replace('atco2_test-set-1h_', '').replace('uwb-atcc_TWR-', '')
    if r['status'] == 'ok':
        print(f"| {r['domain']} | {sid} | {r['snr']:.1f} ({r['wada']:.0f}/{r['vad']:.0f}) | {r['T']} | {r['D']} | {r['conf_mean']:.3f} / {r['frac_conf_lt_0_9']:.2f} | {r['p_star']:.1e} | {1/r['D']:.1e} | {r['p2']:.1e} | {r['margin']:.2f} | {r['greedy_over_pstar']:.2f} | {b['5']['ratio']:.2f} | {b['50']['ratio']:.2f} | {b['800']['ratio']:.2f} | {'n/a' if r['p_ref_over_pstar'] is None else '%.1e' % r['p_ref_over_pstar']} | {r['wer_mode']:.2f} | {r['wer_greedy']:.2f} | {b['50']['wer']:.2f} | {'Y' if r['one_char_edit'] else 'n(%d)' % r['char_edits_mode_vs_l2']} | {r['dec_sec']:.1f} | {r['gen']:.1e} | {b['800']['sec']:.1f} |")
    else:
        print(f"| {r['domain']} | {sid} | {r['snr']:.1f} ({r['wada']:.0f}/{r['vad']:.0f}) | {r['T']} | — | {r['conf_mean']:.3f} / {r['frac_conf_lt_0_9']:.2f} | **{r['status']} @ {r['dec_sec']:.0f}s gen={r['gen']:.1e}** | | | | {r['greedy_over_pstar']:.2f}† | | | | | — | {r['wer_greedy']:.2f} | {b['50']['wer']:.2f} | — | — | {r['gen']:.1e} | {b['800']['sec']:.1f} |")
print("\n### Transcripts (ref / certified mode / runner-up; greedy and beam-50 when they differ from the mode)\n")
for r in R:
    if r['domain'] in ('atc_uwb', 'atc_atco2'): continue
    sid = r['id'].replace('atco2_test-set-1h_', '')
    if r['status'] == 'ok':
        print(f"- `{sid}` SNR {r['snr']:.1f}, margin {r['margin']:.2f}, p* {r['p_star']:.1e}, WER(mode) {r['wer_mode']:.2f}\n  - ref : {r['ref']}\n  - mode: {r['mode_text']}\n  - 2nd : {r['runnerup_text']}" + (f"\n  - grdy: {r['greedy_text']}" if not r['greedy_eq_mode'] else "") + (f"\n  - b50 : {r['beams']['50']['text']}" if not r['beams']['50']['eq_mode'] else ""))
    else:
        print(f"- `{sid}` SNR {r['snr']:.1f}, **{r['status']}**\n  - ref : {r['ref']}\n  - grdy: {r['greedy_text']}\n  - b800: {r['beams']['800']['text']}")
# cross-tab: where beam-k misses the mode, what is the ratio and is the miss a better transcript?
print("\n### Misses\n")
for r in R:
    if r['status'] != 'ok': continue
    for k in ('5', '50', '800'):
        if not r['beams'][k]['eq_mode']:
            print(f"- beam-{k} ≠ mode on `{r['id'][-50:]}` (SNR {r['snr']:.1f}): p(beam)/p* = {r['beams'][k]['ratio']:.3f}; WER beam {r['beams'][k]['wer']:.2f} vs mode {r['wer_mode']:.2f}")
    if not r['greedy_eq_mode']:
        print(f"- greedy ≠ mode on `{r['id'][-50:]}` (SNR {r['snr']:.1f}): p(greedy)/p* = {r['greedy_over_pstar']:.3f}; WER greedy {r['wer_greedy']:.2f} vs mode {r['wer_mode']:.2f}")
# paired synthetic
print("\n### Paired: A4 ATCO2 clip clean → +VHF 10 dB → +VHF 5 dB\n")
print("| clip | clean SNR / p* / margin / greedy=mode / b50=mode / WER mode | 10 dB SNR / p* / margin / greedy / b50 / WER | 5 dB SNR / p* / margin / greedy / b50 / WER |\n|---|---|---|---|")
by = {r['id']: r for r in R}
for r in R:
    if r['domain'] != 'atc_atco2': continue
    cells = []
    for rr in (r, by.get(r['id'] + '__vhf10dB'), by.get(r['id'] + '__vhf5dB')):
        if rr is None: cells.append('—'); continue
        if rr['status'] == 'ok': cells.append(f"{rr['snr']:.1f} / {rr['p_star']:.1e} / {rr['margin']:.2f} / {'Y' if rr['greedy_eq_mode'] else 'n'} / {'Y' if rr['beams']['50']['eq_mode'] else 'n'} / {rr['wer_mode']:.2f}")
        else: cells.append(f"{rr['snr']:.1f} / {rr['status']} / WER greedy {rr['wer_greedy']:.2f}")
    print(f"| {r['id'].replace('atco2_test-set-1h_','')} | " + " | ".join(cells) + " |")
