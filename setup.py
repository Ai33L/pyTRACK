from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
import subprocess, os, shutil, tarfile, glob

TRACK_TARBALL = "TRACK-1.5.2.tar.bz2"
TRACK_DIR = "TRACK-1.5.2"

class BuildTRACK(build_py):
    def run(self):
        self.build_track()
        self.build_extensions()
        super().run()

    def build_track(self):
        root = os.path.abspath(os.path.dirname(__file__))
        track_src = os.path.join(root, "src", TRACK_DIR)
        if not os.path.isdir(track_src):
            with tarfile.open(os.path.join(root, "src", TRACK_TARBALL)) as tar:
                tar.extractall(os.path.join(root, "src"))
        subprocess.check_call(["make", "libtrack"], cwd=track_src)
        lib_dst = os.path.join(root, "pyTRACK", "_lib")
        os.makedirs(lib_dst, exist_ok=True)
        for so_file in ["libtrack.so", "libtrackutils.so"]:
            shutil.copy(os.path.join(track_src, so_file), lib_dst)

    def build_extensions(self):
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
