import platform
import re
import subprocess
from io import IOBase
from subprocess import PIPE
from typing import AnyStr, IO, Union
from warnings import warn

from importlib_resources import path

import hatanaka.bin

__all__ = ['rnx2crx', 'crx2rnx', 'HatanakaException']


def rnx2crx(rnx_content: Union[AnyStr, IO], *, reinit_every_nth: int = None,
            skip_strange_epochs: bool = False) -> AnyStr:
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
        skip_strange option of crx2rnx at the cost of increasing the file size.
    skip_strange_epochs : bool, default False
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
    if reinit_every_nth is not None and reinit_every_nth > 0:
        assert isinstance(reinit_every_nth, int)
        extra_args += ['-e', '{:d}'.format(reinit_every_nth)]
    if skip_strange_epochs:
        extra_args += ['-s']
    return _run('rnx2crx', rnx_content, extra_args)


def crx2rnx(crx_content: Union[AnyStr, IO], *, skip_strange_epochs: bool = False) -> AnyStr:
    """Restore the original RINEX observation file from a Compact RINEX file.

    Parameters
    ----------
    crx_content : str or bytes or file-like
        Compact RINEX observation file content
    skip_strange_epochs : bool, default False
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
    if skip_strange_epochs:
        extra_args = ['-s']
    return _run('crx2rnx', crx_content, extra_args)


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
        proc = _popen(program, ['-'] + extra_args,
                      stdout=PIPE, stderr=PIPE, stdin=content, encoding=encoding, errors=errors)
        stdout, stderr = proc.communicate()
    else:
        if isinstance(content, str):
            encoding = 'ascii'
            errors = 'ignore'
        proc = _popen(program, ['-'] + extra_args,
                      stdout=PIPE, stderr=PIPE, stdin=PIPE, encoding=encoding, errors=errors)
        stdout, stderr = proc.communicate(content)
    retcode = proc.poll()

    _check(program, retcode, stderr)
    return stdout


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


def _popen(program, args, **kwargs):
    if platform.system() == 'Windows':
        program += '.exe'
    with path(hatanaka.bin, program) as executable:
        return subprocess.Popen([str(executable)] + args, **kwargs)
