import bz2
import gzip
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from .hatanaka import crx2rnx, rnx2crx

try:
    from unlzw import unlzw
except ImportError:
    from unlzw3 import unlzw

__all__ = [
    'decompress', 'decompress_on_disk', 'get_decompressed_path',
    'compress', 'compress_on_disk', 'get_compressed_path'
]


def decompress(content: Union[Path, str, bytes], *,
               skip_strange_epochs: bool = False) -> bytes:
    if isinstance(content, (Path, str)):
        content = _decompress(Path(content).read_bytes(), skip_strange_epochs)[1]
    elif not isinstance(content, bytes):
        raise ValueError('input must be either a path or a binary string')
    return _decompress(content, skip_strange_epochs)[1]


def decompress_on_disk(path: Union[Path, str], *, skip_strange_epochs: bool = False) -> Path:
    path = Path(path)
    is_obs, txt = _decompress(path.read_bytes(), skip_strange_epochs=skip_strange_epochs)
    out_path = get_decompressed_path(path, is_obs)
    if out_path == path:
        # file does not need decompressing
        return out_path
    with out_path.open('wb') as f_out:
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


def compress(content: Union[Path, str, bytes], *, compression: str = 'gz',
             skip_strange_epochs: bool = False,
             reinit_every_nth: int = None) -> bytes:
    if isinstance(content, (Path, str)):
        content = Path(content).read_bytes()
    elif not isinstance(content, bytes):
        raise ValueError('input must be either a path or a binary string')
    return _compress(content, compression, skip_strange_epochs, reinit_every_nth)[1]


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


def _decompress(txt: bytes, skip_strange_epochs: bool) -> (bool, bytes):
    if len(txt) < 2:
        raise ValueError('empty file')
    magic_bytes = txt[:2]

    if _is_gz(magic_bytes):
        return _decompress_hatanaka(gzip.decompress(txt), skip_strange_epochs)
    if _is_bz2(magic_bytes):
        return _decompress_hatanaka(bz2.decompress(txt), skip_strange_epochs)
    elif _is_zip(magic_bytes):
        with zipfile.ZipFile(BytesIO(txt), 'r') as z:
            flist = z.namelist()
            if len(flist) == 0:
                raise ValueError('zip archive is empty')
            elif len(flist) > 1:
                raise ValueError('more than one file in zip archive')
            with z.open(flist[0], 'r') as f:
                return _decompress_hatanaka(f.read(), skip_strange_epochs)
    elif _is_lzw(magic_bytes):
        return _decompress_hatanaka(unlzw(txt), skip_strange_epochs)
    else:
        return _decompress_hatanaka(txt, skip_strange_epochs)


def _decompress_hatanaka(txt: bytes, skip_strange_epochs) -> (bool, bytes):
    if len(txt) < 80:
        raise ValueError('file is too short to be a valid RINEX file')

    is_crinex = b'COMPACT RINEX' in txt[:80]
    if is_crinex:
        txt = crx2rnx(txt, skip_strange_epochs=skip_strange_epochs)
    is_obs = b'OBSERVATION DATA' in txt[:80]
    return is_obs, txt


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
