import os
import ctypes
import pytest

@pytest.mark.parametrize("lib_name,function_name", [
    ("libtrack.so", "track_main"),
])
def test_track_function_runs(lib_name, function_name):
    """
    Load the specified shared library from pyTRACK/_lib and
    ensure that the function can be called without raising an exception.
    """
    # build absolute path to the shared library
    lib_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "pyTRACK", "_lib", lib_name)
    )
    assert os.path.exists(lib_path), f"{lib_name} not found at {lib_path}"

    # load the library
    lib = ctypes.CDLL(lib_path)

    # retrieve the function
    try:
        func = getattr(lib, function_name)
    except AttributeError:
        pytest.fail(f"{function_name} not found in {lib_name}")

    # set function signature: void track(void)
    func.restype = None
    func.argtypes = []

    # call function; test fails if an exception occurs
    try:
        func()
    except Exception as e:
        pytest.fail(f"{function_name} raised an exception: {e}")
