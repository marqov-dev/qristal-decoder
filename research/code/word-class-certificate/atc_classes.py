"""ATC word classes as DFAs over a CTC character vocabulary.

Every "slot" is a triple of DFAs (correct, competing, residual = complement of both) built from
word-level patterns (fsa.WordAlphabet) and DFA boolean products:

  number slot   anchor + value v         correct   = anywhere(anchor . VALUE(v)) - anywhere(anchor . VALUE(v) . NUMWORD)
                                         competing = anywhere(anchor . NUMLIKE) - correct
  callsign slot prefix + suffix "37A"    correct   = anywhere(prefix . SUFFIX(v)) - anywhere(prefix . SUFFIX(v) . SUFFIXTOKEN)
                                         competing = anywhere(prefix . SUFFIXLIKE) - correct
  frequency     anchor + "121.9"         same shape with FREQ(v) / FREQLIKE
  phrase        phrase + alternatives    correct = anywhere(phrase); competing = union(anywhere(alt)) - correct

VALUE(v)   = every sequence of <= 4 ICAO number words (zero..nine, niner, hundred, thousand) whose
             value is v under the digit-run / multiplier parse ("one hundred" = "one zero zero" = 100).
NUMLIKE    = DIGIT (DIGIT|hundred|thousand){0,3}  (a superset of well-formed numbers: conservative).
SUFFIX(v)  = every tokenisation of the suffix string into digit words / NATO letters (alfa|alpha,
             juliett|juliet, xray) / "double X" / "triple X".
SUFFIXLIKE = (DIGIT | NATO | (double|triple) NATO){1,5}.
"""
import itertools
from fsa import NFA, DFA, WordAlphabet

DIGITS = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'niner': 9}
MULT = {'hundred': 100, 'thousand': 1000}
NATO = {'a': ['alfa', 'alpha'], 'b': ['bravo'], 'c': ['charlie'], 'd': ['delta'], 'e': ['echo'], 'f': ['foxtrot'], 'g': ['golf'],
        'h': ['hotel'], 'i': ['india'], 'j': ['juliett', 'juliet'], 'k': ['kilo'], 'l': ['lima'], 'm': ['mike'], 'n': ['november'],
        'o': ['oscar'], 'p': ['papa'], 'q': ['quebec'], 'r': ['romeo'], 's': ['sierra'], 't': ['tango'], 'u': ['uniform'],
        'v': ['victor'], 'w': ['whiskey'], 'x': ['xray'], 'y': ['yankee'], 'z': ['zulu']}
NATO_WORDS = [w for ws in NATO.values() for w in ws]
DIGIT_BY_VALUE = {d: [w for w, v in DIGITS.items() if v == d] for d in range(10)}


def number_value(tokens):
    """Digit-run / multiplier parse; None if malformed."""
    run = None; acc = 0
    for t in tokens:
        if t in DIGITS:
            run = (run or 0) * 10 + DIGITS[t]
        elif t in MULT:
            if run is None: return None
            acc += run * MULT[t]; run = None
        else:
            return None
    if run is not None: acc += run
    return acc


def value_sequences(v, max_tokens=4):
    toks = list(DIGITS) + list(MULT); out = []
    for k in range(1, max_tokens + 1):
        for seq in itertools.product(toks, repeat=k):
            if seq[0] in DIGITS and number_value(seq) == v: out.append(seq)
    return out


def suffix_tokenisations(s):
    """All ways to say the alphanumeric string s (e.g. 'hhh' -> triple hotel | hotel hotel hotel | ...)."""
    s = s.lower(); out = []
    def rec(i, acc):
        if i == len(s): out.append(tuple(acc)); return
        ch = s[i]
        if ch.isdigit():
            for w in DIGIT_BY_VALUE[int(ch)]: rec(i + 1, acc + [w])
        else:
            for w in NATO[ch]: rec(i + 1, acc + [w])
            for rep, word in ((2, 'double'), (3, 'triple')):
                if s[i:i + rep] == ch * rep:
                    for w in NATO[ch]: rec(i + rep, acc + [word, w])
    rec(0, []); return out


def freq_sequences(s):
    """'121.9' -> one two one decimal nine (+ optional trailing zeros, niner alias)."""
    ip, fp = s.split('.'); out = []
    for extra in range(0, 3 - len(fp) + 1):
        digs = ip + '.' + fp + '0' * extra
        parts = [DIGIT_BY_VALUE[int(c)] if c != '.' else ['decimal'] for c in digs]
        out += list(itertools.product(*parts))
    return out


