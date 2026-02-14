from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import os
import shutil
import tarfile

TRACK_TARBALL = "TRACK-1.5.2.tar.bz2"
TRACK_DIR = "TRACK-1.5.2"

class BuildTRACK(build_py):
    def run(self):
        self.build_track()
        super().run()

    def build_track(self):
        root = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(root, "src")
        track_src = os.path.join(src_dir, TRACK_DIR)

        # Extract tarball if needed
        if not os.path.isdir(track_src):
            print(f"Extracting {TRACK_TARBALL}...")
            with tarfile.open(os.path.join(src_dir, TRACK_TARBALL)) as tar:
                tar.extractall(src_dir)

        # Run Makefile to build libtrack.so
        print("Running make libtrack...")
        subprocess.check_call(["make", "libtrack"], cwd=src_dir)

        # Copy built .so into package _lib folder
        lib_src = os.path.join(track_src, "libtrack.so")
        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)
        shutil.copy(lib_src, lib_dst)
        lib_src = os.path.join(track_src, "libtrackutils.so")
        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        shutil.copy(lib_src, lib_dst)
        print(f"libtrack.so and libtrackutils.so copied to {lib_dst}")

setup(
    name="pyTRACK",
    version="0.4.0",
    description="Python-wrapped implementation of the TRACK software",
    packages=find_packages(),
    cmdclass={"build_py": BuildTRACK},
    include_package_data=True,
)
