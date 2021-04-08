import os
import shutil
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_clib import build_clib


class Build(build_clib):
    def build_libraries(self, libraries):
        cc = os.environ.get('CC')
        if cc is None and self.compiler.compiler:
            # self.compiler.compiler content is ['gcc', '-pthread', '-Wl,--sysroot=/', ...]
            cc = self.compiler.compiler[0]
        output_dir = 'hatanaka/bin'
        for executable, build_info in libraries:
            output = os.path.join(output_dir, executable)
            build(build_info['sources'], output, cc=cc)


def build(sources, output, cc=None):
    if not all(os.path.isfile(src) for src in sources):
        raise FileNotFoundError(sources)

    cc = find_c_compiler(cc)
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


setup(
    name="hatanaka",
    version="4.0.8.0",
    author="Martin Valgur",
    author_email="martin.valgur@gmail.com",
    description="Compress/decompress RINEX observation files with Hatanaka compression",
    long_description="",
    package_dir={"": "hatanaka"},
    packages=find_packages(where="hatanaka"),
    python_requires=">=3.6",
    libraries=[
        ('rnx2crx', {'sources': ['rnxcmp/source/rnx2crx.c']}),
        ('crx2rnx', {'sources': ['rnxcmp/source/crx2rnx.c']})
    ],
    cmdclass={'build_clib': Build},
    zip_safe=False,
    install_requires=['importlib_resources'],
    extras_require={'test': ['pytest']},
)
