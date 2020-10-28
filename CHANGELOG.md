Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (0.1.0)

[Unreleased]: https://github.com/loicgrobol/scorch/compare/v0.2.0...HEAD

## [0.2.0] — 2020-10-28

[0.2.0]: https://github.com/loicgrobol/scorch/compare/v0.1.0...v0.2.0

### Changed

- Slightly faster BLANC ([#13](https://github.com/LoicGrobol/scorch/pull/13))

## [0.1.0] — 2020-10-12

[0.1.0]: https://github.com/loicgrobol/scorch/compare/v0.0.26...v0.1.0

### Fixed

- Stop redirecting SIGPIPE
  [incorrectly](https://docs.python.org/3/library/signal.html#note-on-sigpipe)
- B³ and CEAF P and R are now set to 0 if their denominator is 0, following the reference implementation ([@Rexhaif](https://github.com/Rexhaif) in [#10](https://github.com/LoicGrobol/scorch/pull/10))

## [0.0.26] - 2019-12-16

[0.0.26]: https://github.com/loicgrobol/scorch/compare/v0.0.25...v0.0.26

### Added

- [`speedtest.py`](/tests/speedtest.py), a benchmark tool for the speed of our implementations

### Changed

- Speed up of BLANC computation by a factor of 75 at the price of straightforwardness of
  implementation. The slow and straightforward implementation is still available behind a parameter
  and is used to test the consistency of the fast one.
  ([#5](https://github.com/LoicGrobol/scorch/pull/5))

## Previous versions

No real changelog was kept for the previous versions, you can have a look at the history but it is
not for the faint of heart
