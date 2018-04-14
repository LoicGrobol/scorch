Scorch<a id="footnote-0-1-backref" href="#footnote-0-1">¹</a>
======
[![Build Status](https://travis-ci.org/LoicGrobol/scorch.svg?branch=master)](https://travis-ci.org/LoicGrobol/scorch)
[![PyPI](https://img.shields.io/pypi/v/scorch.svg)](https://pypi.org/project/scorch)

This is an alternative implementation of the coreference scorer for the CoNLL-2011/2012 shared tasks on coreference resolution.

It aims to be more straightforward than the [reference implementation][ref-scorer], while maintaining as much compatibility with it as possible.

The implementations of the various scores are as close as possible from the formulas used by <a href="#pradhan2014scoring">Pradhan et al. (2014)</a>, with the edge cases for BLANC taken from <a href="recasens2011BLANC">Recasens and Hovy (2011)</a>.

---
<sub><a id="footnote-0-1" href="#footnote-0-1-backref">1.</a> **S**corer for **cor**eference **ch**ains.</sub>

[ref-scorer]: https://github.com/conll/reference-coreference-scorers

## Usage
```bash
scorch gold.json sys.json out.txt
```

## Install
### With pip
```
python3 -m pip install scorch
```

### From git
Download from master with
```bash
git clone https://github.com/LoicGrobol/scorch.git
```

Install with
```bash
python3 -m pip install .
```

Alternatively, just running `scorch.py` without installing should work as long as you have all the dependencies installed
```
python3 scorch.py -h
```

## Formats
### Single document
The input files should be JSON files with a `"type"` key at top-level

  - If `"type"` is `"graph"`, then top-level should have at top-level
     - A `"mentions"` key containing a list of all mention identifiers
     - A `"links"` key containing a list of pairs of corefering mention identifiers
  - If `"type"` is `"clusters"`, then top-level should have a `"clusters"` key containing a mapping
    from clusters ids to cluster contents (as lists of mention identifiers).

Of course the system and gold files should use the same set of mention identifiers…

### Multiple documents
If the inputs are directories, files with the same base name (excluding extension) as those present
in the gold directory are expected to be present in the sys directory, with exactly one sys file for
each gold file.
In that case, the output scores will be the micro-average of the individual files scores, ie their
arithmetic means weighted by the relative numbers of

  - Gold mentions for Recall
  - System mentions for Precision
  - The sum of the previous two for F₁

This is different from the reference interpretation where

  - **MUC** weighting ignores mentions in singleton entities
    - This should not make any difference for the CoNLL-2012 dataset, since singleton entities are not annotated.
    - For datasets with singletons, the shortcomings of MUC are well known, so this score
     shouldn't matter much
  - **BLANC** is calculated by micro-averaging coreference and non-coreference separately, using
    the number of links as weights instead of the number of mentions.
    - This is roughly equivalent to weighting coreference scores per document by their number of
      non-singleton clusters and non-coreference scores by the square of their number of mentions.
      This give disproportionate importance to large documents, which is not desirable
      in heterogenous corpora

The CoNLL average score is the arithmetic mean of the global MUC, B³ and CEAFₑ F₁ scores.

## Sources
  - <a id="pradhan2014scoring" />**Scoring Coreference Partitions of Predicted Mentions: A Reference Implementation.** Sameer Pradhan, Xiaoqiang Luo, Marta Recasens, Eduard Hovy, Vincent Ng and Michael Strube. *Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics*, Baltimore, MD, June 2014. ([pdf](http://aclweb.org/anthology/P/P14/P14-2006.pdf))
  - <a id="recasens2011BLANC" />**BLANC: Implementing the Rand Index for Coreference Evaluation.** Marta Recasens and Eduard Hovy In: *Natural Language Engineering* 17 (4). Cambridge University Press, 2011. ([pdf](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.300.9229&rep=rep1&type=pdf))
  - <a id="luo2014BLANC" /> **An Extension of BLANC to System Mentions.** Xiaoqiang Luo, Sameer Pradhan, Marta Recasens and Eduard Hovy. *Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics*, Baltimore, MD, June 2014. ([pdf](http://aclweb.org/anthology/P/P14/P14-2005.pdf))
  - The version of the Kuhn-Munkres algorithm used for the CEAF scores uses [scipy.optimize.linear_sum_assignment](https://docs.scipy.org/doc/latest/reference/generated/scipy.optimize.linear_sum_assignment.html), with $-ϕ_n$ as cost function.


## License

Unless otherwise specified (see <a href="#license-exceptions">below</a>), the following licence (the so-called “MIT License”) applies to all the files in this repository.
See also [LICENSE.md](LICENSE.md).

```
Copyright 2018 Loïc Grobol <loic.grobol@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### <a id="license-exceptions">License exceptions</a>

  - The reference scorer testcases located in [`tests/fixtures/conll/`](tests/fixtures/conll/datafiles) are distributed under the [Creative Commons Attribution ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/)
    - **Copyright** © 2011- Sameer Pradhan pradhan \<at\> cemantix.org
    - **Authors**
        * Emili Sapena, Universitat Politècnica de Catalunya, <http://www.lsi.upc.edu/~esapena>, esapena \<at\> lsi.upc.edu
        * Sameer Pradhan, http://cemantix.org, pradhan \<at\> cemantix.org
        * Sebastian Martschat, sebastian.martschat \<at\> h-its.org
        * Xiaoqiang Luo, xql \<at\> google.com
    - **Origin** <http://conll.github.io/reference-coreference-scorers>

    These files are taken verbatim from the 8.0.1 of the official CoNLL scorer at <https://github.com/conll/reference-coreference-scorers/releases>
