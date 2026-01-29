import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pyTRACK

def test_lib_load():
    lib_path = os.path.join(os.path.dirname(pyTRACK.__file__), "_lib", "libtrack.so")
    assert os.path.exists(lib_path), "libtrack.so not found"
    lib = ctypes.CDLL(lib_path)
    assert hasattr(lib, "track_main"), "track_main symbol not found"
