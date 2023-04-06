import os
import shutil
from distutils import ccompiler
from pathlib import Path
from tempfile import TemporaryDirectory

from setuptools import setup
from setuptools.command.build_clib import build_clib as _build_clib


class build_clib(_build_clib):
    def build_libraries(self, libraries):
        cc = ccompiler.new_compiler()
        link_flags = []
        if cc.compiler_type == "msvc":
            compile_flags = ["/O2"]
        else:
            compile_flags = ["-O3", "-Wno-unused-result"]

        output_dir = Path("build/lib/hatanaka/bin")
        output_dir.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory() as tmp_dir:
            for executable, build_info in libraries:
                obj_files = cc.compile(
                    sources=build_info["sources"],
                    extra_postargs=compile_flags,
                    output_dir=tmp_dir,
                )
                cc.link_executable(
                    obj_files,
                    executable,
                    output_dir=str(output_dir),
                    extra_postargs=link_flags,
                )

        # copy to source dir as well for easier testing
        executables = list(output_dir.glob("rnx2crx*")) + list(output_dir.glob("crx2rnx*"))
        assert len(executables) == 2
        for f in executables:
            shutil.copy(f, "hatanaka/bin/")


cmdclass = {"build_clib": build_clib}

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    from auditwheel.policy import get_policy_name, POLICY_PRIORITY_HIGHEST

    class bdist_wheel(_bdist_wheel):
        def get_tag(self):
            impl, abi_tag, plat_name = super().get_tag()
            impl = "py3"
            abi_tag = "none"
            if "linux" in plat_name:
                plat_name = get_policy_name(POLICY_PRIORITY_HIGHEST)
            return impl, abi_tag, plat_name

    cmdclass["bdist_wheel"] = bdist_wheel
except ImportError:
    pass

setup(
    libraries=[
        ("rnx2crx", {"sources": ["rnxcmp/source/rnx2crx.c"]}),
        ("crx2rnx", {"sources": ["rnxcmp/source/crx2rnx.c"]}),
    ],
    cmdclass=cmdclass,
)
