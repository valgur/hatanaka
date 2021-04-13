import bz2
import gzip
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from .hatanaka import crx2rnx, rnx2crx

try:
    # unlzw is implemented in C and more efficient that Python-based unlzw3.
    # Much more difficult to install, though.
    from unlzw import unlzw
except ImportError:
    from unlzw3 import unlzw

__all__ = [
    'decompress', 'decompress_on_disk', 'get_decompressed_path',
    'compress', 'compress_on_disk', 'get_compressed_path'
]


def decompress(content: Union[Path, str, bytes], *,
               skip_strange_epochs: bool = False) -> bytes:
    """Decompress compressed RINEX files.

    Any RINEX files compressed with Hatanaka compression (.crx|.##d) and/or with a conventional
    compression format (.gz|.Z|.zip|.bz2) are decompressed to their plain RINEX counterpart.
    Already decompressed files are returned as is.

    Compression type is deduced automatically from the file contents.

    Parameters
    ----------
    content : Path or str or bytes
        Path to a compressed RINEX file or file contents as a bytes object.
    skip_strange_epochs : bool, default False
        For Hatanaka decompression.
        Warn and skip strange epochs instead of raising an exception.
        This option may be used for salvaging usable data when middle of the Compact
        RINEX file is missing. The data after the missing part, are, however, useless
        until the compression operation of all data are initialized at some epoch.
        Using this together with of reinit_every_nth option of rnx2crx may be effective.
        Caution: It is assumed that no change in the list of data types happens in the
        lost part of the data.

    Returns
    -------
    bytes
        Decompressed RINEX file contents.

    Raises
    ------
    HatanakaException
        On any errors during Hatanaka decompression.
    ValueError
        For invalid file contents.
    """
    if isinstance(content, (Path, str)):
        content = _decompress(Path(content).read_bytes(), skip_strange_epochs)[1]
    elif not isinstance(content, bytes):
        raise ValueError('input must be either a path or a binary string')
    return _decompress(content, skip_strange_epochs)[1]


def decompress_on_disk(path: Union[Path, str], *, skip_strange_epochs: bool = False) -> Path:
    """Decompress compressed RINEX files and write the resulting file to disk.

    Any RINEX files compressed with Hatanaka compression (.crx|.##d) and/or with a conventional
    compression format (.gz|.Z|.zip|.bz2) are decompressed to their plain RINEX counterpart.
    Already decompressed files are ignored.

    Compression type is deduced automatically from the file contents.

    Parameters
    ----------
    path : Path or str
        Path to a compressed RINEX file.
    skip_strange_epochs : bool, default False
        For Hatanaka decompression.
        Warn and skip strange epochs instead of raising an exception.
        This option may be used for salvaging usable data when middle of the Compact
        RINEX file is missing. The data after the missing part, are, however, useless
        until the compression operation of all data are initialized at some epoch.
        Using this together with of reinit_every_nth option of rnx2crx may be effective.
        Caution: It is assumed that no change in the list of data types happens in the
        lost part of the data.

    Returns
    -------
    Path
        Path to the decompressed RINEX file.

    Raises
    ------
    HatanakaException
        On any errors during Hatanaka decompression.
    ValueError
        For invalid file contents.
    """
    path = Path(path)
    is_obs, txt = _decompress(path.read_bytes(), skip_strange_epochs=skip_strange_epochs)
    out_path = get_decompressed_path(path)
    if out_path == path:
        # file does not need decompressing
        return out_path
    with out_path.open('wb') as f_out:
        f_out.write(txt)
    return out_path


