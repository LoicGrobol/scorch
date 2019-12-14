import typing as ty

import hypothesis
from hypothesis import strategies as st
import pytest

from scorch import scores  # noqa


@st.composite
def clusterings(draw, max_size=None, allow_singletons=True):
    n_elements = draw(st.integers(min_value=1, max_value=max_size))
    n_clusters = draw(st.integers(min_value=1, max_value=n_elements))
    affectations = draw(
        st.lists(
            st.integers(min_value=0, max_value=n_clusters - 1),
            min_size=n_elements,
            max_size=n_elements,
        )
    )
    clusters = [[] for _ in range(n_clusters)]
    for i, n in enumerate(affectations):
        clusters[n].append(i)
    # FIXME: this removes empty clusters but it would be better to avoid generating them at all
    res = [set(c) for c in clusters if c]
    if not allow_singletons:
        res = [c for c in clusters if len(c) > 1]
    hypothesis.assume(res)
    return res


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
