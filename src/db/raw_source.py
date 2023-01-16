from db.labelled_db import DBTableName, DBWithLabel
from source.source import SourceCode


class RawSourceInfo:
    def __init__(
        self, start_index: int, end_index: int, type: str, label: str
    ):
        self.start_index = start_index
        self.end_index = end_index
        self.type = type
        self.label = label

    def as_dict_obj(self):
        return {
            "start_index": self.start_index,
            "end_index": self.end_index,
            "type": self.type,
            "label": self.label,
        }

    def to_string(self):
        position = f"({self.start_index}, {self.end_index})"
        return f"[{self.type}] {self.label} {position}"


class RawSource:
    def __init__(self, source_code: SourceCode, text: str):
        self.source_code = source_code
        self.text = text
        self.info = []

    def as_dict_obj(self):
        info = []
        for i in self.info:
            info.append(i.as_dict_obj())
        return {
            "source_code": self.source_code.value,
            "text": self.text,
            "info": info,
        }

    def add_info(
        self, start_index: int, end_index: int, type: str, label: str
    ):
        self.info.append(RawSourceInfo(start_index, end_index, type, label))

    def get_info(self):
        return self.info

    def get_info_by_type(self, type):
        return [i for i in self.info if i.type == type]

    def persist(self, db: DBWithLabel):
        return db.save_in_table(self.as_dict_obj(), DBTableName.RAW_SOURCE)

    def exists_in(self, db: DBWithLabel):
        existing = db.load_from_table_where_attr_equals_value(
            DBTableName.RAW_SOURCE, "text", self.text
        )
        if not existing:
            return False
        return True

    def to_string(self, include_info=False):
        numbered_text = ""
        for i, c in enumerate(self.text):
            if include_info and (i % 10 == 0):
                numbered_text += f"[{i}]"
            numbered_text += c
        string = numbered_text
        if include_info:
            for i in self.info:
                string += f"\n{i.to_string()}"
        return string

    @staticmethod
    def count_source_elements_in_db(source_code: SourceCode, db: DBWithLabel):
        return db.count_where_attr_equals_value(
            DBTableName.RAW_SOURCE, "source_code", source_code.value
        )
