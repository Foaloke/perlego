from enum import Enum

from tinydb import Query, TinyDB
from tinydb.operations import set


class DBLabel(Enum):
    LA = "la"
    EN = "en"
    WIKI_INFO = "wiki_info"


class DBTableName(Enum):
    RAW_SOURCE = "RAW_SOURCE"
    ENTITIES = "ENTITIES"
    ENTITY_VARIANT = "ENTITY_VARIANT"
    RELATIONS = "RELATIONS"
    TRAINING_DATA = "TRAINING_DATA"
    WIKI_ENTITY = "WIKI_ENTITY"


class DBWithLabel:
    def __init__(self, label: DBLabel):
        self.db = TinyDB(f"./db/{label.value}_db.json")

    def save_in_table(self, obj: object, table_name: DBTableName) -> int:
        return self.db.table(table_name.value).insert(obj)

    def load_from_table_by_id(self, table_name: DBTableName, id):
        return self.db.table(table_name.value).get(doc_id=id)

    def load_from_table_where_attr_equals_value(
        self,
        table_name: DBTableName,
        attr: str,
        value: object,
        multi: bool = False,
    ) -> object:
        query = Query()
        result = self.db.table(table_name.value).search(query[attr] == value)
        if result and (len(result) > 0):
            if multi:
                return result
            return result[0]
        return None

    def load_all(self, table_name: DBTableName):
        return self.db.table(table_name.value)

    def count_where_attr_equals_value(
        self, table_name: DBTableName, attr: str, value: object
    ):
        table = self.load_from_table_where_attr_equals_value(
            table_name, attr, value, multi=True
        )
        if not table:
            return None

        return len(table)

    def update(
        self,
        table_name: DBTableName,
        search_key,
        search_value,
        update_key,
        update_value,
    ):
        query = Query()
        return self.db.table(table_name.value).update(
            set(update_key, update_value), query[search_key] == search_value
        )
