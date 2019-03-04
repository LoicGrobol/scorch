'''Unit tests for `scorch.py`.'''
import pathlib
import unittest

import pytest

from scorch import main  # noqa


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
    return (test_file.resolve().parent/'fixtures'/'json'/'single'/'gold.json').open()


@pytest.fixture()
def sys_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'single'/'sys.json').open()


@pytest.fixture()
def out_file(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'single'/'out.txt').open().read()


@pytest.fixture()
def gold_dir(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'multiple'/'gold')


@pytest.fixture()
def sys_dir(request):
    test_file = pathlib.Path(request.module.__file__)
    return (test_file.resolve().parent/'fixtures'/'json'/'multiple'/'sys')


# @pytest.fixture()
# def out_file_multiple(request):
#     test_file = pathlib.Path(request.module.__file__)
#     return (test_file.resolve().parent/'fixtures'/'json'/'multiple'/'out.txt').open().read()


def test_greedy_clustering(links):
    case = unittest.TestCase()
    expected_clusters = [{1, 2, 3}, {4, 5, 6}, {7, 8}]
    clusters = main.greedy_clustering(links)
    case.assertCountEqual(clusters, expected_clusters)


def test_process_files(gold_file, sys_file, out_file):
    expected_output = out_file
    output = ''.join(main.process_files(gold_file, sys_file))
    assert output == expected_output


# def test_process_dirs(gold_dir, sys_dir, out_file_multiple):
#     expected_output = out_file_multiple
#     output = ''.join(main.process_dirs(gold_dir, sys_dir))
#     assert output == expected_output
