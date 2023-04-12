from commands.source.la.treebank.source import TreebankSource
from commands.source.source import SourceCode


def custom_relations_command(source):
    source_instance = None
    if source == SourceCode.TREEBANK.value:
        source_instance = TreebankSource()
        for raw_source in source_instance.get_all_raw_sources():
            text = raw_source["text"]
            pnoun_clusters = [
                i for i in raw_source["info"] if i["type"] == "pnoun_cluster"
            ]
            print("\nTEXT\n\n", text)

            print("\nENTITIES\n")
            for pnoun_cluster in pnoun_clusters:
                lemma = pnoun_cluster["label"]
                entity = source_instance.load_entity_data_of_lemma(lemma)
                print(entity.lemma, entity.custom_label)

            input("")
