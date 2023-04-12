from collections.abc import Callable

from db.labelled_db import DBTableName, DBWithLabel


class WikiDataInfo:
    def __init__(self, code: str, info: str):
        self.code = code
        self.info = info

    def as_dict_obj(self):
        return {"code": self.code, "info": self.info}

    @staticmethod
    def load(db: DBWithLabel, code: str, resolver: Callable[[str], str]):
        wikidata_entity = db.load_from_table_where_attr_equals_value(
            DBTableName.WIKI_ENTITY, "code", code
        )
        if not wikidata_entity:
            resolved = resolver(code)
            if not resolved:
                return None
            new_wikidata_entity = WikiDataInfo(code, resolved)
            new_wikidata_entity.persist(db)
            return new_wikidata_entity.info

        return wikidata_entity["info"]

    def persist(self, db: DBWithLabel):
        return db.save_in_table(self.as_dict_obj(), DBTableName.WIKI_ENTITY)
