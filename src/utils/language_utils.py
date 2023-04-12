import itertools
from functools import reduce

import spacy_stanza
import stanza

from commands.source.entity_variants import get_abbreviations, get_variants
from utils.lambda_utils import lmap

LATIN = "la"


def load_latin():
    stanza.download(LATIN)
    nlp = spacy_stanza.load_pipeline("xx", lang=LATIN)
    return nlp


def _cluster_forms_in_same_case(acc, curr):
    for c in curr:
        case_and_form, abbreviations = c
        case, form = case_and_form
        if case not in acc.keys():
            acc[case] = []
        forms = [form]
        forms.extend(abbreviations)
        acc[case].append(forms)
    return acc


def _extract_forms_from_clusters(case_and_form, default_form):

    clusters_by_case = reduce(
        _cluster_forms_in_same_case, case_and_form, {}
    ).values()

    if len(clusters_by_case) == 0:
        print(f"No form found for {default_form}")
        forms = [default_form]
    else:
        # Keep only long clusters
        # (smaller ones are caused by
        #  dangling or umatched fem/masc sing/plural)
        max_len = max(lmap(len, clusters_by_case))
        forms = []
        for c in clusters_by_case:
            if len(c) == max_len:
                forms.extend(lmap(" ".join, list(itertools.product(*c))))

    return forms


def load_forms_of(entity_lemma):
    entity_tokens = entity_lemma.split(" ")

    case_and_form = []
    all_latin_abbreviations = get_abbreviations()
    for i, entity_token in enumerate(entity_tokens):
        variants = get_variants(entity_token)
        case_and_form.append([])
        entity_token_abbreviations = []
        if entity_token in all_latin_abbreviations.keys():
            entity_token_abbreviations = all_latin_abbreviations[entity_token]
        for v in variants:
            case_and_form[i].append((v, entity_token_abbreviations))

    forms = _extract_forms_from_clusters(case_and_form, entity_lemma)

    return list(set(forms))
