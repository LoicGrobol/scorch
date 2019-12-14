'''Unit tests for `scores.py`.'''
import pytest

from scorch import scores  # noqa


@pytest.fixture()
def Key():
    return [{'a', 'b', 'c'}, {'d', 'e', 'f', 'g'}]


@pytest.fixture()
def Response():
    return [{'a', 'b'}, {'c', 'd'}, {'f', 'g', 'h', 'i'}]


def test_trace(Key, Response):
    expected_K_wrt_R = [[{'a', 'b'}, {'c'}], [{'d'}, {'f', 'g'}, {'e'}]]
    expected_R_wrt_K = [[{'a', 'b'}], [{'c'}, {'d'}], [{'f', 'g'}, {'h'}, {'i'}]]
    K_wrt_R = [list(scores.trace(c, Response)) for c in Key]
    R_wrt_K = [list(scores.trace(c, Key)) for c in Response]
    assert K_wrt_R == expected_K_wrt_R
    assert R_wrt_K == expected_R_wrt_K


def test_muc_basic(Key, Response):
    R, P, F = scores.muc(Key, Response)
    assert R == pytest.approx(0.40)
    assert P == pytest.approx(0.40)
    assert F == pytest.approx(0.40)


def test_b_cubed_basic(Key, Response):
    R, P, F = scores.b_cubed(Key, Response)
    # Using the true value instead of the 10⁻² rounding
    assert R == pytest.approx(1 / 7 * 35 / 12)
    assert P == pytest.approx(0.50)
    # Note: According to Pradhan et al. (2014), `assert round(F, 2) == pytest.approx(0.46)` but this
    # is actually only true if we take their rounding of `0.42` for `R` and round `F` to two
    # decimals, too. Using a non-rounded `R`, `F` rounds to `0.45` instead
    assert round(F, 2) == pytest.approx(0.45)


def test_ceaf_m_basic(Key, Response):
    R, P, F = scores.ceaf_m(Key, Response)
    assert R == pytest.approx(4 / 7)
    assert P == pytest.approx(0.50)
    assert round(F, 2) == pytest.approx(0.53)


def test_ceaf_e_basic(Key, Response):
    R, P, F = scores.ceaf_e(Key, Response)
    assert R == pytest.approx(0.65)
    assert P == pytest.approx((4 / 5 + 1 / 2) / 3)
    assert round(F, 2) == pytest.approx(0.52)


def test_blanc_basic(Key, Response):
    R, P, F = scores.blanc(Key, Response)
    assert R == pytest.approx((2 / 9 + 8 / 12) / 2)
    assert P == pytest.approx((2 / 8 + 8 / 20) / 2)
    # Note: According to Pradhan et al. (2014), `assert round(F, 2) == pytest.approx(0.36)`
    # Here, as in B³, this is symptomatic of cascading rounding errors : if we don't round
    # `$R_c$` to `0.22` before computing `$F_c$`, rounding `$F_c$` yields `0.24` instead of
    # `0.23`, which cascades to the final `$F_{BLANC}$`.
    assert round(F, 2) == pytest.approx(0.37)


def test_conll2012_basic(Key, Response):
    score = scores.conll2012(Key, Response)
    assert round(score, 2) == pytest.approx(0.46)