class ATCClasses:
    def __init__(self, wa: WordAlphabet):
        self.wa = wa
        w = wa
        self.DIGIT = NFA.alt(*[w.token(d) for d in DIGITS])
        self.NUMWORD = NFA.alt(*[w.token(d) for d in list(DIGITS) + list(MULT) + ['decimal']])
        self.NUMLIKE = NFA.seq(self.DIGIT, w.wrepeat(NFA.alt(self.DIGIT, w.token('hundred'), w.token('thousand')), 0, 3))
        self.NATOTOK = NFA.alt(*[w.token(n) for n in NATO_WORDS])
        self.SUFFIXTOKEN = NFA.alt(self.DIGIT, self.NATOTOK, NFA.seq(NFA.alt(w.token('double'), w.token('triple')), self.NATOTOK))
        self.SUFFIXLIKE = w.wrepeat(self.SUFFIXTOKEN, 1, 5)
        self.FREQLIKE = NFA.seq(w.wrepeat(self.DIGIT, 1, 3), w.token('decimal'), w.wrepeat(self.DIGIT, 1, 3))

    def seqs(self, seqs):
        return NFA.alt(*[NFA.seq(*[self.wa.token(t) for t in s]) for s in seqs])

    def _anchor(self, anchor):
        if anchor is None: return NFA.eps()
        if isinstance(anchor, (list, tuple)): return NFA.alt(*[self.wa.lit(a) for a in anchor])
        return self.wa.lit(anchor)

    def _slot(self, anchor, correct_nfa, like_nfa, token_nfa, at_start=False):
        w = self.wa; A = self._anchor(anchor)
        place = (lambda p: NFA.seq(p, NFA.star(w.anyword()))) if at_start else w.anywhere
        c_raw = w.compile(place(NFA.seq(A, correct_nfa)))
        c_ext = w.compile(place(NFA.seq(A, correct_nfa, token_nfa)))
        correct = c_raw.difference(c_ext)
        like = w.compile(place(NFA.seq(A, like_nfa)))
        competing = like.difference(correct)
        residual = correct.union(competing).complement()
        return correct, competing, residual

    def number_slot(self, anchor, v, at_start=False):
        return self._slot(anchor, self.seqs(value_sequences(v)), self.NUMLIKE, self.NUMWORD, at_start)

    def callsign_slot(self, prefix, suffix):
        return self._slot(prefix, self.seqs(suffix_tokenisations(suffix)), self.SUFFIXLIKE, self.SUFFIXTOKEN)

    def freq_slot(self, anchor, s):
        return self._slot(anchor, self.seqs(freq_sequences(s)), self.FREQLIKE, self.NUMWORD)

    def phrase_slot(self, phrase, alternatives):
        w = self.wa
        correct = w.compile(w.anywhere(w.lit(phrase)))
        comp = None
        for a in alternatives:
            d = w.compile(w.anywhere(w.lit(a))); comp = d if comp is None else comp.union(d)
        competing = comp.difference(correct)
        residual = correct.union(competing).complement()
        return correct, competing, residual


def make_word_alphabet(kind):
    """'a4': Jzuluaga ATC model (W=31, blank=[PAD]=28, |=0, a..z=1..26).
       'generic': facebook/wav2vec2-base-960h (W=32, blank=<pad>=0, |=4, uppercase letters)."""
    if kind == 'a4':
        c2i = {chr(97 + i): 1 + i for i in range(26)}
        return WordAlphabet(c2i, delim_id=0, blank_id=28, W=31), {**{v: k for k, v in c2i.items()}, 0: '|', 27: '?', 28: '', 29: '', 30: ''}
    vocab = {"<pad>": 0, "<s>": 1, "</s>": 2, "<unk>": 3, "|": 4, "E": 5, "T": 6, "A": 7, "O": 8, "N": 9, "I": 10, "H": 11, "S": 12,
             "R": 13, "D": 14, "L": 15, "U": 16, "M": 17, "W": 18, "C": 19, "F": 20, "G": 21, "Y": 22, "P": 23, "B": 24, "V": 25,
             "K": 26, "'": 27, "X": 28, "J": 29, "Q": 30, "Z": 31}
    c2i = {k.lower(): v for k, v in vocab.items() if len(k) == 1 and k != '|'}
    inv = {v: (k.lower() if len(k) == 1 else '') for k, v in vocab.items()}; inv[4] = '|'
    return WordAlphabet(c2i, delim_id=4, blank_id=0, W=32), inv


