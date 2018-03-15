import pytest

from scorer import scorer  # noqa


@pytest.fixture()
def K():
    return [{'a', 'b', 'c'}, {'d', 'e', 'f', 'g'}]


@pytest.fixture()
def R():
    return [{'a', 'b'}, {'c', 'd'}, {'f', 'g', 'h', 'i'}]


def test_trace(K, R):
    expected_K_wrt_R = [[{'a', 'b'}, {'c'}],
                        [{'d'}, {'f', 'g'}, {'e'}]]
    expected_R_wrt_K = [[{'a', 'b'}],
                        [{'c'}, {'d'}],
                        [{'f', 'g'}, {'h'}, {'i'}]]
    K_wrt_R = [list(scorer.trace(c, R)) for c in K]
    R_wrt_K = [list(scorer.trace(c, K)) for c in R]
    assert K_wrt_R == expected_K_wrt_R
    assert R_wrt_K == expected_R_wrt_K


def test_muc(K, R):
    R, P, F = scorer.muc(K, R)
    assert R == pytest.approx(0.40)
    assert P == pytest.approx(0.40)
    assert F == pytest.approx(0.40)
