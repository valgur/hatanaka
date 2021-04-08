import subprocess
import sys

from importlib_resources import path

import hatanaka.bin


def rnx2crx():
    return _run('rnx2crx')


def crx2rnx():
    return _run('crx2rnx')


def _run(program):
    with path(hatanaka.bin, program) as executable:
        args = [executable] + sys.argv[1:]
        p = subprocess.Popen(args)
        p.wait()
        return p.returncode
