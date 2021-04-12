# Hatanaka [![Build](https://github.com/valgur/hatanaka/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/valgur/hatanaka/actions/workflows/build.yml) [![codecov](https://codecov.io/gh/valgur/hatanaka/branch/master/graph/badge.svg?token=7TBLMZ8Wi9)](https://codecov.io/gh/valgur/hatanaka) [![PyPI](https://img.shields.io/pypi/v/hatanaka)](https://pypi.org/project/hatanaka/)

Effortless compression / decompression of RINEX files in Python and on the command line.

Supports all compression formats allowed by the RINEX 2 and 3 standards:

* Hatanaka compression for Observation Data Files,
* LZW (.Z), gzip (.gz), bzip2 (.bz2) and .zip.

## Quick Start

### Installation

Wheels are available from PyPI for Linux, MacOS and Windows. Python versions 3.6 and up are supported.

```bash
pip install hatanaka
```

To ensure that everything is working as expected, it is recommended to also run the included tests.

```bash
pip install pytest
pytest --pyargs hatanaka
```

### Python

```python
import hatanaka
from pathlib import Path

# decompression
rinex_data = hatanaka.decompress('1lsu0010.21d.Z')
# or
rinex_data = hatanaka.decompress(Path('1lsu0010.21d.Z').read_bytes())
# or, creates '1lsu0010.21o' directly on disk
hatanaka.decompress_on_disk('1lsu0010.21d.Z')

# compression
Path('1lsu0010.21d.gz').write_bytes(hatanaka.compress(rinex_data))
# or
Path('1lsu0010.21d.gz').write_bytes(hatanaka.compress('1lsu0010.21o'))
# or, creates '1lsu0010.21d.gz' directly on disk
hatanaka.compress_on_disk('1lsu0010.21o')
```

Any errors during Hatanaka compression/decompression will be raised as a `HatanakaException` and any non-critical
problems reported as warnings.

These functions are idempotent – already decompressed / compressed data is returned as is.

### CLI

The same functionality is also made available from the command line via `rinex-decompress` and `rinex-compress`.

Simply provide a list of RINEX files to compress or decompress. stdin-stdout is used if no files are specified.

To remove the original files after conversion, add `-d`/`--delete`. The input file is removed only if conversion
succeeds without any errors or warnings.

```bash
# creates 1lsu0010.21o
rinex-decompress 1lsu0010.21d.Z

# creates 1lsu0010.21d.gz
rinex-compress 1lsu0010.21o

# stdin-stdout example
rinex-decompress < 1lsu0010.21d.Z | grep 'SYS / # / OBS TYPES'
```

## Development

### Building from source

Installing from source code is also an option, in which case the RNXCMP tools will be built in the process. This assumes
a C compiler is available and is usually picked up automatically by Python's `setuptools`. If that is not the case, you
can instead provide a path to one by setting the `CC` environment variable.

```bash
pip install git+https://github.com/valgur/hatanaka
```

## Changes

See [CHANGELOG.md](CHANGELOG.md).

## Attribution

Martin Valgur – this Python library.

[RNXCMP software](https://terras.gsi.go.jp/ja/crx2rnx.html) for Hatanaka compression support:<br>
Hatanaka, Y. (2008), A Compression Format and Tools for GNSS Observation Data, Bulletin of the Geospatioal Information
Authority of Japan, 55, 21-30.
(available at https://www.gsi.go.jp/ENGLISH/Bulletin55.html)

## License

This library is provided under the MIT license. Additional license terms apply for the included RNXCMP software –
see [LICENSE](LICENSE).
