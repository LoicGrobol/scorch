#! /usr/bin/env python3
r"""Compute CoNLL scores for coreference clustering as recommended by
*Scoring Coreference Partitions of Predicted Mentions: A Reference
Implementation* (Pradhan et al., 2014)

Usage:
  scorch <sys-file> <gold-file> [<out-file>]

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
  `scorch sys.json gold.json out`
"""

__version__ = 'scorch 0.0.0'

import contextlib
import json
import signal
import sys

import itertools as it
import typing as ty

import numpy as np

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


# OPTIMIZE: This could be made faster by dealing separately with singletons
# OPTIMIZE: This could be made faster (in average) by sorting `cluster_lst` by decreasing length
def links_from_clusters(clusters: ty.Iterable[ty.Set]
                        ) -> ty.Tuple[ty.List[ty.Tuple[ty.Hashable, ty.Hashable]],
                                      ty.List[ty.Tuple[ty.Hashable, ty.Hashable]]]:
    clusters_lst = list(clusters)
    elements = sorted(set.union(*clusters_lst))
    C = []
    N = []
    for i, j in it.combinations(elements, 2):
        if i == j:
            continue
        elif any(c for c in clusters_lst if i in c and j in c):
            C.append((i, j))
        else:
            N.append((i, j))
    return C, N


def trace(cluster: ty.Set, partition: ty.Iterable[ty.Set]) -> ty.Iterable[ty.Set]:
    r'''
    Return the partition of `#cluster` induced by `#partition`, that is
    ```math
    \{C∩A|A∈P\} ∪ \{\{x\}|x∈C∖∪P\}
    ```
    Where `$C$` is `#cluster` and `$P$` is `#partition`.

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
    R &= \frac{∑_{k∈K}(\#k-\#p(k, R))}{∑_{k∈K}(\#k-1)}\\
    P &= \frac{∑_{r∈R}(\#r-\#p(r, K))}{∑_{r∈R}(\#r-1)}\\
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
    R &= \frac{∑_{k∈K}∑_{\∈R}\frac{(\#k∩r)²}{#k}}{∑_{k∈K}\#k}\\
    P &= \frac{∑_{r∈R}∑_{k∈K}\frac{(\#r∩k)²}{#r}}{∑_{r∈R}\#r}\\
    F &= 2*\frac{PR}{P+R}
    ```
    '''
    R = (sum(len(k.intersection(r))**2/len(k) for k in key for r in response) /
         sum(len(k) for k in key))
    P = (sum(len(r.intersection(k))**2/len(r) for r in response for k in key) /
         sum(len(r) for r in response))
    F = (2*P*R)/(P+R)
    return R, P, F


def ceaf(key: ty.List[ty.Set],
         response: ty.List[ty.Set],
         score: ty.Callable[[ty.Set, ty.Set], float]) -> ty.Tuple[float, float, float]:
    r'''
    Compute the CEAF `$(R, P, F₁)$` scores for a `#response` clustering given a `#key`
    clustering` using the `#score` alignment score function, that is
    ```math
    R &= \frac{∑_{k∈K}C(k, A(k))}{∑_{k∈K}\#k}\\
    P &=  \frac{∑_{r∈R}C(r, A⁻¹(r))}{∑_{r∈R}\#r}\\
    F &= 2*\frac{PR}{P+R}
    ```
    Where `$C$` is `#score` and `$A$` is the one-to-one mapping from key clusters to
    response clusters that maximizes `$∑_{k∈K}C(k, A(k))$`.
    '''
    cost_matrix = np.array([[-score(k, r) for r in response] for k in key])
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_score = -cost_matrix[row_ind, col_ind].sum()
    print(total_score, sum(len(k) for k in key))
    R = total_score/sum(score(k, k) for k in key)
    P = total_score/sum(score(r, r) for r in response)
    F = (2*P*R)/(P+R)
    return R, P, F


def ceaf_m(key: ty.List[ty.Set], response: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    r'''
    Compute the CEAF_m `$(R, P, F₁)$` scores for a `#response` clustering given a `#key`
    clustering`, that is the CEAF score for the `$Φ_3$` score function
    ```math
    Φ_3: (k, r) ⟼ \#k∩r
    ```
    '''
    def Φ_3(k, r):
        return len(k.intersection(r))
    return ceaf(key, response, Φ_3)


def ceaf_e(key: ty.List[ty.Set], response: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    r'''
    Compute the CEAF_m `$(R, P, F₁)$` scores for a `#response` clustering given a `#key`
    clustering`, that is the CEAF score for the `$Φ₄$` score function
    (aka the Sørensen–Dice coefficient).
    ```math
    Φ₄: (k, r) ⟼ \frac{2×\#k∩r}{\#k+\#r}
    Note: this use the original (Luo, 2005) definition as opposed to the (Pradhan et al. 2014) one
    which inlines the denominators.
    ```
    '''
    def Φ_4(k, r):
        return 2*len(k.intersection(r))/(len(k)+len(r))
    return ceaf(key, response, Φ_4)


# COMBAK: Check the numeric stability
def blanc(key: ty.List[ty.Set], response: ty.List[ty.Set]) -> ty.Tuple[float, float, float]:
    r'''
    Return the BLANC `$(R, P, F)$` scores for a `#response` clustering given a `#key`
    clustering`, that is.
    '''
    C_k, N_k = map(set, links_from_clusters(key))
    C_r, N_r = map(set, links_from_clusters(response))

    T_c = C_k.intersection(C_r)
    T_n = N_k.intersection(N_r)

    R_c, P_c = len(T_c)/len(C_k), len(T_c)/len(C_r)
    half_F_c = P_c*R_c/(P_c+R_c)  # No need to multiply this by 2 to divide right after

    R_n, P_n = len(T_n)/len(N_k), len(T_n)/len(N_r)
    half_F_n = P_n*R_n/(P_n+R_n)

    return (R_c+R_n)/2, (P_c+P_n)/2, half_F_c+half_F_n


# def main_entry_point(argv=None):
#     arguments = docopt(__doc__, version=__version__, argv=argv)
#     # Since there are no support for default positional arguments in
#     # docopt yet. Might be useful for complex default values, too
#     if arguments['<out-file>'] is None:
#         arguments['<out-file>'] = '-'
#
#     with smart_open(arguments['<sys-input>']) as in_stream:
#         sys_clusters = clusters_from_json(in_stream)
#
#     with smart_open(arguments['<gold-input>']) as in_stream:
#         gold_clusters = clusters_from_json(in_stream)
#
#     R, P, F = muc(sys_clusters, gold_clusters)
#
#     with smart_open(arguments['<out-file>'], 'w') as out_stream:
#         out_stream.write(f'MUC Score\nP: {P}\tR: {R}\tF₁: {F}\n')
#
#
# if __name__ == '__main__':
#     sys.exit(main_entry_point())
