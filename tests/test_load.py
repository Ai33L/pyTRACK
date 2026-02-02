import os
import ctypes
import pytest

def test_track_function_loads():
    lib_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "pyTRACK", "_lib", "libtrack.so")
    )
    assert os.path.exists(lib_path), f"{lib_path} not found"

    lib = ctypes.CDLL(lib_path)
    assert hasattr(lib, "track"), "track() function not found"
