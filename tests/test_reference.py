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

DEFAULT_CONFIG = pathlib.Path(__file__).parent / 'fixtures/conll/conll.json'


def load_testcases(config_path):
    config_path = pathlib.Path(config_path)
    with config_path.open() as config_stream:
        config = json.load(config_stream)
    for testcase_id, testcase in config.items():
        with (config_path.parent / testcase['key_file']).open() as key_stream:
            key_file = list(l.strip() for l in key_stream)
        with (config_path.parent / testcase['response_file']).open() as response_stream:
            response_file = list(l.strip() for l in response_stream)
        yield (testcase_id, key_file, response_file, testcase['expected_metrics'])


@pytest.fixture(params=list(load_testcases(DEFAULT_CONFIG)))
def testcase(request):
    testcase_id, key_file, response_file, raw_metrics = request.param
    key_clusters = [set(c) for c in next(conll.parse_file(key_file))[1].values()]
    response_clusters = [
        set(c) for c in next(conll.parse_file(response_file))[1].values()
    ]
    expected_metrics = {
        metric: [eval(v) if isinstance(v, str) else v for v in rpf]
        for metric, rpf in raw_metrics.items()
    }
    yield (testcase_id, key_clusters, response_clusters, expected_metrics)


def test_offical_case(testcase):
    testcase_id, key_clusters, response_clusters, expected_metrics = testcase
    for m, rpf in expected_metrics.items():
        R, P, F = METRICS[m](key_clusters, response_clusters)
        R_e, P_e, F_e = rpf
        assert R == pytest.approx(R_e)
        assert P == pytest.approx(P_e)
        assert F == pytest.approx(F_e)
