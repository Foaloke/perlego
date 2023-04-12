from commands.source.latin_dictionary.decliner import (
    ABBREVIATIONS as LATIN_ABBREVIATIONS,
)
from commands.source.latin_dictionary.decliner import (
    load_forms as latin_dictionary_get_variants,
)


def get_variants(string):
    return latin_dictionary_get_variants(string)


def get_abbreviations():
    return LATIN_ABBREVIATIONS
