from db.entity import Entity
from source.wiki_tagger.tagger import tag as wiki_tag


def tag(string, language, db):
    (entity, _) = Entity.get_lemma_and_variants_for_string(string, db)
    if entity:
        return entity
    return wiki_tag(string, language)
