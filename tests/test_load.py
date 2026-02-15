import os
import ctypes
import pyTRACK

def test_track_function_loads():
    # locate the shared lib relative to the installed package
    lib_dir = os.path.join(os.path.dirname(pyTRACK.__file__), "_lib")
    lib_path = os.path.join(lib_dir, "libtrack.so")

    assert os.path.exists(lib_path), f"{lib_path} not found"

    lib = ctypes.CDLL(lib_path)
    assert hasattr(lib, "track_main"), "track_main() function not found"