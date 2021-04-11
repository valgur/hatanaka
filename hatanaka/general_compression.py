import bz2
import gzip
import re
import zipfile
from io import BytesIO, IOBase
from pathlib import Path
from typing import BinaryIO, Union

from typing.io import IO

from .hatanaka import crx2rnx, rnx2crx

try:
    from unlzw import unlzw
except ImportError:
    from unlzw3 import unlzw

__all__ = [
    'decompress', 'decompress_on_disk', 'get_decompressed_path',
    'compress', 'compress_on_disk', 'get_compressed_path'
]


def decompress(f: Union[Path, str, BytesIO, BinaryIO], *,
               skip_strange_epochs: bool = False) -> str:
    if isinstance(f, (Path, str)):
        with Path(f).open('rb') as ff:
            return _decompress(ff, skip_strange_epochs)[1]
    elif isinstance(f, IOBase):
        if not f.seekable():
            raise ValueError('input stream must be seekable')
        if not isinstance(f.read(0), bytes):
            raise ValueError('input stream must be binary')
        return _decompress(f, skip_strange_epochs)[1]
    else:
        raise ValueError('input must be either a path or a binary stream')


def decompress_on_disk(path: Union[Path, str], *, skip_strange_epochs: bool = False) -> Path:
    path = Path(path)
    with path.open('rb') as f:
        is_obs, txt = _decompress(f, skip_strange_epochs=skip_strange_epochs)
    out_path = get_decompressed_path(path, is_obs)
    if out_path == path:
        # file does not need decompressing
        return out_path
    with out_path.open('w', encoding='ascii', errors='ignore') as f_out:
        f_out.write(txt)
    return out_path


def get_decompressed_path(path, is_obs):
    path = Path(path)
    parts = path.name.split('.')
    if len(parts) <= 1:
        raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
    if parts[-1].lower() in ['z', 'gz', 'bz2', 'zip']:
        parts.pop()
    suffix = parts[-1]
    if is_obs:
        is_valid = re.match(r'^(?:crx|rnx|\d\d[od])$', suffix, flags=re.I)
        if not is_valid:
            raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
        if suffix[2] == 'd':
            suffix = suffix[:2] + 'o'
        elif suffix[2] == 'D':
            suffix = suffix[:2] + 'O'
        elif suffix == 'crx':
            suffix = 'rnx'
        elif suffix == 'CRX':
            suffix = 'RNX'
    out_path = path.parent / '.'.join(parts[:-1] + [suffix])
    return out_path


def compress(f: Union[Path, str, BytesIO, BinaryIO], *, compression: str = 'gz',
             skip_strange_epochs: bool = False,
             reinit_every_nth: int = None) -> bytes:
    if isinstance(f, (Path, str)):
        txt = Path(f).read_bytes()
        return _compress(txt, compression, skip_strange_epochs, reinit_every_nth)[1]
    elif isinstance(f, IOBase):
        if not isinstance(f.read(0), bytes):
            raise ValueError('input stream must be binary')
        return _compress(f.read(), compression, skip_strange_epochs, reinit_every_nth)[1]
    else:
        raise ValueError('input must be either a path or a binary stream')


def compress_on_disk(path: Union[Path, str], *, compression: str = 'gz',
                     skip_strange_epochs: bool = False,
                     reinit_every_nth: int = None) -> Path:
    path = Path(path)
    if path.name.lower().endswith(('.gz', '.bz2', '.z', '.zip')):
        # already compressed
        return path
    is_obs, txt = _compress(path.read_bytes(), compression=compression,
                            skip_strange_epochs=skip_strange_epochs,
                            reinit_every_nth=reinit_every_nth)
    out_path = get_compressed_path(path, is_obs, compression)
    out_path.write_bytes(txt)
    return out_path


