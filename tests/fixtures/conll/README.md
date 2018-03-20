Official CoNLL testcases
========================

This directory contain the [reference scorer](https://github.com/conll/reference-coreference-scorers) testcases, to ensure compatibility with it.

The test results included in <conll.json> are adapted from [the reference test configuration](https://github.com/conll/reference-coreference-scorers/blob/master/test/CorefMetricTestConfig.pm) using its [README](https://github.com/conll/reference-coreference-scorers/blob/master/test/TestCases.README)  as a reference for the exact values of the metrics (as opposed with the truncated values).

The only exception to the above isf the CEAF_m F₁ value for testcase A9, which is erroneously given as `8/14` instead of `8/13` (which is consistent with the given truncated value in the test config).
