import os
from pathlib import Path

from spacy.cli.init_config import fill_config
from spacy.cli.train import train
from spacy.tokens import DocBin

from db.entity import Entity
from db.labelled_db import DBLabel, DBTableName, DBWithLabel
from train.train import TrainOutcomeCode
from utils.language_loader import load_latin

SPACY_DATA_PATH = os.path.join("data", "spacy")
if not os.path.isdir(SPACY_DATA_PATH):
    os.makedirs(SPACY_DATA_PATH)

SPACY_DEV_DATA_PATH = os.path.join(SPACY_DATA_PATH, "dev.spacy")
SPACY_TRAIN_DATA_PATH = os.path.join(SPACY_DATA_PATH, "train.spacy")

SPACY_BASE_CONFIG_DATA_PATH = os.path.join(SPACY_DATA_PATH, "base_config.cfg")
SPACY_CONFIG_DATA_PATH = os.path.join(SPACY_DATA_PATH, "config.cfg")
SPACY_MODEL_PATH = os.path.join(SPACY_DATA_PATH, "model")


def entity_training_prepare(language, dev_size, limit):

    codes = []
    nlp = None
    db = None
    saved_entries_for_language = None
    if language == "la":
        nlp = load_latin()
        db = DBWithLabel(DBLabel.LA)
        saved_entries_for_language = db.load_all(DBTableName.RAW_SOURCE)

    if not saved_entries_for_language:
        codes.append(TrainOutcomeCode.NO_DATA_FOR_LANGUAGE)
        return codes

    dev_doc_bin = DocBin()
    train_doc_bin = DocBin()
    current_size = 0
    if limit is not None:
        saved_entries_for_language = list(saved_entries_for_language)[:limit]
    total_size = len(saved_entries_for_language)

    dev_doc_bin_size = total_size * dev_size
    for entry in saved_entries_for_language:
        text = entry["text"]
        doc = nlp.make_doc(text)
        ents = []
        for pnoun_cluster in [
            info for info in entry["info"] if info["type"] == "pnoun_cluster"
        ]:
            start = pnoun_cluster["start_index"]
            end = pnoun_cluster["end_index"]
            entity = Entity.get_lemma_and_variants_for_string(
                pnoun_cluster["label"], db
            )
            if not entity:
                print(f"Entity {pnoun_cluster['label']} was not found")
            elif not entity.custom_label:
                print(
                    f"Skipping entity {entity.lemma} as it has no custom label"
                )
            else:
                span = doc.char_span(
                    start,
                    end,
                    label=entity.custom_label,
                    alignment_mode="contract",
                )
                if not span:
                    print(
                        f"Skipping entity '{entity.lemma}'"
                        + " as Spacy doc span creation failed"
                        + f" ({pnoun_cluster['start_index']},"
                        + f" {pnoun_cluster['end_index']})"
                        + f" ({pnoun_cluster['label']})"
                    )
                else:
                    ents.append(span)
        doc.ents = ents
        if current_size <= dev_doc_bin_size:
            dev_doc_bin.add(doc)
        else:
            train_doc_bin.add(doc)
        current_size += 1
        print("\r", f"PROGRESS --> {current_size}/{total_size}", end="\r")

    print("\r", "DONE", end="\r")

    dev_doc_bin.to_disk(SPACY_DEV_DATA_PATH)
    train_doc_bin.to_disk(SPACY_TRAIN_DATA_PATH)

    return codes


def entity_training_execute():
    codes = []
    fill_config(
        Path(SPACY_CONFIG_DATA_PATH), Path(SPACY_BASE_CONFIG_DATA_PATH)
    )
    train(
        Path(SPACY_CONFIG_DATA_PATH),
        Path(SPACY_MODEL_PATH),
        overrides={
            "paths.train": SPACY_TRAIN_DATA_PATH,
            "paths.dev": SPACY_DEV_DATA_PATH,
        },
    )
    return codes
