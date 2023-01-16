import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from utils.lambda_utils import flatmap, lmap

SUFFIX = "que"
ONLINE_LATIN_DICTIONARY_URL = (
    "https://www.online-latin-dictionary.com/latin-dictionary-flexion.php"
)


def _is(needle):
    def _matches(hay):
        if not hay:
            return False
        return hay == needle

    return _matches


def search_variant(soup_row):
    radice = soup_row.find(class_=_is("radice"))
    desinenza = soup_row.find(class_=_is("desinenza"))
    if not radice:
        return None
    desinenza_text = ""
    if desinenza:
        desinenza_text = desinenza.getText()
    return radice.getText() + desinenza_text


def extract_variants(soup_table):
    return filter(
        lambda f: f, lmap(search_variant, soup_table.find_all("tr"))
    )


def extract_lemma_of_variant_from_a(variant, soup_a):
    href = soup_a["href"]
    text = soup_a.getText()
    if (not variant.casefold() == text.casefold()) and (
        "latin-dictionary-flexion.php?lemma" in href
    ):
        return [soup_a.getText()]
    else:
        return []


def search(string):
    url = ONLINE_LATIN_DICTIONARY_URL
    params = {"parola": string}
    print("Requesting", url, params)
    res = requests.get(url, params)
    soup = BeautifulSoup(res.text, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    return soup


def load_variants(lemma):
    return flatmap(
        extract_variants, search(lemma).find_all(class_=_is("span_1_of_2"))
    )


def resolve_lemma(variant):
    # May be already lemma
    variants = load_variants(variant)
    if variants:
        print(
            "The variant",
            unidecode(variant),
            "is already lemma with variants",
            ", ".join(lmap(unidecode, variants)),
        )
        return variants[0]
    # Otherwise lookup
    possible_lemmas = flatmap(
        lambda soup_a: extract_lemma_of_variant_from_a(variant, soup_a),
        search(variant).find_all("a", href=True),
    )
    possible_lemmas = list(dict.fromkeys(possible_lemmas))
    if not possible_lemmas:
        return None
    return possible_lemmas[0]


def get_lemma_and_variants_for_string(string):
    string = string.removesuffix(SUFFIX)

    lemma = resolve_lemma(string)
    if not lemma:
        return None, None

    variants = load_variants(lemma)

    if not variants:
        return lemma, None

    return lemma, variants
