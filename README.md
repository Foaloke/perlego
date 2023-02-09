# Perlego

A tool to help with NLP processing and entity relation extraction.

## Data Sourcing

### Download

To **download** data from a source, and convert it in a format that can be used for a relationship extraction task:

`perlego source -s [SOURCE]`

Where:
- **SOURCE** is one option among [concerts, treebank]

### Item Count

To list the already downloaded sources and the **count of items** per each source:

`perlego source -c`

### Export Entities to a CSV File

After download, the entities will have tags based on Wikipedia Entries. The entities can be downloaded via the command:

`perlego source -e [CSV_PATH]`

Where:
- **CSV_PATH** is the file destination

### Import Entities from a CSV File

A CSV file like the above has a column headed as "custom". There it's possible to define a custom label for the entity, and then import again:

`perlego source -i [CSV_PATH]`

Where:
- **CSV_PATH** is the file to be read
## Training

### Prepare data for training

If sources had been downloaded, they can be used to generate Spacy training data

`perlego train -t [TRAINING_TYPE] -l [LANGUAGE] -ds [DEV_SIZE] -ts [TRAIN_SIZE]`

Where:
- **TRAINING_TYPE** is one option among [entities, relations]
- **LANGUAGE** only "la" supported at the moment
- **DEV_SIZE** is the size size of data to be converted for Spacy DEV training step (fraction of 1)
- **TRAIN_SIZE** is the size size of data to be converted for Spacy TRAIN training step (fraction of 1)



