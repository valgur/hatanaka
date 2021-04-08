# Hatanaka

Hatanaka compression / decompression of RINEX observation files within Python.

Wraps the [RNX2CRX and CRX2RNX tools](https://terras.gsi.go.jp/ja/crx2rnx.html) by Y. Hatanaka of the Geospatial
Information Authority of Japan (GSI).

## Installation

Requires Python 3.6+ and a C compiler when installing from source.

```bash
pip install git+https://github.com/valgur/hatanaka
```

If a C compiler is not available on `PATH`, you can instead provide a path to one with the `CC` environment variable.

To ensure that everything is working as expected run the included tests with

```bash
pip install pytest
pytest --pyargs hatanaka
```

## Usage

```python
from hatanaka import rnx2crx, crx2rnx

with open('observations.crx') as f:
    rnx_data = crx2rnx(f)
```

Any errors during processing will be raised as a `HatanakaException` and any non-critical problems raised as warnings.

## Changes

See [CHANGES.md](rnxcmp/docs/CHANGES.md) of the original source code package.

## Attribution

Martin Valgur – this Python library.

RNXCMP software:<br>
Hatanaka, Y. (2008), A Compression Format and Tools for GNSS Observation Data, Bulletin of the Geospatioal Information
Authority of Japan, 55, 21-30.
(available at https://www.gsi.go.jp/ENGLISH/Bulletin55.html)

## License

MIT – this Python library.

RNXCMP software – see [LICENSE](LICENSE).
