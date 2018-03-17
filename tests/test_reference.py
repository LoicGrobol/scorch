'''Unit tests for `scores.py`.'''
import pathlib
import json

import pytest

from scorch import scores  # noqa
from scorch import conll  # noqa


METRICS = {
    "muc": scores.muc,
    "b_cubed": scores.b_cubed,
    "ceaf_m": scores.ceaf_m,
    "ceaf_e": scores.ceaf_e,
    "blanc": scores.blanc,
}


@pytest.fixture()
def testcases(request):
    config_path = pathlib.Path(request.config.rootdir)/'fixtures/conll/datafiles'
    with config_path.open() as config_stream:
        config = json.load(config_stream)
    for testcase_id, testcase in config.items():
        with (config_path/testcase['key_file']).open() as key_stream:
            key_file = list(l.strip() for l in key_stream)
            key_clusters = list(conll.parse_file(key_file))[0][1]
        with (config_path/testcase['response_file']).open() as response_stream:
            response_file = list(l.strip() for l in response_stream)
            response_clusters = list(conll.parse_file(response_file))[0][1]

        expected_metrics = {metric: [eval(v) if isinstance(v, str) else v for v in rpf]
                            for metric, rpf in testcase['expected_metrics']}
        yield (testcase_id, key_clusters, response_clusters, expected_metrics)


def test_offical_cases(testcases):
    for testcase_id, key_clusters, response_clusters, expected_metrics in testcases:
        for m, rpf in expected_metrics.items():
            assert METRICS[m] == rpf
