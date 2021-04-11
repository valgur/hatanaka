import shutil

from hatanaka.cli import crx2rnx as crx2rnx_cli, rnx2crx as rnx2crx_cli
from .conftest import clean


def test_rnx2crx_cli(tmp_path, rnx_sample, crx_str):
    sample_path = tmp_path / rnx_sample.name
    shutil.copy(rnx_sample, sample_path)
    rnx2crx_cli([str(sample_path)])
    expected_path = tmp_path / (rnx_sample.stem + '.crx')
    assert expected_path.exists()
    result = expected_path.read_text()
    assert clean(result) == clean(crx_str)
    shutil.rmtree(tmp_path)


def test_crx2rnx_cli(tmp_path, crx_sample, rnx_str):
    sample_path = tmp_path / crx_sample.name
    shutil.copy(crx_sample, sample_path)
    crx2rnx_cli([str(sample_path)])
    expected_path = tmp_path / (crx_sample.stem + '.rnx')
    assert expected_path.exists()
    result = expected_path.read_text()
    assert clean(result) == clean(rnx_str)
    shutil.rmtree(tmp_path)
