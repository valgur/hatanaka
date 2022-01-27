# Changelog

See also [CHANGES.md](rnxcmp/docs/CHANGES.md) of the original RNXCMP software package.

## [2.8.0] - 2022-01-27

- `rnx2crx` and `crx2rnx` executables are now added to the PATH.

## [2.7.0] - 2022-01-27

- Updated RNXCMP to version 4.1.0:
   - RINEX 4.xx files are now accepted as inputs.
   - Fixed bugs:
       + Error in case the number of special records exceeds 99 
         in RINEX ver. 2 files.
       + Error in case the clock offset is padded with spaces in RINEX ver. 3 or 4 files. 
       + Error in case a bad GNSS type is detected even if option -s 
         is specified with RNX2CRX.

## [2.6.0] - 2022-01-21

- Added `strict` parameter to decompression methods, which defaults to False.
  `ValueError` for non-RINEX files is only raised when `strict=True`. 

## [2.5.0] - 2022-01-10

- Decompression now raises a `ValueError` if the decompressed file lacks a valid RINEX header record.

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

[2.8.0]: https://github.com/valgur/hatanaka/compare/v2.7.0...v2.8.0
[2.7.0]: https://github.com/valgur/hatanaka/compare/v2.6.0...v2.7.0
[2.6.0]: https://github.com/valgur/hatanaka/compare/v2.5.0...v2.6.0
[2.5.0]: https://github.com/valgur/hatanaka/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.com/valgur/hatanaka/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/valgur/hatanaka/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/valgur/hatanaka/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/valgur/hatanaka/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/valgur/hatanaka/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/valgur/hatanaka/releases/tag/v1.0.0
