from typing import Optional, Tuple
import unicodedata
from sastadev.lexicon import known_word

validwords = {"z'n", 'dees', 'cool', 'ok', 'zoiets'}
validnameparts = {}
punctuationsymbols = """.,?!:;"'“”›"""

# add numerals
numerals = {}

def isvalidword(w: str) -> bool:
    '''
    function to determine whether a word is a valid Dutch word
    :param w:
    :return: bool
    '''
    result, _ = isvalidwordandfoundas(w)
    return result

def isvalidwordandfoundas(w: str) -> Tuple[bool, Optional[str]]:
    '''
    function to determine whether a word is a valid Dutch word and
    if so, to return the form in which it has been found in the lexicon (other wise None)
    :param w: str
    :return: Tuple[bool, Optional[str]]
    '''

    if known_word(w):
        return True, w
    elif w in punctuationsymbols:
        return True, w
    elif w in validwords:
        return True, w
    elif w in numerals:
        return True, w
    else:
        # Check if the word has accents and try without accents
        normalized_word = ''.join(char for char in unicodedata.normalize('NFD', w) if unicodedata.category(char) != 'Mn')
        if known_word(normalized_word):
            return True, normalized_word

        # Try capitalizing the first letter and check again
        capitalized_word = w.capitalize()
        if known_word(capitalized_word):
            return True, capitalized_word

        #try lowercase variant
        lowerword = w.lower()
        if known_word(lowerword):
            return True, lowerword

    return False, None

