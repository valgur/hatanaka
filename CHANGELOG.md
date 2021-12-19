# Changelog

See also [CHANGES.md](rnxcmp/docs/CHANGES.md) of the original RNXCMP software package.

## [2.4.0] - 2021-12-19

- Added support for LZW (.Z) compression output. This is provided by the
  new [`ncompress`](https://github.com/valgur/ncompress) library.

  As a result, LZW decompression is now also 40x faster than with `unlzw3` and as fast as with the optional `unlzw`
  dependency
  (which currently has a [memory leak issue](https://github.com/ionelmc/python-unlzw/pull/3)).

- Fixed a deprecation warning from `importlib_resources`.

## [2.3.0] - 2021-04-13

- Add the `--delete` option of the CLI apps also as an option in the library.

## [2.2.0] - 2021-04-13

- During decompression, allow filenames to end with only .zip, .gz, etc. suffixes. .rnx will be used as the new suffix
  after decompression.

## [2.1.0] - 2021-04-12

- Relax file name requirements.
    - Anything is allowed as long as it is converted without errors and can be renamed unambiguously.

## [2.0.0] - 2021-04-12

- Extend decompression / compression support to all compression formats allowed by the RINEX standard:
    - Add `decompress` and `compress` functions in Python.
    - Replace the `crx2rnx` and `rnx2crx` executables with more general `rinex-decompress` and `rinex-compress` on the
      command line.

## [1.0.0] - 2021-04-10

First release.

- Package and wrap [RNXCMP](https://terras.gsi.go.jp/ja/crx2rnx.html) 4.0.8 as PyPI wheels for all major operating
  systems.
- Provide Hatanaka decompression / compression support via `crx2rnx` and `rnx2crx` functions.
- Install `crx2rnx` and `rnx2crx` as command line executables.

[2.4.0]: https://github.com/valgur/hatanaka/compare/v2.3.0...v2.4.0

[2.3.0]: https://github.com/valgur/hatanaka/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/valgur/hatanaka/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/valgur/hatanaka/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/valgur/hatanaka/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/valgur/hatanaka/releases/tag/v1.0.0
