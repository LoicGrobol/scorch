import pytest

from scorer import scorer  # noqa


@pytest.fixture()
def Key():
    return [{'a', 'b', 'c'}, {'d', 'e', 'f', 'g'}]


@pytest.fixture()
def Response():
    return [{'a', 'b'}, {'c', 'd'}, {'f', 'g', 'h', 'i'}]


def test_trace(Key, Response):
    expected_K_wrt_R = [[{'a', 'b'}, {'c'}],
                        [{'d'}, {'f', 'g'}, {'e'}]]
    expected_R_wrt_K = [[{'a', 'b'}],
                        [{'c'}, {'d'}],
                        [{'f', 'g'}, {'h'}, {'i'}]]
    K_wrt_R = [list(scorer.trace(c, Response)) for c in Key]
    R_wrt_K = [list(scorer.trace(c, Key)) for c in Response]
    assert K_wrt_R == expected_K_wrt_R
    assert R_wrt_K == expected_R_wrt_K


def test_muc_basic(Key, Response):
    R, P, F = scorer.muc(Key, Response)
    assert R == pytest.approx(0.40)
    assert P == pytest.approx(0.40)
    assert F == pytest.approx(0.40)


def test_b_cubed_basic(Key, Response):
    R, P, F = scorer.b_cubed(Key, Response)
    assert R == pytest.approx(1/7*35/12)  # Using the true value instead of the 10⁻² rounding
    assert P == pytest.approx(0.50)
    # Note: According to Pradhan et al. (2014), `assert round(F, 2) == pytest.approx(0.46)` but this
    # is actually only true if we take their rounding of `0.42` for `R` and round `F` to two
    # decimals, too. Using a non-rounded `R`, `F` rounds to `0.45` instead
    assert round(F, 2) == pytest.approx(0.45)
