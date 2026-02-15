from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import os

TRACK_DIR = "TRACK-1.5.2"
SRC_DIR = os.path.join("src", TRACK_DIR)
LIB_FILES = ["libtrack.so", "libtrackutils.so"]

class BuildTrackExt(build_ext):
    def run(self):
        # Ensure TRACK source exists
        if not os.path.isdir(SRC_DIR):
            raise RuntimeError(f"{TRACK_DIR} not found in src/")

        print("Building TRACK shared libraries...")
        # Build both shared libraries via make
        for target in ["libtrack", "libtrackutils"]:
            subprocess.check_call(["make", target], cwd=SRC_DIR)

        # Copy .so files into build lib folder
        lib_dst = os.path.join(self.build_lib, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)
        for so_file in LIB_FILES:
            src = os.path.join(SRC_DIR, so_file)
            dst = os.path.join(lib_dst, so_file)
            self.copy_file(src, dst)
            print(f"{so_file} copied to {lib_dst}")

        super().run()

# Dummy Extensions to mark wheel as platform-specific
ext_modules = [
    Extension("pyTRACK._lib." + os.path.splitext(f)[0], sources=[])
    for f in LIB_FILES
]

setup(
    name="TRACK-pylib",
    version="0.4.1",
    description="Python-wrapped implementation of TRACK software",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildTrackExt},
    include_package_data=True,
    package_data={"pyTRACK": ["_lib/*.so", "data/**", "indat/**"]},
)
