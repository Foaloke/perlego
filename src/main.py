import click

from source.source import SourceCode
from source.source_command import source_command
from train.train import TrainCode
from train.train_command import train_execute_command, train_prepare_command

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
    "--export_ents",
    "-e",
    help="Exports the entities in a csv file",
)
@click.option(
    "--import_ents",
    "-i",
    help="Import the entities from a csv file",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Forces downloading and persisting of the source"
    + "even if this happened already",
)
def source(source, count, export_ents, import_ents, force):
    return source_command(source, count, export_ents, import_ents, force)


# TRAIN


@click.command(name="train")
@click.option(
    "--type",
    "-t",
    required=True,
    type=click.Choice([c.value for c in TrainCode]),
    help="The type of training to perform",
)
@click.option(
    "--language",
    "-l",
    required=True,
    help="The language of the saved entries that must be used for training",
)
@click.option(
    "--prepare_data",
    "-pd",
    is_flag=True,
    help="If this option is on, then a preliminary step to convert"
    + "downloaded data to Spacy format will be executed."
    + " This option requires the 'dev_size' and 'train_size' options defined",
)
@click.option(
    "--dev_size",
    "-ds",
    type=float,
    help="Used with the option 'prepare_data'."
    + "The ratio of entries used for as the dev part of training"
    + " (dev_size + train_size = 1)",
)
@click.option(
    "--train_size",
    "-ts",
    type=float,
    help="Used with the option 'prepare_data'."
    + "The ratio of entries used for as the train part of training"
    + " (dev_size + train_size = 1)",
)
@click.option(
    "--limit",
    "-lt",
    type=click.IntRange(1),
    help="Used with the option 'prepare_data'."
    + "The limit of entries to prepare",
)
def train(type, language, prepare_data, dev_size, train_size, limit):
    if prepare_data:
        if not (dev_size and train_size):
            click.echo(
                "With the 'prepare_data' option,"
                + " both dev_size and train_size must be defined"
            )
            return
        return train_prepare_command(
            type, language, float(dev_size), float(train_size), limit
        )

    return train_execute_command(type, language)


@click.group()
def perlego():
    pass


perlego.add_command(source)
perlego.add_command(train)

if __name__ == "__main__":
    perlego()
