import click

from commands.train.train import training_execute, training_prepare
from strings import code_string


def train_prepare_command(dev_size, train_size, limit):

    if dev_size + train_size != 1.0:
        click.echo(
            "'dev_size' and 'train_size' must add up to 1"
            + f" ({dev_size} and {train_size} given)"
        )
        return

    for code in training_prepare(dev_size, limit):
        click.echo(code_string(code))


def train_execute_command():
    for code in training_execute():
        click.echo(code_string(code))
