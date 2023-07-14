from rapidfuzz import fuzz
from rapidfuzz.process import extractOne, extract




fuzz_funcs = {
    'QRatio': lambda s1,s2, score_cutoff: fuzz.QRatio(s1, s2, score_cutoff=score_cutoff),
    'token_ratio': lambda s1,s2, score_cutoff: fuzz.token_ratio(s1, s2, score_cutoff=score_cutoff),
}