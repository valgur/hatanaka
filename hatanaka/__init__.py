import re
import subprocess
from io import IOBase
from subprocess import PIPE
from typing import AnyStr, IO, Union
from warnings import warn

import hatanaka.bin
from importlib_resources import path

__all__ = ['rnx2crx', 'crx2rnx', 'HatanakaException']


def rnx2crx(rnx_content: Union[AnyStr, IO], reinit_every_nth: int = None, skip_strange: bool = False) -> AnyStr:
    extra_args = []
    if reinit_every_nth:
        assert isinstance(reinit_every_nth, int)
        extra_args += ['-e', '{:d}'.format(reinit_every_nth)]
    if skip_strange:
        extra_args += ['-s']
    return _run('rnx2crx', rnx_content, extra_args)


def crx2rnx(crx_content: Union[AnyStr, IO], skip_strange: bool = False) -> AnyStr:
    extra_args = []
    if skip_strange:
        extra_args = ['-s']
    return _run('crx2rnx', crx_content, extra_args)


def is_binary(f: IO) -> bool:
    return isinstance(f.read(0), bytes)


class HatanakaException(RuntimeError):
    pass


def _run(program, content, extra_args=[]):
    with path(hatanaka.bin, program) as executable:
        if isinstance(content, IOBase):
            encoding = 'ascii' if not is_binary(content) else None
            result = subprocess.run(
                [str(executable), "-"] + extra_args, stdout=PIPE, stderr=PIPE, stdin=content, encoding=encoding)
        else:
            encoding = 'ascii' if isinstance(content, str) else None
            result = subprocess.run(
                [str(executable), "-"] + extra_args, stdout=PIPE, stderr=PIPE, input=content, encoding=encoding)

    stderr = result.stderr
    if not encoding:
        stderr = stderr.decode()

    if result.returncode not in (0, 2):
        stderr = re.sub('^ +', '', stderr, flags=re.M)
        stderr = re.sub('\n(?!WARNING|ERROR)', ' ', stderr)
        stderr = re.sub('^ERROR *: *', '', stderr, flags=re.M)
        raise HatanakaException(stderr)

    if result.returncode == 2 and not stderr:
        warn(f'{program}: exited with an unspecified warning')
    if stderr:
        stderr = re.sub('^ +', '', stderr.strip(), flags=re.M)
        stderr = stderr.replace('\n', ' ')
        stderr = re.sub('^ *WARNING *:? *', '\n', stderr, flags=re.M)
        stderr = re.sub('^\n', '', stderr)
        warn(f'{program}: {stderr}')

    return result.stdout
