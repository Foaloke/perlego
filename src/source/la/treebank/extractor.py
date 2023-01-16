import xml.etree.ElementTree as ET

from db.raw_source import RawSource, SourceCode
from source.la.treebank.converter import print_word, to_dict
from source.la.treebank.pnoun_clusterer import (
    PNOUN_CLUSTER_TYPE,
    cluster_pnouns,
)
from utils.lambda_utils import lmap


def is_valid_sentence(s):
    return (
        all(a in s.attrib for a in ["document_id", "subdoc"])
        and s.attrib["document_id"] != ""
        and s.attrib["subdoc"] != ""
    )


def comes_after_space(w):
    # Punctuation or suffixed conjunction are not preceded by space
    return not (w["postag"] == "u--------" or w["form"] == "-que")


def extract_raw_sources(data_file):
    sentences = ET.parse(data_file).getroot().findall("body/sentence")
    valid_sentences = [s for s in sentences if is_valid_sentence(s)]
    raw_sources = []
    for s in valid_sentences:
        words_in_sentence = [
            w for w in s.findall("word") if "lemma" in w.attrib
        ]
        words = lmap(to_dict, words_in_sentence)
        words_and_spaces = []
        for index, w in enumerate(words):
            w["space"] = False  # Init space to false

            # If we are not at the very beginning of a sentence
            if words_and_spaces != []:
                # Change space of previous token,
                # if you notice the current token should be preceded by space
                words_and_spaces[index - 1]["space"] = comes_after_space(w)

            words_and_spaces.append(w)

        text = "".join(lmap(print_word, words_and_spaces))
        raw_source = RawSource(SourceCode.TREEBANK, text)

        # Convert all the info, and add indexes to the words
        word_index = 0
        for w in words:
            start_index = word_index
            end_index = word_index + len(w["form"])
            w["start_index"] = start_index
            w["end_index"] = end_index
            if w["space"]:
                end_index = end_index + 1
            for info_label in w.keys():
                raw_source.add_info(
                    start_index, end_index, info_label, w[info_label]
                )
            word_index = end_index

        # Cluster pnouns
        for cluster in cluster_pnouns(words):
            raw_source.add_info(
                cluster["start_index"],
                cluster["end_index"],
                PNOUN_CLUSTER_TYPE,
                cluster["label"],
            )
        raw_sources.append(raw_source)
    return raw_sources
