# because Powershell does not do globbing...
import subprocess
import sys
from glob import glob

args = sys.argv[1:]
args[-1] = glob(args[-1])[0]
subprocess.run(['pip'] + args)
