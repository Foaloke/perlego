from source.latin_dictionary.decliner import (
    ABBREVIATIONS as LATIN_ABBREVIATIONS,
)
from source.latin_dictionary.decliner import (
    load_forms as latin_dictionary_get_variants,
)


def get_variants(string, language):
    if language == "la":
        return latin_dictionary_get_variants(string)
    raise Exception(f"Language {language} is not supported")


def get_abbreviations(language):
    if language == "la":
        return LATIN_ABBREVIATIONS
    raise Exception(f"Language {language} is not supported")
