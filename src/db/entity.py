from db.labelled_db import DBTableName, DBWithLabel
from utils.lambda_utils import lmap


class EntityVariant:
    def __init__(self, lemma_id: int, variant: str):
        self.lemma_id = lemma_id
        self.variant = variant

    def as_dict_obj(self):
        return {"lemma_id": self.lemma_id, "variant": self.variant}

    @staticmethod
    def from_dict_obj(db_entity_variant):
        return EntityVariant(
            db_entity_variant["lemma_id"], db_entity_variant["variant"]
        )

    def persist(self, db: DBWithLabel):
        return db.save_in_table(
            self.as_dict_obj(), DBTableName.ENTITY_VARIANT
        )

    @staticmethod
    def get_lemma_id_for_string(string: str, db: DBWithLabel):
        entity = db.load_from_table_where_attr_equals_value(
            DBTableName.ENTITY_VARIANT, "variant", string
        )
        if not entity:
            return None
        return entity["lemma_id"]

    @staticmethod
    def get_variants_for_lemma_id(lemma_id: int, db: DBWithLabel):
        return lmap(
            EntityVariant.from_dict_obj,
            db.load_from_table_where_attr_equals_value(
                DBTableName.ENTITY_VARIANT, "lemma_id", lemma_id, multi=True
            ),
        )


class Entity:
    def __init__(self, lemma: str):
        self.lemma = lemma
        self.labels = []
        self.custom_label = ""
        self.variants_strings = []

    def add_labels(self, labels: list[str]):
        self.labels.extend(labels)

    def add_variant_string(self, variant_string: str):
        self.variants_strings.append(variant_string)

    def as_dict_obj(self):
        return {"lemma": self.lemma, "labels": self.labels}

    @staticmethod
    def from_dict_obj(db_entity, entity_variants=[]):
        entity = Entity(db_entity["lemma"])
        entity.add_labels(db_entity["labels"])
        entity.custom_label = db_entity["custom_label"]
        for entity_variant in entity_variants:
            entity.add_variant_string(entity_variant.variant)
        return entity

    def persist(self, db: DBWithLabel):
        entity_id = db.save_in_table(self.as_dict_obj(), DBTableName.ENTITIES)
        if len(self.variants_strings) == 0:
            entity_base_variant = EntityVariant(entity_id, self.lemma)
            entity_base_variant.persist(db)
        else:
            for vs in self.variants_strings:
                entity_variant = EntityVariant(entity_id, vs)
                entity_variant.persist(db)
        return entity_id

    def exists_in(self, db: DBWithLabel):
        existing = db.load_from_table_where_attr_equals_value(
            DBTableName.ENTITIES, "lemma", self.lemma
        )
        if not existing:
            return False
        return True

    def to_string(self):
        return (
            f"{self.lemma} {self.labels}"
            + f"{self.variants_strings} ({self.custom_label})"
        )

    @staticmethod
    def get_lemma_and_variants_for_string(
        string: str, db: DBWithLabel
    ) -> object:
        lemma_id = EntityVariant.get_lemma_id_for_string(string, db)
        if lemma_id:
            return Entity.from_dict_obj(
                db.load_from_table_by_id(DBTableName.ENTITIES, lemma_id),
                EntityVariant.get_variants_for_lemma_id(lemma_id, db),
            )
        else:
            return Entity.from_dict_obj(Entity.load_by_lemma(db, string), [])

    @staticmethod
    def load_all(db: DBWithLabel) -> object:
        return db.load_all(DBTableName.ENTITIES)

    @staticmethod
    def load_by_lemma(db: DBWithLabel, lemma: str) -> object:
        return db.load_from_table_where_attr_equals_value(
            DBTableName.ENTITIES, "lemma", lemma
        )

    @staticmethod
    def update_custom_label(
        db: DBWithLabel, lemma: str, custom_label: str
    ) -> object:
        return db.update(
            DBTableName.ENTITIES,
            "lemma",
            lemma,
            "custom_label",
            custom_label,
        )
