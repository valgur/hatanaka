import platform
import subprocess
import sys
from typing import List, Optional

from importlib_resources import path

import hatanaka.bin

__all__ = ['rnx2crx', 'crx2rnx']


def rnx2crx(args: Optional[List[str]] = None) -> int:
    return _run('rnx2crx', args)


def crx2rnx(args: Optional[List[str]] = None) -> int:
    return _run('crx2rnx', args)


def _run(program, args=None):
    if args is None:
        args = sys.argv[1:]
    p = _popen(program, args)
    p.wait()
    return p.returncode


def _popen(program, args, **kwargs):
    if platform.system() == 'Windows':
        program += '.exe'
    with path(hatanaka.bin, program) as executable:
        return subprocess.Popen([str(executable)] + args, **kwargs)