def get_compressed_path(path, is_obs, compression='gz'):
    path = Path(path)
    parts = path.name.split('.')
    if len(parts) < 2:
        raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
    suffix = parts[-1]
    if is_obs:
        is_valid = re.match(r'^(?:crx|rnx|\d\d[od])$', suffix, flags=re.I)
        if not is_valid:
            raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
        if suffix[2] == 'o':
            suffix = suffix[:2] + 'd'
        elif suffix[2] == 'O':
            suffix = suffix[:2] + 'D'
        elif suffix == 'rnx':
            suffix = 'crx'
        elif suffix == 'RNX':
            suffix = 'CRX'
    out_parts = parts[:-1] + [suffix]
    if compression != 'none':
        out_parts.append(compression)
    out_path = path.parent / '.'.join(out_parts)
    return out_path


def _is_lzw(magic_bytes: bytes) -> bool:
    return magic_bytes == b'\x1F\x9D'


def _is_gz(magic_bytes: bytes) -> bool:
    return magic_bytes == b'\x1F\x8B'


def _is_zip(magic_bytes: bytes) -> bool:
    return magic_bytes == b'\x50\x4B'


def _is_bz2(magic_bytes: bytes) -> bool:
    return magic_bytes == b'\x42\x5A'


def _decompress(f_in: IO, skip_strange_epochs: bool) -> (bool, str):
    magic_bytes = f_in.read(2)
    f_in.seek(0)
    if len(magic_bytes) != 2:
        raise ValueError('empty file')

    if _is_gz(magic_bytes):
        with gzip.open(f_in, 'rb') as f:
            return _decompress_hatanaka(f.read(), skip_strange_epochs)
    if _is_bz2(magic_bytes):
        with bz2.open(f_in, 'rb') as f:
            return _decompress_hatanaka(f.read(), skip_strange_epochs)
    elif _is_zip(magic_bytes):
        with zipfile.ZipFile(f_in, 'r') as z:
            flist = z.namelist()
            if len(flist) == 0:
                raise ValueError('zip archive is empty')
            elif len(flist) > 1:
                raise ValueError('more than one file in zip archive')
            with z.open(flist[0], 'r') as f:
                return _decompress_hatanaka(f.read(), skip_strange_epochs)
    elif _is_lzw(magic_bytes):
        return _decompress_hatanaka(unlzw(f_in.read()), skip_strange_epochs)
    else:
        return _decompress_hatanaka(f_in.read(), skip_strange_epochs)


def _decompress_hatanaka(txt: bytes, skip_strange_epochs) -> (bool, str):
    if len(txt) < 80:
        raise ValueError('file is too short to be a valid RINEX file')

    is_crinex = b'COMPACT RINEX' in txt[:80]
    if is_crinex:
        txt = crx2rnx(txt, skip_strange_epochs=skip_strange_epochs)
    is_obs = b'OBSERVATION DATA' in txt[:80]
    return is_obs, txt.decode('ascii', 'ignore')


def _compress(txt: bytes, compression, skip_strange_epochs, reinit_every_nth) -> (bool, bytes):
    is_obs, txt = _compress_hatanaka(txt, skip_strange_epochs, reinit_every_nth)
    if compression == 'gz':
        return is_obs, gzip.compress(txt)
    elif compression == 'bz2':
        return is_obs, bz2.compress(txt)
    elif compression == 'zip':
        raise NotImplementedError('zip compression is not supported')
    elif compression == 'none':
        return is_obs, txt
    else:
        raise ValueError(f"invalid compression '{compression}'")


def _compress_hatanaka(txt: bytes, skip_strange_epochs, reinit_every_nth) -> (bool, bytes):
    if len(txt) < 80:
        raise ValueError('file is too short to be a valid RINEX file')

    is_obs = b'OBSERVATION DATA' in txt[:80]
    if is_obs:
        return is_obs, rnx2crx(txt, skip_strange_epochs=skip_strange_epochs,
                               reinit_every_nth=reinit_every_nth)
    else:
        is_obs = b'COMPACT RINEX' in txt[:80]
        return is_obs, txt
