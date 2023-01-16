# Perlego

A tool to help with NLP processing and entity relation extraction.

## Data Sourcing

To downloads data from a source, and convert it in a format that can be used for a relationship extraction task:
`perlego source -s [SOURCE]`

Where:
- **SOURCE** is one option among [concerts, treebank]

To list the already downloaded sources and the count of items per each source:
`perlego source -c`

## Tagging

`perlego tag -l [LANG] -s [SOURCE] -m [MODE] -e [ENTS_PATH] -r [RELS_PATH]`

Where:
- **LANG** is one option among [la, en]
- **SOURCE** is one option among [concerts, treebank]
- **MODE** is one option among [manual, wiki]
- **ENTS_PATH** is the file containing a list of possible entities, one entity per line, e.g.
```
ANIMAL
PERSON
FRUIT
...
```
- **RELS_PATH** is the file containing a list of possible relationships between the ENTS, one relationship per line
Relationships are expressed in the format ENT1_ACTION_ENT2, e.g.
```
PERSON_EATS_FRUIT
PERSON_EATS_ANIMAL
ANIMAL_EATS_FRUIT
...
```

### Manual Option

It starts a cli tool to manually tag entities and relationships in a given downloaded source

### Wiki Option

It starts a cli tool to tag entities using wikipedia and manually tag relationships in a given downloaded source

## Machine Learning

Performs the training in spacy

`perlego train -l 'latin' -s [SOURCE_PATH]`
Where:
- **SOURCE** is one option among [concerts, treebank]

Performs a prediction over text contained in an input file

`perlego predict -l 'latin' -s [SOURCE_PATH] -i [INPUT_PATH]`
Where:
- **SOURCE** is one option among [concerts, treebank]
- **INPUT_PATH** is the file containing the text upon which making predictions
  
# Database Structure

(For each language)

raw_source
    (id, text, info: [{ type, start_index, end_index, label }])

entities
    (id, lemma, variants: [], label)

relations
    (id, start_ent_id, end_ent_id, label)

training_data
    (id, text, entities: [{ start_index, ent_id, weight }], relations: [{ start_ent, end_ent, label, weight }])

