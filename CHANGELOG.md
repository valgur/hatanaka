# Changelog

See also [CHANGES.md](rnxcmp/docs/CHANGES.md) of the original RNXCMP software package.

## [2.0.0] - 2021-04-12

- Extend decompression / compression support to all compression formats allowed by the RINEX standard:
    - Add `decompress` and `compress` functions in Python.
    - Replace the `crx2rnx` and `rnx2crx` executables with more general `rinex-decompress` and `rinex-compress` on the command line.

## [1.0.0] - 2021-04-10

First release.
- Package and wrap [RNXCMP](https://terras.gsi.go.jp/ja/crx2rnx.html) 4.0.8 as PyPI wheels for all major operating systems.
- Provide Hatanaka decompression / compression support via `crx2rnx` and `rnx2crx` functions.
- Install `crx2rnx` and `rnx2crx` as command line executables.

[2.0.0]: https://github.com/valgur/hatanaka/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/valgur/hatanaka/releases/tag/v1.0.0
