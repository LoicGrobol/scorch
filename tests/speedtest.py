import pathlib
import timeit
import typing as ty

from scorch import scores
from scorch import main as scorch


tests_dir = pathlib.Path(__file__).resolve().parent

Clustering = ty.Sequence[ty.Set[ty.Hashable]]


def test_metrics(clusters: Clustering, num_runs: int = 100, repeat: int = 5):
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


def test_blanc_speedup(clusters: Clustering, num_runs: int = 100, repeat: int = 5):
    print(f"Testing BLANC speedup: {num_runs} calls, best of {repeat}")
    slow_runtime = min(
        timeit.repeat(
            "blanc(clusters, clusters, False)",
            globals={"fun": scores.blanc, "clusters": clusters},
            number=num_runs,
            repeat=repeat,
        )
    )
    print(f"Slow\t{slow_runtime} s ({slow_runtime/num_runs} s/call)")
    fast_runtime = min(
        timeit.repeat(
            "blanc(clusters, clusters,)",
            globals={"fun": scores.blanc, "clusters": clusters},
            number=num_runs,
            repeat=repeat,
        )
    )
    print(f"Fast\t{fast_runtime} s ({fast_runtime/num_runs} s/call)")
    print(f"Speedup: ×{slow_runtime/fast_runtime}")


with open(tests_dir / "fixtures" / "clusters.json") as in_stream:
    clusters = scorch.clusters_from_json(in_stream)

test_metrics(clusters)

test_blanc_speedup(clusters)