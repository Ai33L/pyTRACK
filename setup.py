from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import tarfile
import os
import shutil

TRACK_TARBALL = "TRACK-1.5.2.tar.bz2"
TRACK_DIR = "TRACK-1.5.2"

class BuildTRACK(build_py):
    def run(self):
        self.build_track()
        super().run()

    def build_track(self):
        root = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(root, "src")
        build_dir = os.path.join(root, "build", "track")

        os.makedirs(build_dir, exist_ok=True)

        tarball = os.path.join(src_dir, TRACK_TARBALL)

        # Extract legacy source
        with tarfile.open(tarball) as tar:
            tar.extractall(build_dir)

        track_src = os.path.join(build_dir, TRACK_DIR)

        # Build shared library
        subprocess.check_call(
            ["make", "libtrack"],
            cwd=track_src
        )

        # Copy libtrack.so into Python package
        lib_src = os.path.join(track_src, "src", "libtrack.so")
        lib_dst = os.path.join(root, "pyTRACK", "_lib")

        os.makedirs(lib_dst, exist_ok=True)
        shutil.copy(lib_src, lib_dst)

setup(
    name="pyTRACK",
    version="0.1.0",
    description="Python wrapper for the TRACK tracking system",
    packages=find_packages(),
    cmdclass={"build_py": BuildTRACK},
    include_package_data=True,
)
