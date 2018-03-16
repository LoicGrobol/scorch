Scorch<a id="footnote-0-1-backref" href="#footnote-0-1">¹</a>
======

This is an alternative implementation of the coreference scorer for the CoNLL-2011/2012 shared tasks on coreference resolution.

It aims to be more straightforward than the [reference implementation][ref-scorer], while maintaining as much compatibility with it as possible.

The implementations of the various scores are as close as possible from the formulas used by Pradhan et al. (2014).

---
<sub><a id="footnote-0-1" href="#footnote-0-1-backref">1.</a> **S**corer for **co**reference **ch**ains.</sub>

[ref-scorer]: https://github.com/conll/reference-coreference-scorers


## Sources
  - **Scoring Coreference Partitions of Predicted Mentions: A Reference Implementation.** Sameer Pradhan, Xiaoqiang Luo, Marta Recasens, Eduard Hovy, Vincent Ng and Michael Strube. *Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics*, Baltimore, MD, June 2014. ([pdf](http://aclweb.org/anthology/P/P14/P14-2006.pdf))
  - The version of the Kuhn-Munkres algorithm used for the CEAF scores uses [scipy.optimize.linear_sum_assignment](https://docs.scipy.org/doc/latest/reference/generated/scipy.optimize.linear_sum_assignment.html), with $-ϕ_n$ as cost function.


## License
This licence (the so-called “MIT License”) applies to all the files in this repository.
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
