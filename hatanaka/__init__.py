import re
from io import IOBase
from pathlib import Path
from subprocess import PIPE
from typing import AnyStr, IO, Union
from warnings import warn

import hatanaka.bin
from hatanaka import cli

__version__ = '1.0.0'
rnxcmp_version = '4.0.8'
__all__ = ['rnx2crx', 'crx2rnx', 'rnx2crx_file', 'crx2rnx_file', 'HatanakaException',
           'rnxcmp_version']


def rnx2crx(rnx_content: Union[AnyStr, IO], reinit_every_nth: int = None,
            skip_strange: bool = False) -> AnyStr:
    """Compress a RINEX observation file into the Compact RINEX format.

    Parameters
    ----------
    rnx_content : str or bytes or file-like
        RINEX observation file content
    reinit_every_nth : int, optional
        Initialize the compression operation at every # epochs.
        When some part of the Compact RINEX file is lost, the data can not be recovered
        thereafter until all the data arc are initialized for differential operation.
        This option may be used to increase chances to recover parts of data by using the
        skip_strange option of crx2rnx at the cost of increase of file size.
    skip_strange : bool, default False
        Warn and skip strange epochs instead of raising an exception.

    Returns
    -------
    str or bytes
        Compressed RINEX file content. bytes if rnx_content was binary, otherwise str.

    Raises
    ------
    HatanakaException
        On any errors during compression.

    Warns
    -----
    Any non-critical problems during compression will be raised as warnings.
    """
    extra_args = []
    if reinit_every_nth:
        assert isinstance(reinit_every_nth, int)
        extra_args += ['-e', '{:d}'.format(reinit_every_nth)]
    if skip_strange:
        extra_args += ['-s']
    return _run('rnx2crx', rnx_content, extra_args)


def crx2rnx(crx_content: Union[AnyStr, IO], skip_strange: bool = False) -> AnyStr:
    """Restore the original RINEX observation file from a Compact RINEX file.

    Parameters
    ----------
    crx_content : str or bytes or file-like
        Compact RINEX observation file content
    skip_strange : bool, default False
        Warn and skip strange epochs instead of raising an exception.
        This option may be used for salvaging usable data when middle of the Compact
        RINEX file is missing. The data after the missing part, are, however, useless
        until the compression operation of all data are initialized at some epoch.
        Using this together with of reinit_every_nth option of rnx2crx may be effective.
        Caution: It is assumed that no change in the list of data types happens in the
        lost part of the data.

    Returns
    -------
    str or bytes
        Decompressed RINEX file content. bytes if crx_content was binary, otherwise str.

    Raises
    ------
    HatanakaException
        On any errors during decompression.

    Warns
    -----
    Any non-critical problems during decompression will be raised as warnings.
    """
    extra_args = []
    if skip_strange:
        extra_args = ['-s']
    return _run('crx2rnx', crx_content, extra_args)


def rnx2crx_file(rnx_file: Union[str, Path], reinit_every_nth: int = None,
                 skip_strange: bool = False, overwrite: bool = False,
                 delete_on_success: bool = False) -> str:
    """Compress a RINEX observation file into the Compact RINEX format.

    Parameters
    ----------
    rnx_file : str or Path
        RINEX observation file path
    reinit_every_nth : int, optional
        Initialize the compression operation at every # epochs.
        When some part of the Compact RINEX file is lost, the data can not be recovered
        thereafter until all the data arc are initialized for differential operation.
        This option may be used to increase chances to recover parts of data by using the
        skip_strange option of crx2rnx at the cost of increase of file size.
    skip_strange : bool, default False
        Warn and skip strange epochs instead of raising an exception.
    overwrite : bool, default False
        Allow the output file to overwrite an existing one.
    delete_on_success : bool, default False
        Delete the input file if conversion finishes without errors and warnings.

    Returns
    -------
    str
        Path of the resulting compressed RINEX file.

    Raises
    ------
    HatanakaException
        On any errors during compression.

    Warns
    -----
    Any non-critical problems during compression will be raised as warnings.
    """
    args = []
    if reinit_every_nth:
        assert isinstance(reinit_every_nth, int)
        args += ['-e', '{:d}'.format(reinit_every_nth)]
    if skip_strange:
        args.append('-s')
    if overwrite:
        args.append('-f')
    if delete_on_success:
        args.append('-d')
    _run_file('rnx2crx', rnx_file, args)

    # Construct the expect output file name
    suffix = Path(rnx_file).suffix
    if suffix[3] == 'o':
        suffix = suffix[:3] + 'd' + suffix[4:]
    elif suffix[3] == 'O':
        suffix = suffix[:3] + 'D' + suffix[4:]
    elif suffix == '.rnx':
        suffix = '.crx'
    elif suffix == '.RNX':
        suffix = '.CRX'
    out_file = Path(rnx_file).with_suffix(suffix)
    print(suffix, rnx_file, out_file)
    assert out_file != rnx_file
    assert out_file.exists()
    return str(out_file)


