import itertools as it
import pathlib
import timeit
import typing as ty

from scorch import main as scorch


tests_dir = pathlib.Path(__file__).resolve().parent


def test_metrics(
    clusters: ty.Sequence[ty.Set[ty.Hashable]], num_runs: int = 100, repeat: int = 5
):
    print(f"Testing metrics speed: {num_runs} calls, best of {repeat}")
    print("metric\ttotal\tper call")
    for (name, fun) in scorch.METRICS.items():
        runtime = min(
            timeit.repeat(
                "fun(clusters, clusters)",
                globals={"fun": fun, "clusters": clusters},
                number=num_runs,
                repeat=repeat,
            )
        )
        print(f"{name}\t{runtime}\t{runtime/num_runs}")


def remap_clusterings(
    clusterings: ty.Sequence[ty.Sequence[ty.Set[ty.Hashable]]],
) -> ty.List[ty.List[ty.Set[int]]]:
    """Remap clusterings of arbitrary elements to clusterings of integers for faster operations."""
    elts = set(e for clusters in clusterings for c in clusters for e in c)
    elts_map = {e: i for i, e in enumerate(elts)}
    res = []
    for clusters in clusterings:
        remapped_clusters = []
        for c in clusters:
            remapped_c = set(elts_map[e] for e in c)
            remapped_clusters.append(remapped_c)
        res.append(remapped_clusters)
    return res


with open(tests_dir / "fixtures" / "clusters.json") as in_stream:
    clusters = scorch.clusters_from_json(in_stream)

test_metrics(clusters)

remapped = remap_clusterings([clusters])[0]

test_metrics(remapped)
