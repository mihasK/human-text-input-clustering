from rapidfuzz import fuzz
from rapidfuzz.process import extractOne, extract




import unicodedata, string
import unidecode, re
from unidecode import unidecode

def rem_punctuation(x):
    return x.translate(str.maketrans('', '', string.punctuation))

def normalize(s):
#     return unicodedata.normalize('NFKD', s)
    return unidecode(s)

def rem_extra_spaces(s):
    s = re.sub('  +', ' ', s)
    s = re.sub('\n', ' ', s)
    s = re.sub('\t', ' ', s)
    return s

    
def preprocess(x):
    if not x:
        return ''
    
    x = rem_punctuation(x)
    x = rem_extra_spaces(x)
    x = normalize(x)
    x = x.lower()
    x = x.strip()
    return x or ''



fuzz_funcs = {
    'QRatio': fuzz.QRatio,
    'token_ratio': fuzz.token_ratio,
    'partial_ratio': fuzz.token_ratio,
    'token_set_ratio': fuzz.token_set_ratio,
    'token_sort_ratio': fuzz.token_sort_ratio,
}