'''Parse CoNLL-2012 files.'''

import re

import typing as ty

from collections import defaultdict

Span = ty.NewType('Span', ty.Tuple[ty.Hashable, ty.Hashable])


def parse_block(lines: ty.Iterable[str], column=-1) -> ty.Dict[str, ty.List[Span]]:
    entities = defaultdict(list)
    dangling = defaultdict(list)
    for l in lines:
        row = l.split('\t')

        row_n = row[2]
        coref = row[column]
        if coref == '-':
            continue

        for m in re.finditer(r'\(([^()]+)', coref):
            dangling[m.group(1)].append(row_n)

        for m in re.finditer(r'([^()])\)', coref):
            entities[m.group(1)].append((dangling[m.group(1)].pop(), row_n))
    if any(dangling.values()):
        raise ValueError(f'Dangling mentions: {[e for e, v in dangling.items() if e]}')
    return entities
