import gzip
import io
import shutil

import pytest

from hatanaka import compress, compress_on_disk, decompress, decompress_on_disk
from .conftest import clean, get_data_path

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


@pytest.mark.parametrize(
    'input_suffix, expected_suffix',
    decompress_pairs
)
def test_decompress(tmp_path, crx_sample, rnx_bytes, input_suffix, expected_suffix):
    # prepare
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    shutil.copy(get_data_path(in_file), sample_path)
    # decompress
    converted = decompress(sample_path)
    # check
    assert clean(converted) == clean(rnx_bytes)
    converted = decompress(sample_path.read_bytes())
    assert clean(converted) == clean(rnx_bytes)


@pytest.mark.parametrize(
    'input_suffix, expected_suffix',
    decompress_pairs
)
def test_decompress_on_disk(tmp_path, crx_sample, rnx_bytes, input_suffix, expected_suffix):
    # prepare
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    shutil.copy(get_data_path(in_file), sample_path)
    # decompress
    out_path = decompress_on_disk(sample_path)
    # check
    assert out_path.exists()
    print(list(tmp_path.glob('*')))
    assert out_path == tmp_path / ('sample' + expected_suffix)
    assert clean(out_path.read_bytes()) == clean(rnx_bytes)


def make_nav(txt):
    return txt.replace(b'OBSERVATION', b'NAVIGATION ')


@pytest.mark.parametrize(
    'input_suffix',
    ['.rnx', '.RNX', '.21n']
)
def test_decompress_non_obs(tmp_path, rnx_bytes, input_suffix):
    # prepare
    txt = make_nav(rnx_bytes)
    sample_path = tmp_path / ('sample' + input_suffix + '.gz')
    sample_path.write_bytes(gzip.compress(txt))
    # decompress
    out_path = decompress_on_disk(sample_path)
    # check
    assert out_path.exists()
    assert out_path == tmp_path / ('sample' + input_suffix)
    assert clean(out_path.read_bytes()) == clean(txt)


compress_pairs = [
    ('.rnx', 'none', '.crx'),
    ('.rnx', 'gz', '.crx.gz'),
    ('.rnx', 'bz2', '.crx.bz2'),
    ('.RNX', 'gz', '.CRX.gz'),
    ('.21o', 'bz2', '.21d.bz2'),
    ('.21O', 'gz', '.21D.gz'),
    ('.crx', 'gz', '.crx.gz'),
    ('.21d', 'gz', '.21d.gz'),
    ('.crx', 'none', '.crx'),
    ('.21d', 'none', '.21d'),
]


@pytest.mark.parametrize(
    'input_suffix, compression, expected_suffix',
    compress_pairs
)
def test_compress(tmp_path, crx_sample, rnx_bytes, input_suffix, compression, expected_suffix):
    # prepare
    in_file = 'sample' + input_suffix
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # compress
    converted = compress(sample_path, compression=compression)
    # check
    assert clean(decompress(converted)) == clean(rnx_bytes)
    converted = compress(sample_path.read_bytes(), compression=compression)
    assert clean(decompress(converted)) == clean(rnx_bytes)


@pytest.mark.parametrize(
    'input_suffix, compression, expected_suffix',
    compress_pairs
)
def test_compress_on_disk(tmp_path, crx_sample, rnx_bytes, input_suffix, compression,
                          expected_suffix):
    # prepare
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    shutil.copy(get_data_path(in_file), sample_path)
    # compress
    out_path = compress_on_disk(sample_path, compression=compression)
    # check
    assert out_path.exists()
    assert out_path == tmp_path / ('sample' + expected_suffix)
    assert clean(decompress(out_path)) == clean(rnx_bytes)


@pytest.mark.parametrize(
    'input_suffix',
    ['.rnx', '.RNX', '.21n']
)
def test_compress_non_obs(tmp_path, rnx_bytes, input_suffix):
    # prepare
    txt = make_nav(rnx_bytes)
    sample_path = tmp_path / ('sample' + input_suffix)
    sample_path.write_bytes(txt)
    # compress
    out_path = compress_on_disk(sample_path)
    # check
    assert out_path.exists()
    assert out_path == tmp_path / ('sample' + input_suffix + '.gz')
    assert clean(decompress(out_path)) == clean(txt)


def test_invalid_input(crx_str, rnx_bytes):
    with pytest.raises(ValueError):
        decompress(io.BytesIO(rnx_bytes))
    with pytest.raises(ValueError):
        compress(io.BytesIO(rnx_bytes))


def test_invalid_name(tmp_path, rnx_sample):
    sample_path = tmp_path / 'sample'
    shutil.copy(rnx_sample, sample_path)
    with pytest.raises(ValueError) as excinfo:
        decompress_on_disk(sample_path)
    msg = excinfo.value.args[0]
    assert msg.endswith('is not a valid RINEX file name')
    with pytest.raises(ValueError) as excinfo:
        compress_on_disk(sample_path)
    msg = excinfo.value.args[0]
    assert msg.endswith('is not a valid RINEX file name')


def test_decompress_on_disk_delete(tmp_path, rnx_bytes):
    # prepare
    in_file = 'sample.crx.gz'
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # decompress and delete
    out_path = decompress_on_disk(sample_path, delete=True)
    # check
    expected_path = tmp_path / 'sample.rnx'
    assert not sample_path.exists()
    assert out_path == expected_path
    assert expected_path.exists()
    assert clean(decompress(expected_path)) == clean(rnx_bytes)
    # check that already decompressed is not deleted
    out_path = decompress_on_disk(expected_path, delete=True)
    assert out_path == expected_path
    assert out_path.exists()


def test_compress_on_disk_delete(tmp_path, rnx_bytes):
    # prepare
    in_file = 'sample.rnx'
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # decompress and delete
    out_path = compress_on_disk(sample_path, delete=True)
    # check
    expected_path = tmp_path / 'sample.crx.gz'
    assert not sample_path.exists()
    assert out_path == expected_path
    assert expected_path.exists()
    assert clean(decompress(expected_path)) == clean(rnx_bytes)
    # check that already decompressed is not deleted
    out_path = compress_on_disk(expected_path, delete=True)
    assert out_path == expected_path
    assert out_path.exists()
