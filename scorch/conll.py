#! /usr/bin/env python3
r"""Convert CoNLL-2012 files to simple JSON.

Usage:
  conll <conll-file> [<out-dir>]

Arguments:
  <conll-file>  input file (CoNLL-2012 format), `-` for standard input
  <out-dir>     directory for output [default: same as the input]

Options:
  -h, --help  Show this screen.

Example:
  `conll input.conll ./out/`
"""

__version__ = 'conll 0.0.0'

import contextlib
import json
import pathlib
import re
import sys

import typing as ty

from collections import defaultdict

from docopt import docopt


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
        row = l.split()

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


# Thanks http://stackoverflow.com/a/17603000/760767
@contextlib.contextmanager
def smart_open(filename: str = None, mode: str = 'r', *args, **kwargs):
    '''Open files and i/o streams transparently.'''
    if filename == '-':
        if 'r' in mode:
            stream = sys.stdin
        else:
            stream = sys.stdout
        if 'b' in mode:
            fh = stream.buffer
        else:
            fh = stream
    else:
        fh = open(filename, mode, *args, **kwargs)

    try:
        yield fh
    finally:
        try:
            fh.close()
        except AttributeError:
            pass


def main_entry_point(argv=None):
    arguments = docopt(__doc__, version=__version__, argv=argv)
    # Since there are no support for default positional arguments in
    # docopt yet. Might be useful for complex default values, too
    if arguments['<out-dir>'] is None:
        if arguments['<conll-file>'] == '-':
            arguments['<out-dir>'] = pathlib.Path.cwd()
        else:
            arguments['<out-dir>'] = pathlib.Path(arguments['<conll-file>']).parent
    else:
        arguments['<out-dir>'] = pathlib.Path(arguments['<out-dir>'])

    with smart_open(arguments['<conll-file>']) as in_stream:
        documents = list(parse_file((l.strip() for l in in_stream)))

    for name, entities in documents:
        sanitized_name = name.replace('/', '-')
        out_path = arguments['<out-dir>']/f'{sanitized_name}.json'
        with out_path.open('w') as out_stream:
            json.dump(entities, out_stream)


if __name__ == '__main__':
    sys.exit(main_entry_point())
