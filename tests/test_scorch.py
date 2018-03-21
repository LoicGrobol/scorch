'''Unit tests for `scorch.py`.'''
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


def test_greedy_clustering(links):
    case = unittest.TestCase()
    expected_clusters = [{1, 2, 3}, {4, 5, 6}, {7, 8}]
    clusters = scorch.greedy_clustering(links)
    print(clusters)
    case.assertCountEqual(clusters, expected_clusters)
