#! /usr/bin/env python3
r"""Compute CoNLL scores for coreference clustering as recommended by
*Scoring Coreference Partitions of Predicted Mentions: A Reference
Implementation* (Pradhan et al., 2014)

Usage:
  score <sys-file> <gold-file> [<out-file>]

Arguments:
  <sys-file>   system input file (json), `-` for standard input
  <gold-file>  gold input file (json), `-` for standard input
  <out-file>   output file (text), `-` for standard output [default: -]

Options:
  -h, --help  Show this screen.

Formats
The input files should be JSON files with a "type" key at top-level
  - If "type" if "graph", then top-level should have at top-level
    - A "mentions" key containing a list of singleton mention identifiers
    - A "links" key containing a list of pairs of corefering mention
      identifiers
  - If "type" is "clusters", then top-level should have a "clusters" key
    containing a mapping from clusters ids to cluster contents (as lists of
    mention identifiers).

Of course the system and gold files should use the same set of mention identifiers…

Example:
  `score sys.json gold.json out`
"""

__version__ = 'score 0.0.0'

import contextlib
import signal
import sys
import json

import numpy as np
import typing as ty

from docopt import docopt
from scipy.optimize import linear_sum_assignment

# Deal with piping output in a standard-compliant way
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


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
    '''Create transitive closure clusters from a set of edges.'''
    triaged = dict()  # type: ty.Dict[ty.Hashable, int]
    next_n = 0
    for foot, head in links:
        f_cluster = triaged.get(foot, None)
        h_cluster = triaged.get(head, None)
        if f_cluster is None:
            if h_cluster is None:
                next_n += 1
                triaged[head] = next_n
                triaged[foot] = next_n
            else:
                triaged[foot] = h_cluster
        else:
            if h_cluster is None:
                triaged[head] = f_cluster
            else:
                if f_cluster != h_cluster:  # merge `f_cluster` and `h_cluster`
                    for e, c in triaged.items():
                        if c == f_cluster:
                            triaged[e] = h_cluster
    clusters = dict()  # type: ty.Dict[int, ty.List]
    for e, n in triaged.items():
        c = clusters.get(n, None)
        if c is None:
            clusters[n] = [e]
        else:
            c.append(e)
    return [set(c) for c in clusters.values()]


def clusters_from_graph(nodes: ty.Iterable[ty.Hashable],
                        edges: ty.Iterable[ty.Tuple[ty.Hashable, ty.Hashable]]) -> ty.List[ty.Set]:
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


def trace(cluster: ty.Set, partition: ty.Iterable[ty.Set]) -> ty.Iterable[ty.Set]:
    r'''
    Return the partition of `#cluster` induced by `#partition`, that is
    ```math
    \{C∩A|A∈P\} ∪ \{\{x\}|x∈C∖∪P\}
    ```
    Where $C$ is `#cluster` and $P$ is `#partition`.

    This assume that the elements of `#partition` are indeed pairwise disjoint'''
    remaining = set(cluster)
    for a in partition:
        common = remaining.intersection(a)
        if common:
            remaining.difference_update(common)
            yield common
    for x in sorted(remaining):
        yield set((x,))


def muc(key: ty.List[ty.Set], response: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    r'''
    Compute the MUC `$(R, P, F₁)$` scores for a `#response` clustering given a `#key`
    clustering`, that is
    ```math
    R &= \frac{∑_{k∈K}(#k-#p(k, R))}{∑_{k∈K}(#r-1)}\\
    P &= \frac{∑_{r∈R}(#r-#p(r, K))}{∑_{r∈R}(#r-1)}\\
    F &= 2*\frac{PR}{P+R}
    ```
    with `$p(x, E)=\{x∩A|A∈E\}$`
    '''
    R = sum(len(k) - sum(1 for _ in trace(k, response)) for k in key)/sum(len(k)-1 for k in key)
    P = sum(len(r)-sum(1 for _ in trace(r, key)) for r in response)/sum(len(r)-1 for r in response)
    F = (2*P*R)/(P+R)
    return R, P, F


def b_cubed(key: ty.List[ty.Set], response: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    '''
    Compute the B³ `$(R, P, F₁)$` scores for a `#response` clustering given a `#key`
    clustering`, that is
    ```math
    R &= \frac{∑_{k∈K}∑_{r∈R}\frac{(#k∩r)²}{#k}}{∑_{k∈K}#k}\\
    P &= \frac{∑_{r∈R}∑_{k∈K}\frac{(#r∩k)²}{#r}}{∑_{r∈R}#r}\\
    F &= 2*\frac{PR}{P+R}
    ```
    '''
    R = (sum(len(k.intersection(r))**2/len(k) for k in key for r in response) /
         sum(len(k) for k in key))
    P = (sum(len(r.intersection(k))**2/len(r) for r in response for k in key) /
         sum(len(r) for r in response))
    F = (2*P*R)/(P+R)
    return R, P, F


def ceaf(response: ty.List[ty.Set], key: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    '''Compute the CEAF $(P, R, F₁)$ scores for a `#response` clustering given a `#key`
       clustering`.'''
    mentions = sorted(m for c in key for m in c)


def main_entry_point(argv=None):
    arguments = docopt(__doc__, version=__version__, argv=argv)
    # Since there are no support for default positional arguments in
    # docopt yet. Might be useful for complex default values, too
    if arguments['<out-file>'] is None:
        arguments['<out-file>'] = '-'

    with smart_open(arguments['<sys-input>']) as in_stream:
        sys_clusters = clusters_from_json(in_stream)

    with smart_open(arguments['<gold-input>']) as in_stream:
        gold_clusters = clusters_from_json(in_stream)

    P, R, F = muc(sys_clusters, gold_clusters)

    with smart_open(arguments['<out-file>'], 'w') as out_stream:
        out_stream.write(f'MUC Score\nP: {P}\tR: {R}\tF₁: {F}\n')


if __name__ == '__main__':
    sys.exit(main_entry_point())
