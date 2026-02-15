from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
import subprocess, os, shutil, glob, tarfile

TRACK_TARBALL = "TRACK-1.5.2.tar.bz2"
TRACK_DIR = "TRACK-1.5.2"

class BuildTRACK(build_py):
    def run(self):
        self.build_track()
        self.register_extensions()
        super().run()

    def build_track(self):
        root = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(root, "src")

        # Extract tarball if needed
        track_src = os.path.join(src_dir, TRACK_DIR)
        if not os.path.isdir(track_src):
            with tarfile.open(os.path.join(src_dir, TRACK_TARBALL)) as tar:
                tar.extractall(src_dir)

        # Build shared libraries in the src folder where Makefile lives
        subprocess.check_call(["make"], cwd=src_dir)

        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)

        for so_file in ["libtrack.so", "libtrackutils.so"]:
            src = os.path.join(src_dir, so_file)
            shutil.copy(src, lib_dst)

    def register_extensions(self):
        so_files = glob.glob(os.path.join("pyTRACK", "_lib", "*.so"))
        for so in so_files:
            module_name = "pyTRACK._lib." + os.path.splitext(os.path.basename(so))[0]
            ext = Extension(module_name, sources=[])
            if not hasattr(self.distribution, "ext_modules") or self.distribution.ext_modules is None:
                self.distribution.ext_modules = []
            self.distribution.ext_modules.append(ext)

setup(
    name="pyTRACK",
    version="0.4.1",
    description="Python-wrapped implementation of the TRACK software",
    packages=find_packages(),
    cmdclass={"build_py": BuildTRACK},
    include_package_data=True,
)
