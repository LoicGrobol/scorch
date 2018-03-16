'''Parse CoNLL-2012 files.'''

import re

import typing as ty

from collections import defaultdict


def parse_block(lines: ty.Iterable[str], column=-1) -> ty.Dict[str, ty.List[ty.Tuple[str, str]]]:
    '''
    Parse a bloc (≈sentence) in the CoNLL format, return entities as mappings
    ```
    entity_id: [(mention_start, mention_end), …]
    ```
    '''
    entities = defaultdict(list)
    dangling = defaultdict(list)
    for i, l in enumerate(lines):
        row = l.split('\t')

        try:
            row_n = row[2]
            coref = row[column]
        except IndexError:
            raise ValueError(f'Badly formatted line: {l!r}')
        if coref == '-':
            continue

        for m in re.finditer(r'\((\d+)', coref):
            dangling[m.group(1)].append(row_n)

        for m in re.finditer(r'(\d+)\)', coref):
            try:
                entities[m.group(1)].append((dangling[m.group(1)].pop(), row_n))
            except IndexError:
                raise ValueError(f'Unbalanced parentheses at line {i}: {l!r}')
    if any(dangling.values()):
        raise ValueError(f'Dangling mentions at line {i}: {[e for e, v in dangling.items() if e]}')
    return dict(entities)


def split_blocks(lines: ty.Iterable[str]) -> ty.Iterable[ty.List[str]]:
    '''Split blocks in a CoNLL document.'''
    buffer = []
    for l in lines:
        if not l or l.isspace():
            yield buffer
            buffer = []
        else:
            buffer.append(l)
    if buffer:
        yield buffer


def parse_document(lines: ty.Iterable[str], column=-1
                   ) -> ty.Dict[str, ty.List[ty.Tuple[int, str, str]]]:
    '''
    Parse a document in the CoNLL format, return entities as mappings
    ```
    entity_id: [(block_number, mention_start, mention_end), …]
    ```
    '''
    entities = defaultdict(list)
    for i, block in enumerate(split_blocks(lines)):
        try:
            block_entities = parse_block(block)
        except ValueError as e:
            raise ValueError(
                'Parse error in block {i}:\n{e}\n{block}'.format(i=i, e=e,
                                                                block="\n".join(block)))
        # Merge this block entities
        for e, mentions in block_entities.items():
            entities[e].extend([(i, start, end) for start, end in mentions])
    return dict(entities)


def parse_file(lines: ty.Iterable[str],
               column=-1,
              ) -> ty.Iterable[ty.Tuple[str, ty.Dict[str, ty.List[ty.Tuple[int, str, str]]]]]:
    '''Parse a CoNLL file, return document as tuples `(document_name, entities)` where
       entities are mappings
       ```
       entity_id: [(block_number, mention_start, mention_end), …]
       ```'''
    buffer = []
    for l in lines:
        if l.startswith('#'):
            m = re.match(r'#\s*begin document \((.*?)\);(\s*part (.*))?', l)
            if m:
                if m.group(2):
                    doc_name = f'{m.group(1)}-{m.group(3)}'
                else:
                    doc_name = m.group(1)
                continue
            m = re.match(r'#\s*end document', l)
            if m:
                doc_entities = parse_document(buffer, column)
                buffer = []
                yield (doc_name, doc_entities)
        else:
            buffer.append(l)
