import json
def f(x): return f"{x:.2e}" if (x < 1e-2 or x == 0) else f"{x:.3f}"
def cid(i): return i.replace('uwb-atcc_TWR-', '').replace('atco2_test-set-1h_LKPR_RUZYNE_', '').replace('atco2_test-set-1h_LKTB_BRNO_', 'BRNO_').replace('_20201', '_')
summary = {}
for kind, title in (('a4', 'In-domain model `Jzuluaga/...-uwb-atcc-and-atcosim` (A4 posteriors, 16 clips, 33 slots)'), ('generic', 'Generic `facebook/wav2vec2-base-960h` (T7 posteriors), same 8 UWB-ATCC clips, 18 slots')):
    res = json.load(open(f'results__{kind}.json'))
    print(f"\n### {title}\n")
    print("| clip | T | p* | slot | P(correct) exact | P(competing) exact | P(residual) | P(correct \\| parseable) | beam-50 Σ correct | beam-800 Σ correct | exact − beam-50 | mode ∈ | top competing hypothesis (p) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    n = 0; hi = 0; gap1 = 0; gap01 = 0; gaps = []; secs = []; n_comp_hi = 0
    for r in res:
        for i, s in enumerate(r['slots']):
            tk = s['top_competing_hyp']; tk = f"`{tk[0][:60]}` ({tk[1]:.1e})" if tk else "—"
            cond = "—" if s['cond_correct'] is None else f(s['cond_correct'])
            b50 = s['beam']['50']['c']; b800 = s['beam']['800']['c']; g = s['p_correct'] - b50
            n += 1; hi += s['p_correct'] >= 0.9; gap1 += g > 0.1; gap01 += g > 0.01; gaps.append(g); secs.append(s['sec']); n_comp_hi += s['p_competing'] > 0.5
            print(f"| {cid(r['id']) if i == 0 else ''} | {r['T'] if i == 0 else ''} | {f(r['p_star']) if i == 0 else ''} | {s['label']} | **{f(s['p_correct'])}** | {f(s['p_competing'])} | {f(s['p_residual'])} | {cond} | {f(b50)} | {f(b800)} | {f(g)} | {s['mode_in']} | {tk} |")
    gaps.sort()
    summary[kind] = dict(slots=n, p_correct_ge_0_9=hi, gap_gt_0_1=gap1, gap_gt_0_01=gap01, gap_median=gaps[len(gaps)//2], gap_max=gaps[-1], sec_max=max(secs), competing_gt_0_5=n_comp_hi)
    print()
    print("| clip | Σ p over beam-50 hypotheses | Σ p over beam-800 hypotheses | beam-50 s | beam-800 s |")
    print("|---|---|---|---|---|")
    for r in res:
        print(f"| {cid(r['id'])} | {r['beam_mass']['50']:.4f} | {r['beam_mass']['800']:.4f} | {r['beam_sec']['50']:.1f} | {r['beam_sec']['800']:.1f} |")
print("\nSUMMARY", json.dumps(summary, indent=1))
