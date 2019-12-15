import pathlib
import timeit
import typing as ty

from scorch import scores
from scorch import main as scorch


tests_dir = pathlib.Path(__file__).resolve().parent


def test_metrics(
    clusters: ty.Sequence[ty.Set[ty.Hashable]], num_runs: int = 100, repeat: int = 1
):
    print(f"Testing metrics speed: {num_runs} calls, best of {repeat}")
    print("metric\ttotal\tper call")
    for (name, fun) in {
        **scorch.METRICS,
        "Slow BLANC": lambda x, y: scores.blanc(x, y, False),
    }.items():
        runtime = min(
            timeit.repeat(
                "fun(clusters, clusters)",
                globals={"fun": fun, "clusters": clusters},
                number=num_runs,
                repeat=repeat,
            )
        )
        print(f"{name}\t{runtime}\t{runtime/num_runs}")


with open(tests_dir / "fixtures" / "clusters.json") as in_stream:
    clusters = scorch.clusters_from_json(in_stream)

test_metrics(clusters)
