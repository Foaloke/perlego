from abc import ABC, abstractmethod
from enum import Enum

base_path = "data"


class SourceCode(Enum):
    TREEBANK = "treebank"
    CONCERTS = "concerts"


class SourceOutcomeCode(Enum):
    DOWNLOADED = "DOWNLOADED"
    ALREADY_DOWNLOADED = "ALREADY_DOWNLOADED"
    PERSISTED = "PERSISTED"
    ALREADY_PERSISTED = "ALREADY_PERSISTED"


class Source(ABC):
    @staticmethod
    @abstractmethod
    def base_path():
        return base_path

    @abstractmethod
    def is_already_downloaded(self):
        pass

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def is_already_persisted(self):
        pass

    @abstractmethod
    def persist(self):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def get_all_ents(self):
        pass

    @abstractmethod
    def add_entity_custom_label(self, lemma, custom_label):
        pass

    def store(self, force):
        codes = []
        # Download
        if not force and self.is_already_downloaded():
            codes.append(SourceOutcomeCode.ALREADY_DOWNLOADED)
        else:
            self.download()
            codes.append(SourceOutcomeCode.DOWNLOADED)

        # Persist
        if not force and self.is_already_persisted():
            codes.append(SourceOutcomeCode.ALREADY_PERSISTED)
        else:
            self.persist()
            codes.append(SourceOutcomeCode.PERSISTED)
        return codes
