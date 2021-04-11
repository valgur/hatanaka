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
]


@pytest.mark.parametrize(
    'input_suffix, expected_suffix',
    decompress_pairs
)
def test_decompress(tmp_path, crx_sample, rnx_str, input_suffix, expected_suffix):
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    for x in ['.21d', '.21D', '.CRX']:
        in_file = in_file.replace(x, '.crx')
    shutil.copy(get_data_path(in_file), sample_path)
    converted = decompress(sample_path)
    assert clean(converted) == clean(rnx_str)
    converted = decompress(io.BytesIO(sample_path.read_bytes()))
    assert clean(converted) == clean(rnx_str)
    shutil.rmtree(tmp_path)


@pytest.mark.parametrize(
    'input_suffix, expected_suffix',
    decompress_pairs
)
def test_decompress_on_disk(tmp_path, crx_sample, rnx_str, input_suffix, expected_suffix):
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    for x in ['.21d', '.21D', '.CRX']:
        in_file = in_file.replace(x, '.crx')
    shutil.copy(get_data_path(in_file), sample_path)
    out_path = decompress_on_disk(sample_path)
    assert out_path.exists()
    assert out_path == tmp_path / ('sample' + expected_suffix)
    assert clean(out_path.read_text()) == clean(rnx_str)
    shutil.rmtree(tmp_path)


compress_pairs = [
    ('.rnx', 'none', '.crx'),
    ('.rnx', 'gz', '.crx.gz'),
    ('.rnx', 'bz2', '.crx.bz2'),
    ('.RNX', 'gz', '.CRX.gz'),
    ('.21o', 'bz2', '.21d.bz2'),
    ('.21O', 'gz', '.21D.gz'),
]


@pytest.mark.parametrize(
    'input_suffix, compression, expected_suffix',
    compress_pairs
)
def test_compress(tmp_path, crx_sample, rnx_str, input_suffix, compression, expected_suffix):
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    for x in ['.21o', '.21O', '.RNX']:
        in_file = in_file.replace(x, '.rnx')
    shutil.copy(get_data_path(in_file), sample_path)
    converted = compress(sample_path, compression=compression)
    assert clean(decompress(io.BytesIO(converted))) == clean(rnx_str)
    converted = compress(io.BytesIO(sample_path.read_bytes()), compression=compression)
    assert clean(decompress(io.BytesIO(converted))) == clean(rnx_str)
    shutil.rmtree(tmp_path)


@pytest.mark.parametrize(
    'input_suffix, compression, expected_suffix',
    compress_pairs
)
def test_compress_on_disk(tmp_path, crx_sample, rnx_str, input_suffix, compression,
                          expected_suffix):
    sample_path = tmp_path / ('sample' + input_suffix)
    in_file = 'sample' + input_suffix
    for x in ['.21o', '.21O', '.RNX']:
        in_file = in_file.replace(x, '.rnx')
    shutil.copy(get_data_path(in_file), sample_path)
    out_path = compress_on_disk(sample_path, compression=compression)
    assert out_path.exists()
    assert out_path == tmp_path / ('sample' + expected_suffix)
    assert clean(decompress(out_path)) == clean(rnx_str)
    shutil.rmtree(tmp_path)
