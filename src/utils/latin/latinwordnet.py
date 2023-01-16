import requests

from db.entity import Entity

LATIN_WORD_NET_URL = "https://latinwordnet.exeter.ac.uk/lemmatize"


class LatinWordNetException(Exception):
    def __init__(self, code):
        super().__init__(code)


def get_lemma_from_variant(variant, db):
    # If already persisted, return it
    lemma, variants = Entity.get_lemma_and_variants_for_string(variant, db)
    if lemma and variants:
        return lemma

    # Otherwise, make a request
    url = f"{LATIN_WORD_NET_URL}/{variant}/"
    print(f"Requesting {variant} from latinwordnet.exeter.ac.uk")
    res = requests.get(url).json()

    if len(res) == 0:
        return None
    else:
        return res[0]["lemma"]["lemma"]
