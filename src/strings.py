from source.source import SourceOutcomeCode
from train.train import TrainOutcomeCode


def code_string(code, *args):
    if code == SourceOutcomeCode.DOWNLOADED:
        source = args[0]
        return f"The source '{source}' has been downloaded"
    if code == SourceOutcomeCode.ALREADY_DOWNLOADED:
        source = args[0]
        return (
            f"The source '{source}' was already downloaded. Read the 'help'"
            + " to understand how to repeat the process."
        )
    if code == SourceOutcomeCode.PERSISTED:
        source = args[0]
        return f"The source '{source}' has been persisted"
    if code == SourceOutcomeCode.ALREADY_PERSISTED:
        source = args[0]
        return (
            f"The source '{source}' was already persisted."
            + " Read the 'help' to understand how to repeat the process."
        )
    if code == TrainOutcomeCode.NO_DATA_FOR_LANGUAGE:
        language = args[0]
        return (
            f"The language '{language}' has no saved entries."
            + " Maybe the command 'source' has to be run first,"
            + " in order to fill in the database with data?"
        )
