#! /usr/bin/env python3
r"""Compute CoNLL scores for coreference clustering as recommended by
*Scoring Coreference Partitions of Predicted Mentions: A Reference
Implementation* (Pradhan et al., 2014)

Usage:
  scorch <gold-file> <sys-file> [<out-file>]

Arguments:
  <gold-file>  gold input file (json), `-` for standard input
  <sys-file>   system input file (json), `-` for standard input
  <out-file>   output file (text), `-` for standard output [default: -]

Options:
  -h, --help  Show this screen.

Formats
The input files should be JSON files with a "type" key at top-level
  - If "type" if "graph", then top-level should have at top-level
    - A "mentions" key containing a list of all mention identifiers
    - A "links" key containing a list of pairs of corefering mention
      identifiers
  - If "type" is "clusters", then top-level should have a "clusters" key
    containing a mapping from clusters ids to cluster contents (as lists of
    mention identifiers).

Of course the system and gold files should use the same set of mention identifiers…

Example:
  `scorch gold.json sys.json out.txt`
"""

__version__ = 'scorch 0.0.0'

import contextlib
import json
import pathlib
import signal
import sys

import typing as ty

from docopt import docopt


# Usual frobbing of packages, due to Python's insane importing policy
if __name__ == "__main__" and __package__ is None:
    package_root = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(package_root))
    import scorch  # noqa
    __package__ = "scorch"

try:
    from . import scores
except ImportError:
    from scorch import scores


# Deal with piping output in a standard-compliant way
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

METRICS = [
    ('MUC', scores.muc),
    ('B³', scores.b_cubed),
    ('CEAF_m', scores.ceaf_m),
    ('CEAF_e', scores.ceaf_e),
    ('BLANC', scores.blanc)
]


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


def greedy_clustering(links: ty.Iterable[ty.Tuple[ty.Hashable, ty.Hashable]]) -> ty.List[ty.Set]:
    r'''
    Get connected component clusters from a set of edges.

    This is basically done with depth 1 [disjoint-sets][1], which seemed a good tradeoff between
    performance and readability. If performance is an issue, consider using e.g. the [incremental
    connected component algorithm][2] found in Boost Graph.

    Even better: don't rely on this and preprocess your data using a more clever clustering
    procedure, e.g. with [NetworkX][3].

    [1]: https://en.wikipedia.org/wiki/Disjoint-set_data_structure
    [2]: http://www.boost.org/doc/libs/1_66_0/libs/graph/doc/incremental_components.html
    [3]: https://networkx.github.io/documentation/networkx-1.9.1/reference/algorithms.mst.html
    '''
    clusters = dict()  # type: ty.Dict[ty.Hashable, ty.List]
    heads = dict()  # type: ty.Dict[ty.Hashable, ty.Hashable]
    for source, target in links:
        source_head = heads.setdefault(source, source)
        source_cluster = clusters.setdefault(source_head, [source_head])

        target_head = heads.setdefault(target, None)
        if target_head is None:
            heads[target] = source_head
            source_cluster.append(target)
        elif target_head is not source_head:  # Merge `target`'s cluster into `source`'s'
            for e in clusters[target_head]:
                heads[e] = source_head
            source_cluster.extend(clusters[target_head])
            del clusters[target_head]

    return [set(c) for c in clusters.values()]


def clusters_from_graph(nodes: ty.Iterable[ty.Hashable],
                        edges: ty.Iterable[ty.Tuple[ty.Hashable, ty.Hashable]]) -> ty.List[ty.Set]:
    '''Return the connex components of a graph.'''
    clusters = greedy_clustering(edges)
    non_sing = set.union(*clusters)
    singletons = [{n} for n in nodes if n not in non_sing]
    clusters.extend(singletons)
    return clusters


def clusters_from_json(fp) -> ty.List[ty.Set]:
    obj = json.load(fp)
    if obj["type"] == "graph":
        return clusters_from_graph(obj['mentions'], obj['links'])
    elif obj["type"] == "clusters":
        return [set(c) for c in obj["clusters"]]
    raise ValueError('Unsupported input format')


def main_entry_point(argv=None):
    arguments = docopt(__doc__, version=__version__, argv=argv)
    # Since there are no support for default positional arguments in
    # docopt yet. Might be useful for complex default values, too
    if arguments['<out-file>'] is None:
        arguments['<out-file>'] = '-'

    with smart_open(arguments['<gold-file>']) as in_stream:
        gold_clusters = clusters_from_json(in_stream)

    with smart_open(arguments['<sys-file>']) as in_stream:
        sys_clusters = clusters_from_json(in_stream)

    with smart_open(arguments['<out-file>'], 'w') as out_stream:
        for name, metric in METRICS:
            P, R, F = metric(gold_clusters, sys_clusters)
            out_stream.write(f'{name}:\tP={P}\tR={R}\tF₁={F}\n')
        conll_score = scores.conll2012(gold_clusters, sys_clusters)
        out_stream.write(f'CoNLL-2012 average score: {conll_score}\n')


if __name__ == '__main__':
    sys.exit(main_entry_point())
