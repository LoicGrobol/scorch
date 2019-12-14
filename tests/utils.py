import hypothesis
from hypothesis import strategies as st

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