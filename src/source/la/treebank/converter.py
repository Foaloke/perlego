import string

from utils.lambda_utils import lmap

# ** Spacy format **
#
# TEXT: The original word text.
# LEMMA: The base form of the word.
# POS: The simple UPOS part-of-speech tag.
# TAG: The detailed part-of-speech tag.
# DEP: Syntactic dependency, i.e. the relation between tokens.
# SHAPE: The word shape – capitalization, punctuation, digits.
# ALPHA: Is the token an alpha character?
# STOP: Is the token part of a stop list,
#  i.e. the most common words of the language?
#
# e.g. Apple	apple	PROPN	NNP	nsubj	Xxxxx	True	False
SPACY_BLANK = {
    "TEXT": "",
    "LEMMA": "",
    "POS": "",
    "TAG": "",
    "SHAPE": "",
    "STOP": False,
    "ALPHA": False,
}


def is_pnoun(lemma, form, postag):
    if (not postag) or (not lemma):
        return False
    part_of_speech = postag[0]
    if part_of_speech == "n":
        if lemma[0].isupper():
            # We consider single uppercase letters
            # with an uppercase lemma to be symbols
            # as they are symbols representing a proper noun
            return True
    return False


def to_pos(w):
    # We consider 'non' only as a latin particle
    if w.attrib["lemma"] == "non":
        return "PART"

    # We consider emphasising particles as 'other'
    if w.attrib["relation"] == "AuxZ":
        return "OTHER"

    postag = w.attrib["postag"]
    part_of_speech = postag[0]

    # n   noun
    if part_of_speech == "n":
        # We consider single uppercase letters
        # with an uppercase lemma to be symbols
        # as they are symbols representing a proper noun
        w_is_pnoun = is_pnoun(
            w.attrib["lemma"], w.attrib["form"], w.attrib["postag"]
        )
        if w_is_pnoun:
            if len(w.attrib["form"]) == 1:
                return "SYM"
            else:
                return "PROPN"
        else:
            return "NOUN"
    # v   verb
    if part_of_speech == "v":
        if w.attrib["relation"] == "AuxV":
            return "CCONJ"
        else:
            return "VERB"
    # a   adjective
    if part_of_speech == "a":
        return "ADJ"
    # d   adverb
    if part_of_speech == "d":
        return "ADV"
    # c   conjunction
    if part_of_speech == "c":
        if w.attrib["relation"] == "COORD":
            return "AUX"
        else:
            return "SCONJ"
    # r   adposition
    if part_of_speech == "r":
        return "ADP"
    # p   pronoun
    if part_of_speech == "p":
        if w.attrib["relation"] == "ATR":
            return "DET"
        else:
            return "PRON"
    # m   numeral
    if part_of_speech == "m":
        return "NUM"
    # i   interjection
    if part_of_speech == "i":
        return "INTJ"
    # e   exclamation
    if part_of_speech == "e":
        return "INTJ"
    # u   punctuation
    if part_of_speech == "u":
        return "PUNCT"

    return None


def char_shape(letter):
    if not letter.isalpha():
        return letter
    if letter.isupper():
        return "X"
    else:
        return "x"


def to_shape(w):
    return "".join(lmap(char_shape, w.attrib["form"]))


def is_stop_word(w):
    return w.attrib["form"] in [
        "ab",
        "ac",
        "ad",
        "adhic",
        "aliqui",
        "aliquis",
        "an",
        "ante",
        "apud",
        "at",
        "atque",
        "aut",
        "autem",
        "cum",
        "cur",
        "de",
        "deinde",
        "dum",
        "ego",
        "enim",
        "ergo",
        "es",
        "est",
        "et",
        "etiam",
        "etsi",
        "ex",
        "fio",
        "haud",
        "hic",
        "iam",
        "idem",
        "igitur",
        "ille",
        "in",
        "infra",
        "inter",
        "interim",
        "ipse",
        "is",
        "ita",
        "magis",
        "modo",
        "mox",
        "nam",
        "ne",
        "nec",
        "necque",
        "neque",
        "nisi",
        "non",
        "nos",
        "o",
        "ob",
        "per",
        "possum",
        "post",
        "pro",
        "quae",
        "quam",
        "quare",
        "qui",
        "quia",
        "quicumque",
        "quidem",
        "quilibet",
        "quis",
        "quisnam",
        "quisquam",
        "quisque",
        "quisquis",
        "quo",
        "quoniam",
        "sed",
        "si",
        "sic",
        "sive",
        "sub",
        "sui",
        "sum",
        "super",
        "suus",
        "tam",
        "tamen",
        "trans",
        "tu",
        "tum",
        "ubi",
        "uel",
        "uero",
        "unus",
        "ut",
    ]


def is_alpha_word(w):
    return w.attrib["postag"][0] not in ["m", "i", "e", "u"]


def print_word(w, as_lemma=False):
    value_to_print = w["form"]
    if as_lemma:
        value_to_print = "".join(
            i
            for i in w["lemma"]
            if (
                not i.isdigit()
                and (i not in string.punctuation)
                and not w["lemma"].startswith("PERIOD")
            )
        )
    if w["space"]:
        return f"{value_to_print} "
    return value_to_print


# <word
#  id='1'
#  form='Cum'
#  lemma='cum'
#  postag='c--------'
#  relation='AuxC'
#  cite='urn:cts:latinLit:phi0448.phi001:2.1'
#  head='21'/>
def to_spacy_format(w):
    if (
        not w.attrib["postag"]
        or not w.attrib["form"]
        or not w.attrib["lemma"]
    ):
        return SPACY_BLANK

    pos = to_pos(w)
    if not pos:
        return SPACY_BLANK

    return {
        "TEXT": w.attrib["form"],
        "LEMMA": w.attrib["lemma"],
        "POS": to_pos(w),
        "TAG": w.attrib["postag"],
        "SHAPE": to_shape(w),
        "STOP": is_stop_word(w),
        "ALPHA": is_alpha_word(w),
    }


# <word
#  id='1'
#  form='Cum'
#  lemma='cum'
#  postag='c--------'
#  relation='AuxC'
#  cite='urn:cts:latinLit:phi0448.phi001:2.1'
#  head='21'/>
def to_dict(w):
    return {
        "index": w.attrib["id"],
        "form": w.attrib["form"],
        "lemma": w.attrib["lemma"],
        "postag": w.attrib["postag"],
        "relation": w.attrib["relation"],
        "head_index": w.attrib["head"],
    }
