import requests
from unidecode import unidecode

from commands.source.wiki_tagger.codes import AMBIGUOUS
from commands.source.wiki_tagger.db.wikidata_entity import WikiDataInfo
from commands.source.wiki_tagger.exceptions import WikiException
from db.labelled_db import DBLabel, DBWithLabel
from utils.lambda_utils import lmap
from utils.language_utils import LATIN

LABEL_LANGUAGE = "en"
WIKIDATA_API_URL = "https://www.wikidata.org/wiki/Special:EntityData/"
INSTANCE_WIKIDATA_ID = "P31"
WIKIPEDIA_DISAMBIGUATION_ID = "Q2054125"
WIKIPEDIA_DISAMBIGUATION_INSTANCE_ID = "Q4167410"
ERROR_ID = "ERROR_ID"

db = DBWithLabel(DBLabel.WIKI_INFO)


def extract_wiki_id(wiki_info):
    try:
        return next(
            p for p in wiki_info["properties"] if p["name"] == "wikibase_item"
        )["*"]
    except Exception:
        return None


def build_wikipedia_api_url(language_code):
    return f"https://{language_code}.wikipedia.org/w/api.php"


def build_wikidata_api_url():
    return "https://www.wikidata.org/w/api.php"


def is_redirect_result(res):
    return (
        len(res["parse"]["links"]) == 1 and len(res["parse"]["iwlinks"]) == 0
    )


def filter_instances(instances):
    return [
        i
        for i in instances
        if i["id"] != WIKIPEDIA_DISAMBIGUATION_INSTANCE_ID
    ]


def get_instances_from_page_id(page_id, language_code):
    url = build_wikipedia_api_url(language_code)
    params = {"action": "parse", "pageid": page_id, "format": "json"}
    print("Resolving search result: ", page_id, ". Requesting", url, params)
    res = requests.get(url, params).json()
    wiki_id = extract_wiki_id(res["parse"])
    if not wiki_id:
        print("WIKI ID NOT FOUND", res)
        return []
    return get_wikidata_instances(wiki_id)


def wikipedia_api_search(lemma, language_code):
    url = build_wikipedia_api_url(language_code)
    params = {
        "action": "query",
        "list": "search",
        "srsearch": unidecode(lemma),
        "format": "json",
    }
    print("Wikipedia Search: ", unidecode(lemma), ". Requesting", url, params)
    res = requests.get(url, params).json()
    matches = res["query"]["search"]
    if not matches:
        raise WikiException(
            AMBIGUOUS, Exception("Cannot disambiguate the term " + lemma)
        )

    instances = []
    for match in matches:
        instances.extend(
            get_instances_from_page_id(match["pageid"], language_code)
        )

    return filter_instances(instances)


def wikidata_api_search(lemma, language_code):
    url = build_wikidata_api_url()
    params = {
        "action": "wbsearchentities",
        "search": unidecode(lemma),
        "language": language_code,
        "format": "json",
    }
    print("Wikidata Search: ", unidecode(lemma), ". Requesting", url, params)
    res = requests.get(url, params).json()
    matches = res["search"]
    instances = []
    for match in matches:
        instances.extend(get_wikidata_instances(match["id"]))

    return filter_instances(instances)


def get_wikidata_info(wiki_id):
    url = f"{WIKIDATA_API_URL}{wiki_id}"

    def resolver(id):
        print("Requesting", url)
        return requests.get(url).json()["entities"][id]

    if db:
        return WikiDataInfo.load(db, wiki_id, resolver)

    return resolver(wiki_id)


def get_wikidata_instances(wiki_id):
    wikidata_info = get_wikidata_info(wiki_id)
    if INSTANCE_WIKIDATA_ID not in wikidata_info["claims"].keys():
        return []

    instances = lmap(
        lambda i: get_wiki_property_info(
            i["mainsnak"]["datavalue"]["value"]["id"]
        ),
        wikidata_info["claims"][INSTANCE_WIKIDATA_ID],
    )

    # Some instance may be null if wiki property info returns None
    return [i for i in instances if i]


def get_wiki_property_info(wiki_id):
    wiki_property_info = get_wikidata_info(wiki_id)
    if LABEL_LANGUAGE not in wiki_property_info["labels"].keys():
        print(
            f"Cannot find labels in {LABEL_LANGUAGE}."
            + f" Available labels are {wiki_property_info['labels'].keys()}"
        )
        return None
    info = wiki_property_info["labels"][LABEL_LANGUAGE]
    info["id"] = wiki_property_info["id"]
    return info


def tag(lemma):
    try:
        instances = []
        instances.extend(wikidata_api_search(lemma, LATIN))
        instances.extend(wikipedia_api_search(lemma, LATIN))
        tags = list(set(lmap(lambda i: i["value"], instances)))
        return tags
    except WikiException as e:
        print("Exception Occurred", e)
        return None
