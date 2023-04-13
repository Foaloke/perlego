
import click

from commands.score_model.score_model import score_model_execute
from commands.score_model.score_model_codes import ScoreModelOutcomeCode
from strings import code_string


def score_model_command(source, start_index):
    precision, recall = score_model_execute(source, start_index)
    click.echo(code_string(
        ScoreModelOutcomeCode.SCORE_MODEL_COMPLETE, precision, recall
    ))
