import re
from pathlib import Path

import pytest
from importlib_resources import files

import hatanaka.test.data


def get_data_path(fname) -> Path:
    for x in ['.21o', '.rnx']:
        fname = fname.replace(x.lower(), '.rnx')
        fname = fname.replace(x.upper(), '.rnx')
    for x in ['.21d', '.crx']:
        fname = fname.replace(x.lower(), '.crx')
        fname = fname.replace(x.upper(), '.crx')
    m = re.fullmatch(r'sample\.(zip|gz|bz2|Z)', fname)
    if m:
        fname = 'sample.crx.' + m.group(1)
    return files(hatanaka.test.data) / fname


def clean(txt):
    # Remove rnx2crx version number and timestamp for testing
    pattern = '^RNX2CRX.+CRINEX PROG / DATE$'
    if isinstance(txt, bytes):
        return re.sub(pattern.encode(), b'', txt.replace(b'\r', b''), flags=re.M)
    return re.sub(pattern, '', txt.replace('\r', ''), flags=re.M)


@pytest.fixture
def crx_sample():
    return get_data_path('sample.crx')


@pytest.fixture
def rnx_sample():
    return get_data_path('sample.rnx')


@pytest.fixture
def crx_str(crx_sample):
    return crx_sample.read_text()


@pytest.fixture
def rnx_str(rnx_sample):
    return rnx_sample.read_text()


@pytest.fixture
def crx_str_stream(crx_sample):
    with crx_sample.open('r', encoding='ascii') as f:
        yield f


@pytest.fixture
def rnx_str_stream(rnx_sample):
    with rnx_sample.open('r', encoding='ascii') as f:
        yield f


@pytest.fixture
def crx_bytes(crx_sample):
    return crx_sample.read_bytes()


@pytest.fixture
def rnx_bytes(rnx_sample):
    return rnx_sample.read_bytes()


@pytest.fixture
def crx_bytes_stream(crx_sample):
    with crx_sample.open('rb') as f:
        yield f


@pytest.fixture
def rnx_bytes_stream(rnx_sample):
    with rnx_sample.open('rb') as f:
        yield f


decompress_pairs = [
    ('.crx', '.rnx'),
    ('.CRX', '.RNX'),
    ('.21d', '.21o'),
    ('.21D', '.21O'),
    ('.21d.gz', '.21o'),
    ('.21d.Z', '.21o'),
    ('.21d.bz2', '.21o'),
    ('.21d.zip', '.21o'),
    ('.crx.gz', '.rnx'),
    ('.crx.Z', '.rnx'),
    ('.crx.bz2', '.rnx'),
    ('.crx.zip', '.rnx'),
    ('.rnx', '.rnx'),
    ('.rnx.gz', '.rnx'),
    ('.rnx.Z', '.rnx'),
    ('.rnx.zip', '.rnx'),
    ('.rnx.bz2', '.rnx'),
    ('.21o', '.21o'),
    ('.21o.gz', '.21o'),
    ('.zip', '.rnx'),
    ('.gz', '.rnx'),
    ('.bz2', '.rnx'),
]

compress_pairs = [
    ('.rnx', 'none', '.crx'),
    ('.rnx', 'gz', '.crx.gz'),
    ('.rnx', 'bz2', '.crx.bz2'),
    ('.rnx', 'Z', '.crx.Z'),
    ('.RNX', 'gz', '.CRX.gz'),
    ('.21o', 'bz2', '.21d.bz2'),
    ('.21o', 'Z', '.21d.Z'),
    ('.21O', 'gz', '.21D.gz'),
    ('.crx', 'gz', '.crx.gz'),
    ('.21d', 'gz', '.21d.gz'),
    ('.crx', 'none', '.crx'),
    ('.21d', 'none', '.21d'),
]
