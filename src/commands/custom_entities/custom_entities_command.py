import csv

import click

from commands.source.la.treebank.source import TreebankSource
from commands.source.source import SourceCode


def custom_entities_command(source, export_ents, import_ents):
    source_instance = None
    if source == SourceCode.TREEBANK.value:
        source_instance = TreebankSource()
    if export_ents:
        ents = source_instance.get_all_ents()
        with open(export_ents, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["lemma", "labels", "custom"])
            for e in ents:
                click.echo(f"Saving {e}")
                writer.writerow([e["lemma"], ", ".join(e["labels"])])
            click.echo(
                f"Saved entities to {export_ents}. Fill in the 'custom' column"
                "before importing the entities again."
            )
        return

    if import_ents:
        with open(import_ents, encoding="UTF8", newline="") as f:
            entities = list(csv.reader(f, delimiter=",", quotechar='"'))
            if not entities[0]:
                raise Exception("Invalid csv")
            header = entities[0]
            if not (
                header[0] == "lemma"
                and header[1] == "labels"
                and header[2] == "custom"
            ):
                raise Exception(
                    "In order for the import to work,"
                    " the csv has to have the columns:"
                    " 'lemma', 'labels' and 'custom'"
                )
            for row in list(entities)[1:]:
                lemma = row[0]
                label = row[2]
                click.echo(f"Labelling {lemma} with custom label {label}")
                source_instance.add_entity_custom_label(row[0], row[2])
        return
