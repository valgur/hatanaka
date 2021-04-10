# Hatanaka [![Build](https://github.com/valgur/hatanaka/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/valgur/hatanaka/actions/workflows/build.yml) ![PyPI](https://img.shields.io/pypi/v/hatanaka)

Hatanaka compression / decompression of RINEX observation files within Python.

Wraps the [RNX2CRX and CRX2RNX tools](https://terras.gsi.go.jp/ja/crx2rnx.html) by Y. Hatanaka of the Geospatial
Information Authority of Japan (GSI).

## Installation

Python 3.6+ is required. Binary wheels are available from PyPI for Linux, MacOS and Windows.

```bash
pip install hatanaka
```

To ensure that everything is working as expected, it is recommended to run the included tests with

```bash
pip install pytest
pytest --pyargs hatanaka
```

### Building from source

Another option is to install from the git source code repo, in which case the RNXCMP tools will be built in the process. This assumes a C compiler is available and is usually picked up automatically by Python's `setuptools`. If that is not the case, you can instead provide a path to one by setting the `CC` environment variable.

```bash
pip install git+https://github.com/valgur/hatanaka
```

## Usage

Usage is simple and straightforward.

```python
from hatanaka import rnx2crx, crx2rnx

with open('observations.crx') as f:
    rinex_data = crx2rnx(f)
    # or
    rinex_data = crx2rnx(f.read())
```

Any errors during processing will be raised as a `HatanakaException` and any non-critical problems raised as warnings.

Additionally, the original `rnx2crx` and `crx2rnx` tools are also made available from
the command line and from within Python as `hatanaka.cli.rnx2crx` and `hatanaka.cli.crx2rnx`.
The latter can be convenient for working directly with files on disk:

```python
from hatanaka.cli import crx2rnx

# creates a decompressed 1lsu0010.21o file
crx2rnx(['1lsu0010.21d'])
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
