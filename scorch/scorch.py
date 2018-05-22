#! /usr/bin/env python3
r"""Compute CoNLL scores for coreference clustering as recommended by
*Scoring Coreference Partitions of Predicted Mentions: A Reference
Implementation* (Pradhan et al., 2014)

## Usage:
  scorch <gold> <sys> [<out-file>]

## Arguments:
  <gold>      gold input file (json) or directory, `-` for standard input
  <sys>       system input file (json) or directory, `-` for standard input
  <out-file>  output file (text), `-` for standard output [default: -]

## Options:
  -h, --help       Show this screen.

## Example:
  `scorch gold.json sys.json out.txt`
  `scorch gold/ sys/ out.txt`
"""

import contextlib
import json
import pathlib
import signal
import sys

import typing as ty

from statistics import mean

import tqdm

import numpy as np

from docopt import docopt


try:
    from . import scores
    from . import __version__
except ImportError:
    # Usual frobbing of packages, due to Python's insane importing policy
    if __name__ == "__main__" and __package__ is None:
        package_root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(package_root))
    from scorch import scores
    from scorch import __version__


# Deal with piping output in a standard-compliant way
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

METRICS = {
    'MUC': scores.muc,
    'B³': scores.b_cubed,
    'CEAF_m': scores.ceaf_m,
    'CEAF_e': scores.ceaf_e,
    'BLANC': scores.blanc,
}


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

    This is basically done with depth 1 [disjoint-sets][1], which seemed a good trade-off between
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


def clusters_from_graph(
    nodes: ty.Iterable[ty.Hashable],
    edges: ty.Iterable[ty.Tuple[ty.Hashable, ty.Hashable]]
) -> ty.List[ty.Set]:
    '''Return the connex components of a graph.'''
    clusters = greedy_clustering(edges)
    if not clusters:
        return [{n} for n in nodes]
    non_sing = set.union(*clusters)
    singletons = [{n} for n in nodes if n not in non_sing]
    clusters.extend(singletons)
    return clusters


def clusters_from_json(fp) -> ty.List[ty.Set]:
    obj = json.load(fp)
    if obj["type"] == "graph":
        return clusters_from_graph(obj['mentions'], obj['links'])
    elif obj["type"] == "clusters":
        return [set(c) for n, c in obj["clusters"].items()]
    raise ValueError('Unsupported input format')


def process_files(gold_fp, sys_fp) -> ty.Iterable[str]:
    gold_clusters = clusters_from_json(gold_fp)
    sys_clusters = clusters_from_json(sys_fp)
    for name, metric in METRICS.items():
        R, P, F = metric(gold_clusters, sys_clusters)
        yield f'{name}:\tR={R}\tP={P}\tF₁={F}\n'
    conll_score = scores.conll2012(gold_clusters, sys_clusters)
    yield f'CoNLL-2012 average score: {conll_score}\n'


def process_dirs(gold_dir, sys_dir) -> ty.Iterable[str]:
    gold_path = pathlib.Path(gold_dir)
    sys_path = pathlib.Path(sys_dir)
    pairs = dict()  # ty.Dict[str, ty.Tuple[pathlib.Path, pathlib.Path]]
    for gold_file in gold_path.iterdir():
        try:
            sys_file = next(sys_path.glob(f'{gold_file.stem}*'))
        except StopIteration:
            raise ValueError(f'No matching sys file for {gold_file}')
        pairs[gold_file.stem] = (gold_file, sys_file)

    individual_results = []  # ty.List[str, ty.Dict[str, ty.Tuple[float, float, float]] int, int]
    pbar = tqdm.tqdm(
        pairs.items(),
        unit='document',
        desc='Scoring',
        unit_scale=True,
        unit_divisor=1024,
        dynamic_ncols=True,
        leave=False
    )
    for name, (gold_file, sys_file) in pbar:
        with gold_file.open() as gold_stream, sys_file.open() as sys_stream:
            gold_clusters = clusters_from_json(gold_stream)
            sys_clusters = clusters_from_json(sys_stream)
        r = {name: metric(gold_clusters, sys_clusters) for name, metric in METRICS.items()}
        individual_results.append(
            (
                name,
                r,
                sum(map(len, gold_clusters)),
                sum(map(len, sys_clusters)),
            ),
        )

    gold_sizes = np.fromiter((g_size for *_, g_size, _ in individual_results), dtype=int)
    sys_sizes = np.fromiter((s_size for *_, _, s_size in individual_results), dtype=int)

    results = {}
    for name in METRICS:
        all_R, all_P, all_F = (
            np.fromiter(s, float)
            for s in zip(*(r[name] for _, r, *_ in individual_results))
        )
        R = np.average(all_R, weights=gold_sizes)
        P = np.average(all_P, weights=sys_sizes)
        F = np.average(all_F, weights=gold_sizes+sys_sizes)
        results[name] = (R, P, F)
        yield f'{name}:\tR={R}\tP={P}\tF₁={F}\n'
    conll_score = mean(results[s][2] for s in ('MUC', 'B³', 'CEAF_e'))
    yield f'CoNLL-2012 average score: {conll_score}\n'


def main_entry_point(argv=None):
    arguments = docopt(__doc__, version=__version__, argv=argv)
    # Since there are no support for default positional arguments in
    # docopt yet. Might be useful for complex default values, too
    if arguments['<out-file>'] is None:
        arguments['<out-file>'] = '-'

    if arguments['<gold>'] != '-' and arguments['<sys>'] != '-':
        gold_path = pathlib.Path(arguments['<gold>'])
        sys_path = pathlib.Path(arguments['<sys>'])
        if gold_path.is_dir() and sys_path.is_dir():
            with smart_open(arguments['<out-file>'], 'w') as out_stream:
                out_stream.writelines(process_dirs(gold_path, sys_path))
            return None

    with contextlib.ExitStack() as stack:
        gold_stream = stack.enter_context(smart_open(arguments['<gold>']))
        sys_stream = stack.enter_context(smart_open(arguments['<sys>']))
        out_stream = stack.enter_context(smart_open(arguments['<out-file>'], 'w'))
        out_stream.writelines(process_files(gold_stream, sys_stream))


if __name__ == '__main__':
    sys.exit(main_entry_point())