# ------------------------------------------------------------------ per-clip clearance specs
# (slot label, kind, args).  The verifier is given the CLEARANCE (what the controller expects), so these
# are what a readback verifier would be handed for each clip; refs are the A4 manifest transcripts.
SPECS = {
    'uwb-atcc_TWR-34720N_002001_002559_AT': [
        ('departure "one hotel"', 'callsign', ('via', '1H')),                 # "... via voz one hotel departure" (anchor: via .. reads "voz" though) -> use prefix-free below
    ],
    'uwb-atcc_TWR-a1WcrN_000157_000469_AT': [
        ('callsign NOR-SHUTTLE 1515', 'callsign', ('nor shuttle', '1515')),
        ('runway 31', 'number', ('runway', 31)),
        ('phrase "line up"', 'phrase', ('line up', ['hold short', 'hold position', 'cleared for takeoff', 'cross'])),
    ],
    'uwb-atcc_TWR-a3o8f0_000000_000352_AT': [
        ('callsign OPERA-JET 300', 'callsign', ('opera jet', '300')),
        ('"one hotel" after confirmation', 'callsign', ('confirmation', '1H')),
    ],
    'uwb-atcc_TWR-A5lZHJ_000000_000613_AT': [
        ('callsign CSA 37A', 'callsign', ('csa', '37A')),
        ('runway 31', 'number', ('runway', 31)),
        ('phrase "cleared for takeoff"', 'phrase', ('cleared for takeoff', ['cleared for landing', 'cleared to land', 'line up', 'hold short', 'hold position'])),
        ('wind 160', 'number', ('wind', 160)),
        ('knots 5 (after degrees)', 'number', ('degrees', 5)),
    ],
    'uwb-atcc_TWR-A5lZHJ_002805_003388_PIAT': [
        ('callsign AUSTRIAN 706P', 'callsign', ('austrian', '706P')),
    ],
    'uwb-atcc_TWR-a8R9jE_000144_000596_AT': [
        ('callsign CSA 731', 'callsign', ('csa', '731')),
        ('frequency 121.9 (after ground)', 'freq', ('ground', '121.9')),
    ],
    'uwb-atcc_TWR-a8R9jE_000700_001023_PIAT': [
        ('callsign CSA 71', 'callsign', ('csa', '71')),
        ('leading number 19', 'number_start', (None, 19)),
    ],
    'uwb-atcc_TWR-A64ueL_000128_000777_PI': [
        ('callsign SKY-TRAVEL 1102', 'callsign', ('sky travel', '1102')),
        ('stand 22A (after standing)', 'callsign', ('standing', '22A')),
    ],
    'atco2_test-set-1h_LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536': [
        ('callsign OK-FAO', 'callsign', ('oscar kilo', 'FAO')),
        ('runway 27', 'number', ('runway', 27)),
        ('phrase "taxi to holding point"', 'phrase', ('taxi to holding point', ['line up', 'cross', 'hold short', 'hold position'])),
        ('taxiway A C (after via)', 'callsign', ('via', 'AC')),
    ],
    'atco2_test-set-1h_LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395': [
        ('callsign OK-ELA', 'callsign', ('oscar kilo', 'ELA')),
        ('waypoint TB402', 'callsign', ('tango bravo', '402')),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444': [
        ('callsign CSA 1DZ', 'callsign', ('csa', '1DZ')),
        ('flight level 100', 'number', ('flight level', 100)),
        ('phrase "descend"', 'phrase', ('descend', ['climb', 'maintain'])),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934': [
        ('flight level 100  [ERROR CASE: mode "one on eight"]', 'number', ('flight level', 100)),
        ('callsign CSA 1DZ', 'callsign', ('csa', '1DZ')),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349': [
        ('callsign OK-HHH  [ERROR CASE: mode "kio hotel"]', 'callsign', ('oscar kilo', 'HHH')),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332': [
        ('callsign EUROWINGS 1TK', 'callsign', (['euro wings', 'eurowings'], '1TK')),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742': [
        ('callsign EUROWINGS 1TK', 'callsign', (['euro wings', 'eurowings'], '1TK')),
    ],
    'atco2_test-set-1h_LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212': [
        ('runway 24', 'number', ('runway', 24)),
    ],
}
# 34720N: the reference "via voz one hotel departure" -- the slot is the SID "one hotel"; anchor on the
# following word "departure" is not expressible with a prefix anchor, so use the SID as a suffix-class
# with no anchor (prefix-free) followed by the literal "departure".
SPECS['uwb-atcc_TWR-34720N_002001_002559_AT'] = [('SID "one hotel departure"', 'sid', ('1H', 'departure'))]


def build_slots(classes: ATCClasses, spec):
    label, kind, args = spec
    if kind == 'number': return label, classes.number_slot(*args)
    if kind == 'number_start': return label, classes.number_slot(args[0], args[1], at_start=True)
    if kind == 'callsign': return label, classes.callsign_slot(*args)
    if kind == 'freq': return label, classes.freq_slot(*args)
    if kind == 'phrase': return label, classes.phrase_slot(*args)
    if kind == 'sid':
        w = classes.wa; suffix, follow = args
        correct = w.compile(w.anywhere(NFA.seq(classes.seqs(suffix_tokenisations(suffix)), w.lit(follow))))
        like = w.compile(w.anywhere(NFA.seq(classes.SUFFIXLIKE, w.lit(follow))))
        competing = like.difference(correct); residual = correct.union(competing).complement()
        return label, (correct, competing, residual)
    raise ValueError(kind)
