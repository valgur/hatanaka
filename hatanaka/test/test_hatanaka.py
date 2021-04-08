import re

import hatanaka.test
import pytest
from hatanaka import crx2rnx, rnx2crx
from importlib_resources import files

crx_sample = files(hatanaka.test) / 'sample.crx'
rnx_sample = files(hatanaka.test) / 'sample.rnx'


@pytest.fixture
def crx_str():
    with crx_sample.open('r', encoding='ascii') as f:
        return f.read()


@pytest.fixture
def rnx_str():
    with rnx_sample.open('r', encoding='ascii') as f:
        return f.read()


@pytest.fixture
def crx_str_stream():
    with crx_sample.open('r', encoding='ascii') as f:
        yield f


@pytest.fixture
def rnx_str_stream():
    with rnx_sample.open('r', encoding='ascii') as f:
        yield f


@pytest.fixture
def crx_bytes():
    with crx_sample.open('rb') as f:
        return f.read()


@pytest.fixture
def rnx_bytes():
    with rnx_sample.open('rb') as f:
        return f.read()


@pytest.fixture
def crx_bytes_stream():
    with crx_sample.open('rb') as f:
        yield f


@pytest.fixture
def rnx_bytes_stream():
    with rnx_sample.open('rb') as f:
        yield f


def clean(txt):
    # Remove rnx2crx version number and timestamp for testing
    pattern = '^RNX2CRX.+CRINEX PROG / DATE$'
    if isinstance(txt, bytes):
        return re.sub(pattern.encode(), b'', txt, flags=re.M).replace(b'\r', b'')
    return re.sub(pattern, '', txt, flags=re.M)


def test_rnx2crx_str(rnx_str, crx_str):
    assert clean(rnx2crx(rnx_str)) == clean(crx_str)


def test_rnx2crx_bytes(rnx_bytes, crx_bytes):
    assert clean(rnx2crx(rnx_bytes)) == clean(crx_bytes)


def test_crx2rnx_str(crx_str, rnx_str):
    assert crx2rnx(crx_str) == rnx_str


def test_crx2rnx_bytes(crx_bytes, rnx_bytes):
    assert clean(crx2rnx(crx_bytes)) == clean(rnx_bytes)


def test_rnx2crx_str_stream(rnx_str_stream, crx_str):
    assert clean(rnx2crx(rnx_str_stream)) == clean(crx_str)


def test_rnx2crx_bytes_stream(rnx_bytes_stream, crx_bytes):
    assert clean(rnx2crx(rnx_bytes_stream)) == clean(crx_bytes)


def test_crx2rnx_str_stream(crx_str_stream, rnx_str):
    assert crx2rnx(crx_str_stream) == rnx_str


def test_crx2rnx_bytes_stream(crx_bytes_stream, rnx_bytes):
    assert clean(crx2rnx(crx_bytes_stream)) == clean(rnx_bytes)


if __name__ == '__main__':
    pytest.main()
