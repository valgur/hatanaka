import pytest

from hatanaka import HatanakaException, crx2rnx, rnx2crx
from .conftest import clean


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
    converted = rnx2crx(rnx_str, reinit_every_nth=1, skip_strange_epochs=True)
    assert clean(converted) == clean(crx_str)


def test_rnx2crx_extra_args_warning(rnx_str, crx_str):
    rnx_str = rnx_str.replace('R19 129262004.57708', 'G13 130321269.80108')
    with pytest.warns(UserWarning) as record:
        converted = rnx2crx(rnx_str, reinit_every_nth=1, skip_strange_epochs=True)
    assert len(record) == 1
    assert (record[0].message.args[0] ==
            'rnx2crx: Duplicated satellite in one epoch at line 15. ... skip')
    # Only the header remains
    assert clean(crx_str).startswith(clean(converted))


def test_crx2rnx_extra_args_good(rnx_str, crx_str):
    converted = crx2rnx(crx_str, skip_strange_epochs=True)
    assert clean(converted) == clean(rnx_str)


def test_non_ascii_is_tolerated(rnx_bytes, crx_bytes):
    def add_non_ascii(txt):
        return txt.replace(
            b'VERSION / TYPE',
            b'VERSION / TYPE' + 'õäü'.encode().ljust(60) + b'COMMENT\n')

    converted = crx2rnx(add_non_ascii(crx_bytes))
    assert clean(converted) == clean(add_non_ascii(rnx_bytes))
    converted = rnx2crx(add_non_ascii(rnx_bytes))
    assert clean(converted) == clean(add_non_ascii(crx_bytes))


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
