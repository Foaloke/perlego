import click

from strings import code_string
from train.entity_training import (
    entity_training_execute,
    entity_training_prepare,
)
from train.train import TrainCode

TYPE_MAPPING = {
    TrainCode.ENTITIES.value: {
        "prepare": entity_training_prepare,
        "execute": entity_training_execute,
    }
}


def train_prepare_command(type, language, dev_size, train_size, limit):

    if not TYPE_MAPPING[type]:
        click.echo(
            f"The type of training '{type}' has not yet been implemented"
        )
        return

    if dev_size + train_size != 1.0:
        click.echo(
            "'dev_size' and 'train_size' must add up to 1"
            + f" ({dev_size} and {train_size} given)"
        )
        return

    for code in (TYPE_MAPPING[type]["prepare"])(language, dev_size, limit):
        click.echo(code_string(code, language))


def train_execute_command(type, language):

    if not TYPE_MAPPING[type]:
        click.echo(
            f"The type of training '{type}' has not yet been implemented"
        )
        return

    for code in TYPE_MAPPING[type]["execute"]():
        click.echo(code_string(code, language))
