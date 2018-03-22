'''Unit tests for `scorch.py`.'''
import pathlib
import unittest

import pytest

from scorch import scorch  # noqa


@pytest.fixture()
def links():
    return [
        (1, 2),
        (2, 3),
        (4, 5),
        (5, 6),
        (4, 5),
        (5, 4),
        (7, 8),
    ]


@pytest.fixture()
def gold_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'gold.json').open()


@pytest.fixture()
def sys_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'sys.json').open()


@pytest.fixture()
def out_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'out.txt').open()


def test_greedy_clustering(links):
    case = unittest.TestCase()
    expected_clusters = [{1, 2, 3}, {4, 5, 6}, {7, 8}]
    clusters = scorch.greedy_clustering(links)
    print(clusters)
    case.assertCountEqual(clusters, expected_clusters)


def test_process_files(gold_file, sys_file, out_file):
    expected_output = out_file.read()
    output = ''.join(scorch.process_files(gold_file, sys_file))
    assert output == expected_output
