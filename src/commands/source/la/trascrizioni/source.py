import os

from commands.source.entity_tagger import tag
from commands.source.la.trascrizioni.expected_source_files import \
    EXPECTED_SOURCE_FILES
from commands.source.la.trascrizioni.extractor import extract_raw_sources
from commands.source.latin_dictionary.decliner import resolve_nominative
from commands.source.source import (INFO_PNOUN_CLUSTER, Source, SourceCode,
                                    SourceOutcomeCode)
from db.entity import Entity
from db.labelled_db import DBLabel, DBWithLabel
from db.raw_source import RawSource
from utils.lambda_utils import flatmap, lmap
from utils.language_utils import load_forms_of

EXPECTED_DB_ENTRIES = len(EXPECTED_SOURCE_FILES)
UNKNOWN_LABEL = "UNKNOWN"


class TrascrizioniSource(Source):
    def __init__(self):
        self.db = DBWithLabel(DBLabel.LA)

    @staticmethod
    def base_path():
        return os.path.join(Source.base_path(), SourceCode.TRASCRIZIONI.value)

    def is_already_downloaded(self):
        if not os.path.exists(TrascrizioniSource.base_path()):
            return False
        expected_length = len(EXPECTED_SOURCE_FILES)
        files = os.listdir(TrascrizioniSource.base_path())
        return len(files) == expected_length and all(
            file in EXPECTED_SOURCE_FILES for file in files
        )

    def download(self):
        return SourceOutcomeCode.MANUAL_DOWNLOAD_REQUIRED

    def is_already_persisted(self):
        count = RawSource.count_source_elements_in_db(
            SourceCode.TRASCRIZIONI, self.db
        )
        print(f"Counted {count} persisted raw sources")
        return count == EXPECTED_DB_ENTRIES

    def persist(self):
        path = TrascrizioniSource.base_path()
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
                marked_items = lmap(
                    lambda info: {
                        "info": info,
                        "pnoun": raw_source.text[
                            info.start_index:info.end_index
                        ]
                    },
                    raw_source.get_info_by_type(INFO_PNOUN_CLUSTER),
                )

                for marked_item in marked_items:
                    pnoun = marked_item["pnoun"]
                    lemma = resolve_nominative(pnoun)
                    if not lemma:
                        lemma = pnoun
                    entity = Entity(lemma)
                    if not entity.exists_in(self.db):
                        labels = tag(lemma, self.db)
                        if labels:
                            entity.add_labels(labels)
                        else:
                            entity.add_labels([UNKNOWN_LABEL])

                        for f in load_forms_of(entity.lemma):
                            entity.add_variant_string(f)

                        print("Saving entity:", entity.to_string())
                        entity.persist(self.db)
                        entity.update_custom_label(
                            self.db, lemma, marked_item['info'].label)

                    else:
                        print(f"Entity {pnoun} already saved.")

                print("Saving raw source")
                raw_source.persist(self.db)
        return SourceOutcomeCode.PERSISTED

    def count(self):
        return RawSource.count_source_elements_in_db(
            SourceCode.TRASCRIZIONI, self.db
        )
