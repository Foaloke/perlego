import os
from functools import partial
from pathlib import Path
from typing import Callable, Iterable

import spacy
from spacy.cli.init_config import fill_config
from spacy.cli.train import train
from spacy.language import Language
from spacy.tokens import Doc, DocBin
from spacy.training import Example

from commands.source.source import INFO_PNOUN_CLUSTER
# make the config work
from commands.train.spacy.rel_model import \
    create_classification_layer  # noqa: F401
from commands.train.spacy.rel_model import create_instances  # noqa: F401
from commands.train.spacy.rel_model import create_relation_model  # noqa: F401
from commands.train.spacy.rel_model import create_tensors  # noqa: F401
# make the factory work
from commands.train.spacy.rel_pipe import make_relation_extractor  # noqa: F401
from commands.train.train_codes import TrainOutcomeCode
from db.entity import Entity
from db.labelled_db import DBLabel, DBTableName, DBWithLabel
from utils.language_utils import load_latin

SPACY_DATA_PATH = os.path.join("data", "spacy")
if not os.path.isdir(SPACY_DATA_PATH):
    os.makedirs(SPACY_DATA_PATH)

SPACY_DEV_DATA_PATH = os.path.join(SPACY_DATA_PATH, "dev.spacy")
SPACY_TRAIN_DATA_PATH = os.path.join(SPACY_DATA_PATH, "train.spacy")

SPACY_BASE_CONFIG_DATA_PATH = os.path.join(SPACY_DATA_PATH, "base_config.cfg")
SPACY_CONFIG_DATA_PATH = os.path.join(SPACY_DATA_PATH, "config.cfg")
SPACY_MODEL_PATH = os.path.join(SPACY_DATA_PATH, "model")


@spacy.registry.readers("Perlego_Corpus.v1")
def create_docbin_reader(
    file: Path,
) -> Callable[[Language], Iterable[Example]]:
    return partial(read_files, file)


def read_files(file: Path, nlp: Language) -> Iterable[Example]:
    doc_bin = DocBin().from_disk(file)
    docs = doc_bin.get_docs(nlp.vocab)
    for gold in docs:
        pred = Doc(
            nlp.vocab,
            words=[t.text for t in gold],
            spaces=[t.whitespace_ for t in gold],
        )
        pred.ents = gold.ents
        yield Example(pred, gold)


def training_prepare(dev_size, limit, source, accepted_labels):

    codes = []
    nlp = None
    db = None
    saved_entries_for_language = None

    nlp = load_latin()
    db = DBWithLabel(DBLabel.LA)
    saved_entries_for_language = []

    if not source:
        saved_entries_for_language = db \
            .load_all(
                DBTableName.RAW_SOURCE,
                source
            )
    else:
        saved_entries_for_language = db \
            .load_from_table_where_attr_equals_value(
                DBTableName.RAW_SOURCE,
                "source_code",
                source,
                multi=True
            )

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
            info for info in entry["info"]
            if info["type"] == INFO_PNOUN_CLUSTER
        ]:
            start = pnoun_cluster["start_index"]
            end = pnoun_cluster["end_index"]
            cluster_string = text[start:end]
            entity = Entity.get_lemma_and_variants_for_string(
                cluster_string, db
            )
            if not entity:
                print(f"Entity {cluster_string} was not found")
            elif not entity.custom_label:
                print(
                    f"Skipping entity {entity.lemma} as it has no custom label"
                )
            elif len(accepted_labels) > 0 \
                    and entity.custom_label not in accepted_labels:
                print(
                    f"Skipping entity {entity.lemma}"
                    f"as label {entity.custom_label} is not recognised"
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
                        " as Spacy doc span creation failed"
                        + f" ({pnoun_cluster['start_index']},"
                        + f" {pnoun_cluster['end_index']})"
                        + f" ({pnoun_cluster['label']})"
                    )
                else:
                    print(
                        f"Adding entity {entity.lemma}"
                        f" ({entity.custom_label})")
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


def training_execute():
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
