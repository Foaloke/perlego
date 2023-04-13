from commands.score_model.score_model_codes import ScoreModelOutcomeCode
from commands.source.source import SourceOutcomeCode
from commands.train.train_codes import TrainOutcomeCode


def code_string(code, *args):
    if code == SourceOutcomeCode.DOWNLOADED:
        source = args[0]
        return f"The source '{source}' has been downloaded"
    if code == SourceOutcomeCode.ALREADY_DOWNLOADED:
        source = args[0]
        return (
            f"The source '{source}' was already downloaded. Read the 'help'"
            " to understand how to repeat the process if needed."
        )
    if code == SourceOutcomeCode.MANUAL_DOWNLOAD_REQUIRED:
        source = args[0]
        return (
            f"The source '{source}' needs the user to manually download"
            " the required files and place them in the data directory."
        )
    if code == SourceOutcomeCode.PERSISTED:
        source = args[0]
        return f"The source '{source}' has been persisted"
    if code == SourceOutcomeCode.ALREADY_PERSISTED:
        source = args[0]
        return (
            f"The source '{source}' was already persisted."
            " Read the 'help' to understand"
            " how to repeat the process if needed."
        )
    if code == TrainOutcomeCode.NO_DATA_FOR_LANGUAGE:
        return (
            "There is no saved entries."
            " Maybe the command 'source' has to be run first,"
            " in order to fill in the database with data?"
        )

    if code == ScoreModelOutcomeCode.SCORE_MODEL_COMPLETE:
        return f"Precision: {args[0]} - Recall: {args[1]}"
