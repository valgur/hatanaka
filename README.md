# Hatanaka [![Build](https://github.com/valgur/hatanaka/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/valgur/hatanaka/actions/workflows/build.yml) [![PyPI](https://img.shields.io/pypi/v/hatanaka)](https://pypi.org/project/hatanaka/)

Hatanaka compression / decompression of RINEX observation files within Python.

Wraps the original [RNXCMP tools](https://terras.gsi.go.jp/ja/crx2rnx.html) by Y. Hatanaka of the Geospatial
Information Authority of Japan (GSI).

## Usage

Usage is simple and straightforward.

```python
from hatanaka import rnx2crx, crx2rnx

with open('observations.crx') as f:
    rinex_data = crx2rnx(f)
    # or
    rinex_data = crx2rnx(f.read())
```

Alternatively, either function can also be applied directly to a file on disk.

```python
from hatanaka import rnx2crx_file, crx2rnx_file

rinex_path = crx2rnx_file('1lsu0010.21d')
assert rinex_path == '1lsu0010.21o'
```

Any errors during processing will be raised as a `HatanakaException` and any non-critical problems reported as warnings.

In addition to the above, the original `rnx2crx` and `crx2rnx` tools are made available from the command line as well.

## Installation

Binary wheels are available from PyPI for Linux, MacOS and Windows. Python versions 3.6+ are supported.

```bash
pip install hatanaka
```

To ensure that everything is working as expected, it is recommended to also run the included tests.

```bash
pip install pytest
pytest --pyargs hatanaka
```

### Building from source

Installing from git source code repo is also an option, in which case the RNXCMP tools will be built in the process.
This assumes a C compiler is available and is usually picked up automatically by Python's `setuptools`.
If that is not the case, you can instead provide a path to one by setting the `CC` environment variable.

```bash
pip install git+https://github.com/valgur/hatanaka
```

## Changes

See [CHANGES.md](rnxcmp/docs/CHANGES.md) of the original RNXCMP software package.

## Attribution

Martin Valgur – this Python library.

RNXCMP software:<br>
Hatanaka, Y. (2008), A Compression Format and Tools for GNSS Observation Data, Bulletin of the Geospatioal Information
Authority of Japan, 55, 21-30.
(available at https://www.gsi.go.jp/ENGLISH/Bulletin55.html)

## License
This library is provided under the MIT license.
Additional license terms apply from the included RNXCMP software – see [LICENSE](LICENSE).
