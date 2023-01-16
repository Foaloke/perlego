from db.labelled_db import DBTableName, DBWithLabel


class EntityVariant:
    def __init__(self, lemma_id: int, variant: str):
        self.lemma_id = lemma_id
        self.variant = variant

    def as_dict_obj(self):
        return {"lemma_id": self.lemma_id, "variant": self.variant}

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


class Entity:
    def __init__(self, lemma: str):
        self.lemma = lemma
        self.labels = []
        self.variants_strings = []

    def add_labels(self, labels: list[str]):
        self.labels.extend(labels)

    def add_variant_string(self, variant_string: str):
        self.variants_strings.append(variant_string)

    def as_dict_obj(self):
        return {"lemma": self.lemma, "labels": self.labels}

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
        return f"{self.lemma} {self.labels} {self.variants_strings}"

    @staticmethod
    def get_lemma_and_variants_for_string(
        string: str, db: DBWithLabel
    ) -> object:
        lemma_id = EntityVariant.get_lemma_id_for_string(string, db)
        if not lemma_id:
            return None, None
        entity = db.load_from_table_where_attr_equals_value(
            DBTableName.ENTITIES, "id", lemma_id
        )
        variants = db.load_from_table_where_attr_equals_value(
            DBTableName.ENTITY_VARIANT, "lemma_id", lemma_id, multi=True
        )
        return entity, variants
