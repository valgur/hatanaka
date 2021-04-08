import subprocess
from typing import AnyStr

import hatanaka.bin
from importlib_resources import path

__all__ = ['rnx2crx', 'crx2rnx']


def rnx2crx(rnx_content: AnyStr) -> AnyStr:
    encoding = 'ascii' if isinstance(rnx_content, str) else None
    with path(hatanaka.bin, 'rnx2crx') as executable:
        return subprocess.check_output([str(executable), "-"], input=rnx_content, encoding=encoding)


def crx2rnx(crx_content: AnyStr) -> AnyStr:
    encoding = 'ascii' if isinstance(crx_content, str) else None
    with path(hatanaka.bin, 'crx2rnx') as executable:
        return subprocess.check_output([str(executable), "-"], input=crx_content, encoding=encoding)
