import re

import pytest
from importlib_resources import files

import hatanaka.test.data


def get_data_path(fname):
    for x in ['.21o', '.rnx']:
        fname = fname.replace(x.lower(), '.rnx')
        fname = fname.replace(x.upper(), '.rnx')
    for x in ['.21d', '.crx']:
        fname = fname.replace(x.lower(), '.crx')
        fname = fname.replace(x.upper(), '.crx')
    m = re.fullmatch(r'sample\.(zip|gz|bz2)', fname)
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
