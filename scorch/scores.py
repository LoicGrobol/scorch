'''CoNLL-2011/2012 scores for coreference detection.'''

import itertools as it
import typing as ty

import numpy as np

from scipy.optimize import linear_sum_assignment

# OPTIMIZE: This could be made faster by dealing separately with singletons
# OPTIMIZE: This could be made faster (in average) by sorting `cluster_lst` by decreasing length
def links_from_clusters(clusters: ty.Iterable[ty.Set]
                        ) -> ty.Tuple[ty.List[ty.Tuple[ty.Hashable, ty.Hashable]],
                                      ty.List[ty.Tuple[ty.Hashable, ty.Hashable]]]:
    r'''
    Return a `(coreference_links, non-coreference_links)` tuple corresponding to a clustering.
    '''
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

    if not C_k or not C_r:
        R_c, P_c, half_F_c = (1., 1., 1.) if C_k == C_r else (0., 0., 0.)
    else:
        R_c, P_c = len(T_c)/len(C_k), len(T_c)/len(C_r)
        half_F_c = P_c*R_c/(P_c+R_c)

    if not N_k or not N_r:
        R_n, P_n, half_F_n = (1., 1., 1.) if N_k == N_r else (0., 0., 0.)
    else:
        R_n, P_n = len(T_n)/len(N_k), len(T_n)/len(N_r)
        half_F_n = P_n*R_n/(P_n+R_n)

    # Quirk: when GOLD (key) is unbalanced, we break the symmetry
    if not C_k:
        return R_n, P_n, 2*half_F_n
    if not N_k:
        return R_c, P_c, 2*half_F_c

    return (R_c+R_n)/2, (P_c+P_n)/2, half_F_c+half_F_n
