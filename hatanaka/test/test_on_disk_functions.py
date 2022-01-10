import shutil

import pytest

from hatanaka import HatanakaException, compress_on_disk, decompress, decompress_on_disk, \
    get_compressed_path, get_decompressed_path
from hatanaka.test.conftest import clean, compress_pairs, decompress_pairs, get_data_path


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


def test_on_disk_empty_input(tmp_path, crx_str, rnx_bytes):
    path = tmp_path / 'sample.crx'
    path.write_bytes(b'')
    with pytest.raises(ValueError) as excinfo:
        decompress_on_disk(path)
    assert "empty file" in str(excinfo.value)
    assert not get_decompressed_path(path).exists()
    path.unlink()

    path = tmp_path / 'sample.rnx'
    path.write_bytes(b'')
    with pytest.raises(ValueError) as excinfo:
        compress_on_disk(path)
    assert "file is too short" in str(excinfo.value)
    assert not get_compressed_path(path, is_obs=True).exists()


def test_invalid_name_on_disk(tmp_path, rnx_sample):
    sample_path = tmp_path / 'sample'
    shutil.copy(rnx_sample, sample_path)
    with pytest.raises(ValueError) as excinfo:
        compress_on_disk(sample_path)
    msg = excinfo.value.args[0]
    assert msg.endswith('is not a valid RINEX file name')
    assert not get_compressed_path(tmp_path / 'sample.rnx', is_obs=True).exists()


def test_on_disk_invalid_input(tmp_path):
    path = tmp_path / 'sample.crx'
    path.write_bytes(b'blah' * 100)
    with pytest.raises(ValueError) as excinfo:
        decompress_on_disk(path)
    msg = excinfo.value.args[0]
    assert 'not a valid RINEX file' in msg
    assert not get_compressed_path(path).exists()


def test_on_disk_truncated_input(tmp_path):
    in_file = 'sample.crx'
    sample_path = tmp_path / in_file
    sample_path.write_bytes(get_data_path(in_file).read_bytes()[:200])
    with pytest.raises(HatanakaException) as excinfo:
        decompress_on_disk(sample_path)
    msg = excinfo.value.args[0]
    assert 'truncated in the middle' in msg
    assert not get_compressed_path(sample_path).exists()


def test_on_disk_hatanaka_warning(tmp_path, crx_bytes):
    in_file = 'sample.rnx'
    sample_path = tmp_path / in_file
    sample_path.write_bytes(get_data_path(in_file).read_bytes() + b'\0\0\0')
    with pytest.warns(UserWarning) as record:
        crx_path = compress_on_disk(sample_path, compression='none')
    assert crx_path.exists()
    assert clean(crx_path.read_bytes()) == clean(crx_bytes)
    assert len(record) == 1
    assert record[0].message.args[0].startswith('rnx2crx: null characters')