def crx2rnx_file(crx_file: Union[str, Path], skip_strange: bool = False, overwrite: bool = False,
                 delete_on_success: bool = False) -> str:
    """Restore the original RINEX observation file from a Compact RINEX file.

    Parameters
    ----------
    crx_file : str or bytes or file-like
        Compact RINEX observation file path
    skip_strange : bool, default False
        Warn and skip strange epochs instead of raising an exception.
        This option may be used for salvaging usable data when middle of the Compact
        RINEX file is missing. The data after the missing part, are, however, useless
        until the compression operation of all data are initialized at some epoch.
        Using this together with of reinit_every_nth option of rnx2crx may be effective.
        Caution: It is assumed that no change in the list of data types happens in the
        lost part of the data.
    overwrite : bool, default False
        Allow the output file to overwrite an existing one.
    delete_on_success : bool, default False
        Delete the input file if conversion finishes without errors and warnings.

    Returns
    -------
    str
        Path of the resulting decompressed RINEX file.

    Raises
    ------
    HatanakaException
        On any errors during decompression.

    Warns
    -----
    Any non-critical problems during decompression will be raised as warnings.
    """
    args = []
    if skip_strange:
        args.append('-s')
    if overwrite:
        args.append('-f')
    if delete_on_success:
        args.append('-d')

    _run_file('crx2rnx', crx_file, args)

    # Construct the expect output file name
    suffix = Path(crx_file).suffix
    if suffix[3] == 'd':
        suffix = suffix[:3] + 'o' + suffix[4:]
    elif suffix[3] == 'D':
        suffix = suffix[:3] + 'O' + suffix[4:]
    elif suffix == '.crx':
        suffix = '.rnx'
    elif suffix == '.CRX':
        suffix = '.RNX'
    out_file = Path(crx_file).with_suffix(suffix)
    assert out_file != crx_file
    assert out_file.exists()
    return str(out_file)


class HatanakaException(RuntimeError):
    pass


def _is_binary(f: IO) -> bool:
    return isinstance(f.read(0), bytes)


def _run(program, content, extra_args=[]):
    encoding = None
    errors = None
    if isinstance(content, IOBase):
        if not _is_binary(content):
            encoding = 'ascii'
            # let's be relaxed about non-ascii symbols as long as it decodes successfully
            errors = 'ignore'
        proc = cli._popen(program, ['-'] + extra_args,
                          stdout=PIPE, stderr=PIPE, stdin=content, encoding=encoding, errors=errors)
        stdout, stderr = proc.communicate()
    else:
        if isinstance(content, str):
            encoding = 'ascii'
            errors = 'ignore'
        proc = cli._popen(program, ['-'] + extra_args,
                          stdout=PIPE, stderr=PIPE, stdin=PIPE, encoding=encoding, errors=errors)
        stdout, stderr = proc.communicate(content)
    retcode = proc.poll()

    _check(program, retcode, stderr)
    return stdout


def _run_file(program, file, args):
    if not Path(file).exists():
        raise FileNotFoundError(f"'{file}' does not exist")
    if not Path(file).is_file():
        raise FileNotFoundError(f"'{file}' is not a file")
    proc = cli._popen(program, [str(file)] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = proc.communicate()
    retcode = proc.poll()
    _check(program, retcode, stderr)


def _check(program, retcode, stderr):
    """Raise HatanakaException on errors and report warnings"""
    if isinstance(stderr, bytes):
        stderr = stderr.decode('ascii', errors='backslashreplace').strip()
    if retcode not in (0, 2):
        stderr = re.sub('^ +', '', stderr, flags=re.M)
        stderr = re.sub('\n(?!WARNING|ERROR)', ' ', stderr)
        stderr = re.sub('^ERROR *: *', '', stderr, flags=re.M)
        raise HatanakaException(stderr)
    if retcode == 2 and not stderr:
        warn(f'{program}: exited with an unspecified warning')
    if stderr:
        stderr = re.sub('^ +', '', stderr.strip(), flags=re.M)
        stderr = stderr.replace('\n', ' ')
        stderr = re.sub('^ *WARNING *:? *', '\n', stderr, flags=re.M)
        stderr = re.sub('^\n', '', stderr)
        warn(f'{program}: {stderr}')
