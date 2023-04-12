from abc import ABC, abstractmethod
from enum import Enum

base_path = "data"


class SourceCode(Enum):
    TREEBANK = "treebank"
    TRASCRIZIONI = "trascrizioni"


class SourceOutcomeCode(Enum):
    DOWNLOADED = "DOWNLOADED"
    ALREADY_DOWNLOADED = "ALREADY_DOWNLOADED"
    PERSISTED = "PERSISTED"
    ALREADY_PERSISTED = "ALREADY_PERSISTED"
    MANUAL_DOWNLOAD_REQUIRED = "MANUAL_DOWNLOAD_REQUIRED"


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

    @staticmethod
    def add_entity_custom_label(lemma, custom_label):
        pass

    @staticmethod
    def get_all_ents(self):
        pass

    def store(self, force):
        codes = []
        # Download
        if not force and self.is_already_downloaded():
            codes.append(SourceOutcomeCode.ALREADY_DOWNLOADED)
        else:
            codes.append(self.download())

        # Persist
        if not force and self.is_already_persisted():
            codes.append(SourceOutcomeCode.ALREADY_PERSISTED)
        else:
            codes.append(self.persist())
        return codes
