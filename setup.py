import os
import shutil
import subprocess

from setuptools import setup
from setuptools.command.build_clib import build_clib
from setuptools.command.develop import develop


class Build(build_clib):
    def build_libraries(self, libraries):
        cc = os.environ.get('CC')
        if cc is None:
            if self.compiler.compiler:
                # self.compiler.compiler content is ['gcc', '-pthread', '-Wl,--sysroot=/', ...]
                cc = self.compiler.compiler[0]
            else:
                cc = find_c_compiler()
        output_dir = 'build/lib/hatanaka/bin'
        for executable, build_info in libraries:
            output = os.path.join(output_dir, executable)
            build(build_info['sources'], output, cc)


def build(sources, output, cc):
    if not all(os.path.isfile(src) for src in sources):
        raise FileNotFoundError(sources)

    if cc.endswith("cl"):  # msvc-like
        cmd = [cc, *sources, "/Fe:" + output]
    else:
        cmd = [cc, *sources, "-O3", "-Wno-unused-result", "-o", output]

    print(" ".join(cmd))
    subprocess.check_call(cmd)


def find_c_compiler(cc=None):
    compilers = ["cc", "gcc", "clang", "icc", "icl", "cl", "clang-cl"]
    if cc is not None:
        compilers = [cc] + compilers
    available = list(filter(shutil.which, compilers))
    if not available:
        raise FileNotFoundError("No C compiler found on PATH")
    return available[0]


class Develop(develop):
    def run(self):
        self.run_command('build_clib')
        shutil.copy('build/lib/hatanaka/bin/rnx2crx', 'hatanaka/bin/')
        shutil.copy('build/lib/hatanaka/bin/crx2rnx', 'hatanaka/bin/')
        super().run()


setup(
    libraries=[
        ('rnx2crx', {'sources': ['rnxcmp/source/rnx2crx.c']}),
        ('crx2rnx', {'sources': ['rnxcmp/source/crx2rnx.c']})
    ],
    cmdclass={
        'build_clib': Build,
        'develop': Develop,
    }
)
