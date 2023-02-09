import spacy_stanza
import stanza


def load_latin():
    stanza.download("la")
    nlp = spacy_stanza.load_pipeline("xx", lang="la")
    return nlp