def get_decompressed_path(path: Union[Path, str]) -> Path:
    """Get the decompressed path corresponding to a compressed RINEX file after decompression.

    Parameters
    ----------
    path : path or str
        Path to the compressed RINEX file.

    Returns
    -------
    Path
        The path of the resulting RINEX file after decompression.
    """
    path = Path(path)
    parts = path.name.split('.')
    if len(parts) <= 1:
        raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
    if parts[-1].lower() in ['z', 'gz', 'bz2', 'zip']:
        parts.pop()
    suffix = parts[-1]
    if len(parts) == 1:
        return path.parent / (parts[0] + '.rnx')
    elif re.fullmatch(r'\d\dd', suffix):
        suffix = suffix[:2] + 'o'
    elif re.fullmatch(r'\d\dD', suffix):
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
    """Compress RINEX files.

    Applies Hatanaka (if observation data) and optionally a conventional compression (gzip by default)
    to the provided RINEX file. Already compressed files are returned as is.

    Parameters
    ----------
    content : Path or str or bytes
        Path to a RINEX file or file contents as a bytes object.
    compression : 'gz' (default), 'bz2', or 'none'
        Which compression (if any) to apply in addition to the Hatanaka compression.
    skip_strange_epochs : bool, default False
        For Hatanaka compression. Warn and skip strange epochs instead of raising an exception.
    reinit_every_nth : int, optional
        For Hatanaka compression. Initialize the compression operation at every # epochs.
        When some part of the Compact RINEX file is lost, the data can not be recovered
        thereafter until all the data arc are initialized for differential operation.
        This option may be used to increase chances to recover parts of data by using the
        skip_strange option of crx2rnx at the cost of increasing the file size.

    Returns
    -------
    bytes
        Compressed RINEX file contents.

    Raises
    ------
    HatanakaException
        On any errors during Hatanaka compression.
    ValueError
        For invalid file contents.
    """
    if isinstance(content, (Path, str)):
        content = Path(content).read_bytes()
    elif not isinstance(content, bytes):
        raise ValueError('input must be either a path or a binary string')
    return _compress(content, compression, skip_strange_epochs, reinit_every_nth)[1]


def compress_on_disk(path: Union[Path, str], *, compression: str = 'gz',
                     skip_strange_epochs: bool = False,
                     reinit_every_nth: int = None) -> Path:
    """Compress RINEX files.

    Applies Hatanaka (if observation data) and optionally a conventional compression (gzip by default)
    to the provided RINEX file. Already compressed files are ignored.

    Parameters
    ----------
    path : Path or str
        Path to a RINEX file.
    compression : 'gz' (default), 'bz2', or 'none'
        Which compression (if any) to apply in addition to the Hatanaka compression.
    skip_strange_epochs : bool, default False
        For Hatanaka compression. Warn and skip strange epochs instead of raising an exception.
    reinit_every_nth : int, optional
        For Hatanaka compression. Initialize the compression operation at every # epochs.
        When some part of the Compact RINEX file is lost, the data can not be recovered
        thereafter until all the data arc are initialized for differential operation.
        This option may be used to increase chances to recover parts of data by using the
        skip_strange option of crx2rnx at the cost of increasing the file size.

    Returns
    -------
    Path
        Path to the compressed RINEX file.

    Raises
    ------
    HatanakaException
        On any errors during Hatanaka compression.
    ValueError
        For invalid file contents.
    """
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


def get_compressed_path(path, is_obs=None, compression='gz'):
    """Get the compressed path corresponding to a RINEX file after compression.

    Parameters
    ----------
    path : path or str
        Path to the RINEX file being compressed.
    is_obs : bool, optional
        Whether the RINEX file contains observation data.
        Needed for correct renaming of files with .rnx suffix,
        which will be Hatanaka-compressed if they contain observation data.
    compression : 'gz' (default), 'bz2', or 'none'
        Compression (if any) applied in addition to the Hatanaka compression.

    Returns
    -------
    Path
        The path of the resulting RINEX file after compression.
    """
    path = Path(path)
    parts = path.name.split('.')
    if len(parts) < 2:
        raise ValueError(f"'{str(path)}' is not a valid RINEX file name")
    suffix = parts[-1]
    if re.fullmatch(r'\d\do', suffix):
        suffix = suffix[:2] + 'd'
    elif re.fullmatch(r'\d\dO', suffix):
        suffix = suffix[:2] + 'D'
    elif suffix.lower() == 'rnx':
        if is_obs is None:
            raise ValueError(f'whether {path.name} contains observation data is ambiguous, '
                             'need to specify is_obs argument')
        elif is_obs:
            if suffix == 'RNX':
                suffix = 'CRX'
            else:
                suffix = 'crx'
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
