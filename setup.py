from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess, os, shutil, tarfile, glob

TRACK_TARBALL = "TRACK-1.5.2.tar.bz2"
TRACK_DIR = "TRACK-1.5.2"

class BuildTrackExt(build_ext):
    def run(self):
        root = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(root, "src")
        track_src = os.path.join(src_dir, TRACK_DIR)

        if not os.path.isdir(track_src):
            with tarfile.open(os.path.join(src_dir, TRACK_TARBALL)) as tar:
                tar.extractall(src_dir)

        # Build shared libs via Makefile
        subprocess.check_call(["make"], cwd=src_dir)

        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)

        for so_file in ["libtrack.so", "libtrackutils.so"]:
            shutil.copy(os.path.join(src_dir, so_file), lib_dst)

        # Now call default build_ext which will compile the dummy C file
        super().run()

extensions = [
    Extension(
        "pyTRACK._lib._dummy_extension",
        sources=["pyTRACK/_lib/_dummy_extension.c"],
    )
]

setup(
    name="pyTRACK",
    version="0.4.1",
    packages=find_packages(),
    ext_modules=extensions,
    cmdclass={"build_ext": BuildTrackExt},
    include_package_data=True,
)
