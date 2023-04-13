import os
import shutil

from git import Repo

from commands.source.entity_tagger import tag
from commands.source.la.treebank.expected_source_files import \
    EXPECTED_SOURCE_FILES
from commands.source.la.treebank.extractor import extract_raw_sources
from commands.source.source import (INFO_PNOUN_CLUSTER, Source, SourceCode,
                                    SourceOutcomeCode)
from db.entity import Entity
from db.labelled_db import DBLabel, DBWithLabel
from db.raw_source import RawSource
from utils.file import delete_dir_if_exists
from utils.lambda_utils import flatmap
from utils.language_utils import load_forms_of

TREEBANK_REPO = "https://github.com/PerseusDL/treebank_data.git"
EXPECTED_DB_ENTRIES = len(EXPECTED_SOURCE_FILES)
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
        return SourceOutcomeCode.DOWNLOADED

    def is_already_persisted(self):
        count = RawSource.count_source_elements_in_db(
            SourceCode.TREEBANK, self.db
        )
        print(f"Counted {count} persisted raw sources")
        return count == EXPECTED_DB_ENTRIES

    def persist(self):
        path = TreebankSource.base_path()
        data_full_paths = list(
            map(lambda f: os.path.join(path, f), os.listdir(path))
        )
        raw_sources = flatmap(extract_raw_sources, data_full_paths)
        already_persisted_index = max(self.count() - 1, 0)
        for raw_source in raw_sources[already_persisted_index:]:
            print(
                "\n\nExtracting entities from:"
                + f"\n```\n{raw_source.to_string()}\n\n```\n\n"
            )
            if not raw_source.exists_in(self.db):
                pnoun_cluster = raw_source.get_info_by_type(
                    INFO_PNOUN_CLUSTER
                )
                for pnoun in pnoun_cluster:
                    entity = Entity(pnoun.label)
                    if not entity.exists_in(self.db):
                        labels = tag(pnoun.label, self.db)
                        if labels:
                            entity.add_labels(labels)
                        else:
                            entity.add_labels([UNKNOWN_LABEL])

                        for f in load_forms_of(entity.lemma):
                            entity.add_variant_string(f)

                        print("Saving entity:", entity.to_string())
                        entity.persist(self.db)

                    else:
                        print(f"Entity {pnoun.label} already saved")

                print("Saving raw source")
                raw_source.persist(self.db)
        return SourceOutcomeCode.PERSISTED

    def count(self):
        return RawSource.count_source_elements_in_db(
            SourceCode.TREEBANK, self.db
        )

    def get_all_ents(self):
        returned_ents = []
        all_ents = Entity.load_all(self.db)
        for e in all_ents:
            returned_ents.append({"lemma": e["lemma"], "labels": e["labels"]})
        return returned_ents

    def get_all_raw_sources(self):
        return RawSource.load_all(self.db)

    def load_entity_data_of_lemma(self, lemma):
        return Entity.get_lemma_and_variants_for_string(lemma, self.db)

    def add_entity_custom_label(self, lemma, custom_label):
        Entity.update_custom_label(self.db, lemma, custom_label)
