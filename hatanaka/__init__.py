import subprocess
from io import IOBase
from typing import AnyStr, IO, Union

import hatanaka.bin
from importlib_resources import path

__all__ = ['rnx2crx', 'crx2rnx']


def rnx2crx(rnx_content: Union[AnyStr, IO]) -> AnyStr:
    return _run('rnx2crx', rnx_content)


def crx2rnx(crx_content: Union[AnyStr, IO]) -> AnyStr:
    return _run('crx2rnx', crx_content)


def is_binary(f: IO) -> bool:
    return isinstance(f.read(0), bytes)


def _run(program, content, extra_args=[]):
    with path(hatanaka.bin, program) as executable:
        if isinstance(content, IOBase):
            encoding = 'ascii' if not is_binary(content) else None
            return subprocess.check_output(
                [str(executable), "-"] + extra_args, stdin=content, encoding=encoding)
        else:
            encoding = 'ascii' if isinstance(content, str) else None
            return subprocess.check_output(
                [str(executable), "-"] + extra_args, input=content, encoding=encoding)
