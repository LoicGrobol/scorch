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
    return str(test_file.resolve().parent/'fixtures'/'json'/'gold.json')


@pytest.fixture()
def sys_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return str(test_file.resolve().parent/'fixtures'/'json'/'sys.json')


@pytest.fixture()
def out_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return str(test_file.resolve().parent/'fixtures'/'json'/'out.txt')


def test_greedy_clustering(links):
    case = unittest.TestCase()
    expected_clusters = [{1, 2, 3}, {4, 5, 6}, {7, 8}]
    clusters = scorch.greedy_clustering(links)
    print(clusters)
    case.assertCountEqual(clusters, expected_clusters)


def test_process_files(gold_file, sys_file, out_file, tmpdir):
    with open(out_file) as stream:
        expected_output = stream.read()
    scorch.main_entry_point([gold_file, sys_file, str(tmpdir.join('out.txt'))])
    with tmpdir.join('out.txt').open() as stream:
        output = stream.read()
    assert output == expected_output
