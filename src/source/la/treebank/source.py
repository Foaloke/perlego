import itertools
import os
import shutil
from functools import reduce

from git import Repo

from db.entity import Entity
from db.labelled_db import DBLabel, DBWithLabel
from db.raw_source import RawSource
from source.entity_tagger import tag
from source.entity_variants import get_abbreviations, get_variants
from source.la.treebank.extractor import extract_raw_sources
from source.la.treebank.pnoun_clusterer import PNOUN_CLUSTER_TYPE
from source.source import Source, SourceCode
from utils.file import delete_dir_if_exists
from utils.lambda_utils import flatmap, lmap

LATIN = "la"
TREEBANK_REPO = "https://github.com/PerseusDL/treebank_data.git"
EXPECTED_SOURCE_FILES = [
    "phi0448.phi001.perseus-lat1.tb.xml",
    "phi0474.phi013.perseus-lat1.tb.xml",
    "phi0620.phi001.perseus-lat1.tb.xml",
    "phi0631.phi001.perseus-lat1.tb.xml",
    "phi0690.phi003.perseus-lat1.tb.xml",
    "phi0959.phi006.perseus-lat1.tb.xml",
    "phi0972.phi001.perseus-lat1.xml",
    "phi0975.phi001.perseus-lat1.tb.xml",
    "phi1221.phi007.perseus-lat1.tb.xml",
    "phi1348.abo012.perseus-lat1.tb.xml",
    "phi1351.phi005.perseus-lat1.tb.xml",
    "tlg0031.tlg027.perseus-lat1.tb.xml",
]
EXPECTED_DB_ENTRIES = 12
UNKNOWN_LABEL = "UNKNOWN"


def is_valid_sentence(s):
    return (
        all(a in s.attrib for a in ["document_id", "subdoc"])
        and s.attrib["document_id"] != ""
        and s.attrib["subdoc"] != ""
    )


class TreebankSource(Source):
    def __init__(self):
        self.db = DBWithLabel(DBLabel.LA)

    @staticmethod
    def base_path():
        return os.path.join(Source.base_path(), SourceCode.TREEBANK.value)

    def is_already_downloaded(self):
        if not os.path.exists(TreebankSource.base_path()):
            return False
        expected_length = len(EXPECTED_SOURCE_FILES)
        files = os.listdir(TreebankSource.base_path())
        return len(files) == expected_length and all(
            file in EXPECTED_SOURCE_FILES for file in files
        )

    def download(self):
        git_path = os.path.join(TreebankSource.base_path(), "tmp_git")
        delete_dir_if_exists(git_path)

        Repo.clone_from(TREEBANK_REPO, git_path)
        git_texts_path = os.path.join(git_path, "v2.1", "Latin", "texts")
        for text_file in os.listdir(git_texts_path):
            file_path = os.path.join(git_texts_path, text_file)
            shutil.move(
                file_path, os.path.join(TreebankSource.base_path(), text_file)
            )

        delete_dir_if_exists(git_path)

    def is_already_persisted(self):
        count = RawSource.count_source_elements_in_db(
            SourceCode.TREEBANK, self.db
        )
        print(f"Counted {count} persisted raw sources")
        return count == EXPECTED_DB_ENTRIES

    def _cluster_forms_in_same_case(self, acc, curr):
        for c in curr:
            case_and_form, abbreviations = c
            case, form = case_and_form
            if case not in acc.keys():
                acc[case] = []
            forms = [form]
            forms.extend(abbreviations)
            acc[case].append(forms)
        return acc

    def _extract_forms_from_clusters(self, case_and_form, default_form):

        clusters_by_case = reduce(
            self._cluster_forms_in_same_case, case_and_form, {}
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

    def load_forms_of(self, entity):
        entity_tokens = entity.lemma.split(" ")

        case_and_form = []
        all_latin_abbreviations = get_abbreviations(LATIN)
        for i, entity_token in enumerate(entity_tokens):
            variants = get_variants(entity_token, LATIN)
            case_and_form.append([])
            entity_token_abbreviations = []
            if entity_token in all_latin_abbreviations.keys():
                entity_token_abbreviations = all_latin_abbreviations[
                    entity_token
                ]
            for v in variants:
                case_and_form[i].append((v, entity_token_abbreviations))

        forms = self._extract_forms_from_clusters(case_and_form, entity.lemma)

        return list(set(forms))

    def persist(self):
        path = TreebankSource.base_path()
        data_full_paths = list(
            map(lambda f: os.path.join(path, f), os.listdir(path))
        )
        raw_sources = flatmap(extract_raw_sources, data_full_paths)
        for raw_source in raw_sources:
            print(
                "\n\nExtracting entities from:"
                + f"\n```\n{raw_source.to_string()}\n\n```\n\n"
            )
            if not raw_source.exists_in(self.db):
                pnoun_cluster = raw_source.get_info_by_type(
                    PNOUN_CLUSTER_TYPE
                )
                for pnoun in pnoun_cluster:
                    entity = Entity(pnoun.label)
                    if not entity.exists_in(self.db):
                        labels = tag(pnoun.label, LATIN, self.db)
                        if labels:
                            entity.add_labels(labels)
                        else:
                            entity.add_labels([UNKNOWN_LABEL])

                        for f in self.load_forms_of(entity):
                            entity.add_variant_string(f)

                        print("Saving entity:", entity.to_string())
                        entity.persist(self.db)

                    else:
                        print(f"Entity {pnoun.label} already saved")

                print("Saving raw source")
                raw_source.persist(self.db)

    def count(self):
        return RawSource.count_source_elements_in_db(
            SourceCode.TREEBANK, self.db
        )
