import click

from commands.custom_entities.custom_entities_command import \
    custom_entities_command
from commands.custom_relations.custom_relations_command import \
    custom_relations_command
from commands.source.source import SourceCode
from commands.source.source_command import source_command
from commands.train.train_command import (train_execute_command,
                                          train_prepare_command)

# SOURCE


@click.command(name="source")
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Choice([c.value for c in SourceCode]),
    help="The source to download",
)
@click.option(
    "--count",
    "-c",
    is_flag=True,
    help="Displays the count of data source items",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Forces downloading and persisting of the source"
    "even if this has already happened",
)
def source(source, count, force):
    return source_command(source, count, force)


# CUSTOM ENTITIES


@click.command(name="custom_entities")
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Choice([c.value for c in SourceCode]),
    help="The source containing the entities to label",
)
@click.option(
    "--export_ents",
    "-e",
    help="Exports the entities in a csv file",
)
@click.option(
    "--import_ents",
    "-i",
    help="Import the entities from a csv file",
)
def custom_entities(source, export_ents, import_ents):
    return custom_entities_command(source, export_ents, import_ents)


# CUSTOM RELATIONS


@click.command(name="custom_relations")
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Choice([c.value for c in SourceCode]),
    help="The source with the relations to define",
)
def custom_relations(source):
    return custom_relations_command(source)


# PREPARE TRAINING


@click.command(name="train_prepare")
@click.option(
    "--dev_size",
    "-ds",
    required=True,
    type=float,
    help="The ratio of entries used for as the dev part of training"
    " (dev_size + train_size = 1)",
)
@click.option(
    "--train_size",
    "-ts",
    required=True,
    type=float,
    help="Used with the option 'prepare_data'."
    "The ratio of entries used for as the train part of training"
    " (dev_size + train_size = 1)",
)
@click.option(
    "--limit",
    "-lt",
    type=click.IntRange(1),
    help="The limit of entries to prepare",
)
def train_prepare(dev_size, train_size, limit):
    return train_prepare_command(float(dev_size), float(train_size), limit)


# TRAINING


@click.command(name="train")
def train():
    return train_execute_command()


# GROUP COMMANDS


@click.group()
def perlego():
    pass


perlego.add_command(source)
perlego.add_command(custom_entities)
perlego.add_command(custom_relations)
perlego.add_command(train_prepare)
perlego.add_command(train)

if __name__ == "__main__":
    perlego()
