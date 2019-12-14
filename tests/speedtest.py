import pathlib
import timeit

from scorch import main as scorch


tests_dir = pathlib.Path(__file__).resolve().parent


with open(tests_dir / "fixtures" / "clusters.json") as in_stream:
    clusters = scorch.clusters_from_json(in_stream)

num_runs = 100
repeat = 5

print(f"Testing metrics speed: {num_runs} calls × {repeat} repetitions")
print("metric\ttotal\tper call")
for (name, fun) in scorch.METRICS.items():
    runtime = min(
        timeit.repeat(
            "fun(clusters, clusters)",
            globals={"fun": fun, "clusters": clusters},
            number=num_runs,
            repeat=repeat
        )
    )
    print(f"{name}\t{runtime}\t{runtime/num_runs}")
