
import os

import numpy as np
from spacy.util import load_model

from commands.source.source import INFO_PNOUN_CLUSTER
from commands.train.train import SPACY_MODEL_PATH
from db.labelled_db import DBLabel, DBTableName, DBWithLabel


def prediction_in_expected(prediction, expected_predictions):
    matching_expected = [
        e for e in expected_predictions
        if (
            e["start_index"] == prediction.start_char
            and e["end_index"] == prediction.end_char
            and e["label"] == prediction.label_
        )
    ]
    return len(matching_expected) == 1


def score_model_execute(source, start_index):

    nlp = load_model(os.path.join(SPACY_MODEL_PATH, "model-best"))

    db = None
    saved_entries_for_language = None

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

    saved_entries_for_language = list(saved_entries_for_language)[start_index:]

    precision_values = []
    recall_values = []

    current_size = 0
    total_size = len(saved_entries_for_language)
    for entry in saved_entries_for_language:
        text = entry["text"]
        doc = nlp(text)

        # print(text)

        expected = [
            info for info in entry["info"]
            if info["type"] == INFO_PNOUN_CLUSTER
        ]
        predicted = doc.ents

        # for e in expected:
        #     e_start = e['start_index']
        #     e_end = e['end_index']
        #     print(
        #       'EXPECTED', e_start, e_end, text[e_start:e_end], e['label']
        #     )
        # for p in predicted:
        #     print('PREDICTED', p.start_char, p.end_char, p.text, p.label_)

        number_of_correct_results = len([
            p for p in predicted if prediction_in_expected(p, expected)])

        precision = 1
        if len(predicted) > 0:
            precision = number_of_correct_results / len(predicted)
        elif len(expected) > 0:
            precision = 0

        recall = 1
        if len(expected) > 0:
            recall = number_of_correct_results / len(expected)

        precision_values.append(precision)
        recall_values.append(recall)

        current_size += 1
        print("\r", f"PROGRESS --> {current_size}/{total_size}", end="\r")

    return np.mean(precision_values), np.mean(recall_values)
