import io
import shutil
import sys
from contextlib import contextmanager

import pytest

from hatanaka.cli import compress_cli, decompress, decompress_cli
from .conftest import clean, get_data_path
from .test_general_compression import compress_pairs, decompress_pairs


@contextmanager
def replace_stdin(content):
    orig = sys.stdin
    target = io.BytesIO()
    target.write(content)
    target.seek(0)
    target.buffer = target
    sys.stdin = target
    yield
    sys.stdin = orig


@contextmanager
def replace_stdout():
    orig = sys.stdout
    target = io.BytesIO()
    sys.stdout = target
    target.buffer = target
    yield target
    target.seek(0)
    sys.stdout = orig


@pytest.mark.parametrize(
    'input_suffix, expected_suffix',
    decompress_pairs
)
def test_decompress_cli(tmp_path, crx_sample, rnx_str, input_suffix, expected_suffix):
    # prepare
    in_file = 'sample' + input_suffix
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # decompress
    retcode = decompress_cli([str(sample_path)])
    # check
    assert retcode == 0
    expected_path = tmp_path / ('sample' + expected_suffix)
    assert sample_path.exists()
    assert expected_path.exists()
    assert clean(expected_path.read_text()) == clean(rnx_str)


@pytest.mark.parametrize(
    'input_suffix, compression, expected_suffix',
    compress_pairs
)
def test_compress_cli(tmp_path, crx_sample, rnx_bytes, input_suffix, compression,
                      expected_suffix):
    # prepare
    in_file = 'sample' + input_suffix
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # compress
    retcode = compress_cli([
        str(sample_path),
        '--compression', compression
    ])
    # check
    assert retcode == 0
    expected_path = tmp_path / ('sample' + expected_suffix)
    assert sample_path.exists()
    assert expected_path.exists()
    assert clean(decompress(expected_path)) == clean(rnx_bytes)


def test_decompress_cli_stdin(rnx_bytes):
    in_data = get_data_path('sample.crx.gz').read_bytes()
    with replace_stdin(in_data), replace_stdout() as stdout:
        decompress_cli([])
    assert clean(stdout.getvalue()) == clean(rnx_bytes)


def test_compress_cli_stdin(rnx_bytes):
    in_data = get_data_path('sample.rnx').read_bytes()
    with replace_stdin(in_data), replace_stdout() as stdout:
        compress_cli([])
    result = stdout.getvalue()
    assert clean(result) != clean(rnx_bytes)
    assert clean(decompress(result)) == clean(rnx_bytes)


def test_cli_delete(tmp_path, rnx_bytes):
    # prepare
    in_file = 'sample.rnx'
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # compress
    retcode = compress_cli([str(sample_path), '--delete'])
    # check
    assert retcode == 0
    expected_path = tmp_path / 'sample.crx.gz'
    assert not sample_path.exists()
    assert expected_path.exists()
    assert clean(decompress(expected_path)) == clean(rnx_bytes)


def test_cli_no_delete_on_warnings(tmp_path, rnx_bytes):
    # prepare
    in_file = 'sample.rnx'
    sample_path = tmp_path / in_file
    txt = get_data_path(in_file).read_bytes()
    sample_path.write_bytes(txt + b'\0\0\0')
    # compress
    with pytest.warns(UserWarning) as record:
        retcode = compress_cli([str(sample_path), '--delete'])
    # check
    assert len(record) == 1
    assert record[0].message.args[0].startswith('rnx2crx: null characters')
    assert retcode == 2
    expected_path = tmp_path / 'sample.crx.gz'
    assert sample_path.exists()
    assert expected_path.exists()
    assert clean(decompress(expected_path)) == clean(rnx_bytes)


def test_cli_no_delete_unchanged(tmp_path, rnx_str):
    # prepare
    in_file = 'sample.crx.gz'
    sample_path = tmp_path / in_file
    shutil.copy(get_data_path(in_file), sample_path)
    # compress
    retcode = compress_cli([str(sample_path), '--delete'])
    # check
    assert retcode == 0
    expected_path = tmp_path / 'sample.crx.gz'
    assert sample_path.exists()
    assert expected_path == sample_path
