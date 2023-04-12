from commands.source.wiki_tagger.tagger import tag as wiki_tag
from db.entity import Entity


def tag(string, db):
    entity = Entity.get_lemma_and_variants_for_string(string, db)
    if entity:
        return entity.labels
    return wiki_tag(string)
