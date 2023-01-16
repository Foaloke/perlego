import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from utils.lambda_utils import flatmap, lmap

SUFFIX = "que"

ABBREVIATIONS = {
    "Agrippa": ["Agr."],
    "Appia": ["Ap."],
    "Appius": ["Ap."],
    "Arruns": ["Ar."],
    "Aula": ["A."],
    "Aule": ["A."],
    "Aulus": ["A."],
    "Cae": ["C."],
    "Caeso": ["K."],
    "Cneve": ["Cn."],
    "Decima": ["D."],
    "Decimus": ["D."],
    "Fasti": ["F."],
    "Fausta": ["F."],
    "Faustus": ["F."],
    "Gaia": ["C."],
    "Gaius": ["C."],
    "Gnaea": ["Cn."],
    "Gnaeus": ["Cn."],
    "Hasti": ["H."],
    "Hosta": ["H."],
    "Laris": ["Lr."],
    "Larth": ["La.", "Lth."],
    "Lucia": ["L."],
    "Lucie": ["L."],
    "Lucius": ["L."],
    "Maio": ["Mai."],
    "Mamarce": ["Mam."],
    "Mamerca": ["Mam."],
    "Mamercus": ["Mam."],
    "Mania": ["M'."],
    "Manius": ["ꟿ.", "M'."],
    "Marce": ["M."],
    "Marcia": ["M."],
    "Marcus": ["M."],
    "Mino": ["Min."],
    "Numeria": ["N."],
    "Numerius": ["N."],
    "Octavia": ["Oct."],
    "Octavius": ["Oct."],
    "Opiter": ["Opet."],
    "Postuma": ["Post."],
    "Postumus": ["Post."],
    "Procula": ["Pro."],
    "Proculus": ["Pro."],
    "Publia": ["P."],
    "Publius": ["P."],
    "Puplie": ["P."],
    "Quinta": ["Q."],
    "Quintus": ["Q."],
    "Ramtha": ["R."],
    "Secunda": ["Seq."],
    "Sertor": ["Sert."],
    "Servia": ["Ser."],
    "Servius": ["Ser."],
    "Sethre": ["Se."],
    "Sexta": ["Sex."],
    "Sextus": ["Sex."],
    "Spuria": ["Sp."],
    "Spurie": ["S."],
    "Spurius": ["S.", "Sp."],
    "Statia": ["St."],
    "Statius": ["St."],
    "Tanaquil": ["Thx."],
    "Thana": ["Th."],
    "Tiberia": ["Ti."],
    "Tiberius": ["Ti."],
    "Tite": ["T."],
    "Titia": ["T."],
    "Titus": ["T."],
    "Vel": ["Vl."],
    "Velthur": ["Vth."],
    "Vibia": ["V."],
    "Vibius": ["V."],
    "Vipie": ["V."],
    "Volesus": ["Vol."],
    "Volusa": ["Vol."],
    "Vopisca": ["Vop."],
    "Vopiscus": ["Vop."],
}


def _is(needle):
    def _matches(hay):
        if not hay:
            return False
        return hay == needle

    return _matches


def _is_not(*needles):
    def _does_not_match(hay):
        if not hay:
            return True
        return hay not in needles

    return _does_not_match


def get_gender_cell(soup_row):
    gender_row = soup_row.parent.parent.parent.find_previous_sibling("table")
    gender_cell = gender_row.find_all("td")[0]
    return gender_cell


def get_singular_plural_row(soup_row):
    parent = soup_row.parent
    first_row = parent.find_all("tr")[0]
    return first_row


def search_form(soup_row):
    form = soup_row.find(class_=_is_not("radice", "desinenza"))
    radice = soup_row.find(class_=_is("radice"))
    desinenza = soup_row.find(class_=_is("desinenza"))
    if not radice:
        return None
    singular_plural_row = get_singular_plural_row(soup_row)
    gender_cell = get_gender_cell(soup_row)
    form_text = (
        form.getText() + singular_plural_row.getText() + gender_cell.getText()
    )
    radice_text = radice.getText()
    desinenza_text = ""
    if desinenza:
        desinenza_text = desinenza.getText()

    return form_text, radice_text + desinenza_text


def extract_forms(soup_table):
    return filter(lambda f: f, lmap(search_form, soup_table.find_all("tr")))


def extract_nominative_of_form_from_a(form, soup_a):
    href = soup_a["href"]
    text = soup_a.getText()
    if (not form.casefold() == text.casefold()) and (
        "latin-dictionary-flexion.php?lemma" in href
    ):
        return [soup_a.getText()]
    else:
        return []


def search(string):
    url = (
        "https://www.online-latin-dictionary.com/latin-dictionary-flexion.php"
    )
    params = {"parola": string}
    print("Requesting", url, params)
    res = requests.get(url, params)
    soup = BeautifulSoup(res.text, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    return soup


def abbreviate(nominative):
    if nominative in ABBREVIATIONS.keys():
        return ABBREVIATIONS[nominative]
    return []


def load_forms(nominative):
    try:
        return flatmap(
            extract_forms,
            search(nominative).find_all(class_=_is("span_1_of_2")),
        )
    except Exception as e:
        print(
            f"An error occurred while retrieving the forms for {nominative}",
            e,
        )
        return []


def resolve_nominative(form):
    # May be already nominative
    forms = load_forms(form)
    if forms:
        print(
            "The form",
            unidecode(form),
            "is already nominative with forms",
            ", ".join(lmap(unidecode, forms)),
        )
        _, resolved_form = forms[0]
        return resolved_form
    # Otherwise lookup
    possible_nominatives = flatmap(
        lambda soup_a: extract_nominative_of_form_from_a(form, soup_a),
        search(form).find_all("a", href=True),
    )
    possible_nominatives = list(dict.fromkeys(possible_nominatives))
    if possible_nominatives:
        return possible_nominatives[0]
    return None


def resolve_form(form):
    form = form.removesuffix(SUFFIX)

    nominative = resolve_nominative(form)
    if not nominative:
        raise Exception(f"Could not find nominative for form {form}")
    forms = load_forms(nominative)

    if not forms:
        print("No form found for", form)

    return nominative
