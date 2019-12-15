import typing as ty

import hypothesis
import pytest

from scorch import scores  # noqa
from tests.utils import clusterings


@hypothesis.given(clusters=clusterings(max_size=256))
@pytest.mark.parametrize(
    "metric", [scores.b_cubed, scores.ceaf_m, scores.ceaf_e, scores.blanc]
)
def test_perfect(metric, clusters: ty.Sequence[ty.Set[int]]):
    """Test that all the scores are `1.0` for a perfect system output."""
    assert metric(clusters, clusters) == (1.0, 1.0, 1.0)


# TODO: there might be a hypothesis invocation to integrate this in `test_perfect`
@hypothesis.given(clusters=clusterings(max_size=256, allow_singletons=False))
def test_perfect_muc(clusters: ty.Sequence[ty.Set[int]]):
    """Test that all the scores are `1.0` for a perfect system output for MUC"""
    assert scores.muc(clusters, clusters) == (1.0, 1.0, 1.0)


@hypothesis.given(key=clusterings(max_size=256), response=clusterings(max_size=256))
def test_blanc_consistency(key, response):
    fast_blanc = scores.blanc(key, response, fast=True)
    slow_blanc = scores.blanc(key, response, fast=False)
    assert fast_blanc == slow_blanc
