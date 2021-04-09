import platform
import subprocess
import sys

from importlib_resources import path

import hatanaka.bin

__all__ = ['rnx2crx', 'crx2rnx']


def rnx2crx(args=None):
    return _run('rnx2crx', args)


def crx2rnx(args=None):
    return _run('crx2rnx', args)


def _run(program, args=None):
    if args is None:
        args = sys.argv[1:]
    if platform.system() == 'Windows':
        program += '.exe'
    with path(hatanaka.bin, program) as executable:
        p = subprocess.Popen([str(executable)] + args)
        p.wait()
        return p.returncode
