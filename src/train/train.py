from enum import Enum


class TrainCode(Enum):
    ENTITIES = "entities"
    RELATIONS = "relations"


class TrainOutcomeCode(Enum):
    NO_DATA_FOR_LANGUAGE = "no_data_for_language"
    TRAINING_COMPLETE = "training_complete"
