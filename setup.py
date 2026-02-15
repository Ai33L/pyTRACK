from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
import subprocess
import os
import shutil
import tarfile
import glob

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

        print("Running make libtrack...")
        subprocess.check_call(["make", "libtrack"], cwd=src_dir)

        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)

        for so_file in ["libtrack.so", "libtrackutils.so"]:
            src = os.path.join(track_src, so_file)
            shutil.copy(src, lib_dst)
            print(f"{so_file} copied to {lib_dst}")

so_files = glob.glob(os.path.join("pyTRACK", "_lib", "*.so"))
ext_modules = []
for so in so_files:
    module_name = "pyTRACK._lib." + os.path.splitext(os.path.basename(so))[0]
    ext_modules.append(
        Extension(
            module_name,
            sources=[],
        )
    )

setup(
    name="pyTRACK",
    version="0.4.1",
    description="Python-wrapped implementation of the TRACK software",
    packages=find_packages(),
    cmdclass={"build_py": BuildTRACK},
    include_package_data=True,
    ext_modules=ext_modules,
)
