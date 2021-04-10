import re
import shutil

import pytest
from importlib_resources import files

import hatanaka.test
from hatanaka import HatanakaException, crx2rnx, rnx2crx
from hatanaka.cli import crx2rnx as crx2rnx_cli, rnx2crx as rnx2crx_cli

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
        return re.sub(pattern.encode(), b'', txt.replace(b'\r', b''), flags=re.M)
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


def test_invalid():
    with pytest.raises(HatanakaException) as excinfo:
        crx2rnx('blah')
    msg = excinfo.value.args[0]
    assert msg.startswith('The file seems to be truncated in the middle.')


def test_warning(rnx_bytes, crx_bytes):
    rnx_bytes += b'\0\0\0'
    with pytest.warns(UserWarning) as record:
        converted = rnx2crx(rnx_bytes)
    assert clean(converted) == clean(crx_bytes)
    assert len(record) == 1
    assert record[0].message.args[0].startswith('rnx2crx: null characters')


def test_rnx2crx_extra_args_good(rnx_str, crx_str):
    converted = rnx2crx(rnx_str, reinit_every_nth=1, skip_strange=True)
    assert clean(converted) == clean(crx_str)


def test_rnx2crx_extra_args_warning(rnx_str, crx_str):
    rnx_str = rnx_str.replace('R19 129262004.57708', 'G13 130321269.80108')
    with pytest.warns(UserWarning) as record:
        converted = rnx2crx(rnx_str, reinit_every_nth=1, skip_strange=True)
    assert len(record) == 1
    assert (record[0].message.args[0] ==
            'rnx2crx: Duplicated satellite in one epoch at line 15. ... skip')
    # Only the header remains
    assert clean(crx_str).startswith(clean(converted))


def test_crx2rnx_extra_args_good(rnx_str, crx_str):
    converted = crx2rnx(crx_str, skip_strange=True)
    assert clean(converted) == clean(rnx_str)


def test_rnx2crx_cli(tmp_path, crx_str):
    sample_path = tmp_path / rnx_sample.name
    shutil.copy(rnx_sample, sample_path)
    rnx2crx_cli([str(sample_path)])
    expected_path = tmp_path / (rnx_sample.stem + '.crx')
    assert expected_path.exists()
    with expected_path.open() as f:
        result = f.read()
    assert clean(result) == clean(crx_str)
    shutil.rmtree(tmp_path)


def test_crx2rnx_cli(tmp_path, rnx_str):
    sample_path = tmp_path / crx_sample.name
    shutil.copy(crx_sample, sample_path)
    crx2rnx_cli([str(sample_path)])
    expected_path = tmp_path / (crx_sample.stem + '.rnx')
    assert expected_path.exists()
    with expected_path.open() as f:
        result = f.read()
    assert clean(result) == clean(rnx_str)
    shutil.rmtree(tmp_path)


def test_stderr_bad_encoding(crx_bytes):
    """The errors and warnings can include cited garbage from invalid files
    and we should handle that gracefully."""
    with pytest.raises(HatanakaException) as excinfo:
        crx2rnx(crx_bytes[:-1] + b'\xFF\0')
    msg = excinfo.value.args[0]
    assert msg.startswith('The file seems to be truncated')
    assert msg.endswith('\\xff<end')


if __name__ == '__main__':
    pytest.main()
