import os
import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_clib import build_clib as _build_clib


class build_clib(_build_clib):
    def build_libraries(self, libraries):
        cc = os.environ.get('CC')
        build_static = os.environ.get('BUILD_STATIC', 'n') == 'y'
        include_dirs = None
        library_dirs = None
        if cc is None:
            if self.compiler.compiler_type == 'msvc':
                self.compiler.initialize()
                cc = self.compiler.cc
                include_dirs = self.compiler.include_dirs
                library_dirs = self.compiler.library_dirs
            elif self.compiler.compiler_type == 'bcpp':
                cc = 'bcpp'
            elif hasattr(self.compiler, 'compiler_so') and self.compiler.compiler_so:
                # looks like ['gcc', '-pthread', '-Wl,--sysroot=/', ...]
                cc = self.compiler.compiler_so[0]
            if not cc:
                cc = find_c_compiler()
        output_dir = Path('build/lib/hatanaka/bin')
        output_dir.mkdir(parents=True, exist_ok=True)
        for executable, build_info in libraries:
            output = output_dir / executable
            build(build_info['sources'], output, cc, build_static, include_dirs, library_dirs)

        # copy to source dir as well for easier testing
        for f in list(output_dir.glob('rnx2crx*')) + list(output_dir.glob('crx2rnx*')):
            shutil.copy(f, 'hatanaka/bin/')


def build(sources, output, cc, build_static=False, include_dirs=None, library_dirs=None):
    if not all(Path(src).is_file() for src in sources):
        raise FileNotFoundError(sources)
    output = str(output)

    if cc.replace('.exe', '').endswith('cl'):  # msvc-like
        cmd = [cc, *sources, '/nologo', '/O2', '/Fe:' + output]
        if include_dirs:
            cmd += ['/I' + inc_dir for inc_dir in include_dirs]
        if library_dirs:
            cmd += ['/link']
            cmd += ['/LIBPATH:' + library_dir for library_dir in library_dirs]
    else:
        cmd = [cc, *sources, '-O3', '-Wno-unused-result', '-o', output]
        if include_dirs:
            cmd += ['-I' + inc_dir for inc_dir in include_dirs]
        if library_dirs:
            cmd += ['-L' + library_dir for library_dir in library_dirs]
        if build_static:
            cmd.append('-static')

    print(' '.join(cmd))
    subprocess.check_call(cmd)


def find_c_compiler(cc=None):
    compilers = ['cc', 'gcc', 'clang', 'icc', 'icl', 'cl', 'clang-cl']
    if cc is not None:
        compilers = [cc] + compilers
    available = list(filter(shutil.which, compilers))
    if not available:
        raise FileNotFoundError('No C compiler found on PATH')
    return available[0]


cmdclass = {'build_clib': build_clib}

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


    class bdist_wheel(_bdist_wheel):
        def get_tag(self):
            impl, abi_tag, plat_name = super().get_tag()
            impl = 'py3'
            abi_tag = 'none'
            plat_name = plat_name.replace('linux', 'manylinux1')
            return impl, abi_tag, plat_name


    cmdclass['bdist_wheel'] = bdist_wheel
except ImportError:
    pass

setup(
    libraries=[
        ('rnx2crx', {'sources': ['rnxcmp/source/rnx2crx.c']}),
        ('crx2rnx', {'sources': ['rnxcmp/source/crx2rnx.c']})
    ],
    cmdclass=cmdclass,
)
