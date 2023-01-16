from abc import ABC, abstractmethod
from enum import Enum

base_path = "data"


class SourceCode(Enum):
    TREEBANK = "treebank"
    CONCERTS = "concerts"


class StoreCode(Enum):
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
    def count():
        pass

    def store(self, force):
        codes = []
        if not force and self.is_already_downloaded():
            codes.append(StoreCode.ALREADY_DOWNLOADED)
        else:
            self.download()
            codes.append(StoreCode.DOWNLOADED)
        if not force and self.is_already_persisted():
            codes.append(StoreCode.ALREADY_PERSISTED)
        else:
            self.persist()
            codes.append(StoreCode.PERSISTED)
        return codes
