from scorer import scorer  # noqa


def test_trace():
    K = [{'a', 'b', 'c'}, {'d', 'e', 'f', 'g'}]
    R = [{'a', 'b'}, {'c', 'd'}, {'f', 'g', 'h', 'i'}]
    expected_K_wrt_R = [[{'a', 'b'}, {'c'}],
                        [{'d'}, {'f', 'g'}, {'e'}]]
    expected_R_wrt_K = [[{'a', 'b'}],
                        [{'c'}, {'d'}],
                        [{'f', 'g'}, {'h'}, {'i'}]]
    K_wrt_R = [list(scorer.trace(c, R)) for c in K]
    R_wrt_K = [list(scorer.trace(c, K)) for c in R]
    assert K_wrt_R == expected_K_wrt_R
    assert R_wrt_K == expected_R_wrt_K
