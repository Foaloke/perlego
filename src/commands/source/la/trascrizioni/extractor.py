import re

from db.raw_source import RawSource, SourceCode
from utils.lambda_utils import lmap

TAGGED_PNOUN_LABEL = 'tagged_pnoun'

CONTROL_SYMBOLS_TO_REMOVE = ['(', ')', '[', ']', '...']
MARKER = {
    'LOCATION': {'start': '@', 'end': '%'},
    'PERSON': {'start': '$', 'end': '^'}
}


def is_marker(character, marker_flag):
    for type, marker in MARKER.items():
        if marker[marker_flag] == character:
            return type
    return None


def remove_control_strings(string):
    result = string
    for cs in CONTROL_SYMBOLS_TO_REMOVE:
        result = result.replace(cs, '')
    return re.sub(' +', ' ', result).replace('\n', ' ')


def extract_marked_items_from(sentence):
    sentence_without_markers = ''
    marked = []
    current_index = 0
    current_marked = None
    for character in sentence:
        start_marker_type = is_marker(character, 'start')
        end_marker_type = is_marker(character, 'end')
        if start_marker_type:
            current_marked = {
                'start_index': current_index,
                'end_index': None,
                'type': start_marker_type
            }
        elif end_marker_type:
            if not current_marked:
                raise Exception(
                    f'Unexpected terminal marker {character} in {sentence}')
            if end_marker_type != current_marked['type']:
                print(f'WARNING: Marked type "{current_marked["type"]}"'
                      f' ended unexpectedly with "{character}"\n'
                      f'{sentence}'
                      )
            current_marked['end_index'] = current_index
            marked.append(current_marked)
            current_marked = None
        else:
            sentence_without_markers += character
            current_index += 1
    return sentence_without_markers, marked


def extract_raw_sources(data_file):
    raw_sources = []
    with open(data_file, 'r') as f:
        text = ''
        for line in f.readlines():
            text += remove_control_strings(line)
        marked_sentences = text.split('.')
        marked_sentences = lmap(lambda s: s.strip(), marked_sentences)
        for marked_sentence in marked_sentences:
            sentence, marked = extract_marked_items_from(marked_sentence)
            raw_source = RawSource(SourceCode.TRASCRIZIONI, sentence)
            for m in marked:
                raw_source.add_info(
                    m['start_index'],
                    m['end_index'],
                    TAGGED_PNOUN_LABEL,
                    m['type']
                )
            raw_sources.append(raw_source)
    return raw_sources
