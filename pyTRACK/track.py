import os
import ctypes

# Path to shared library
_LIB = os.path.join(os.path.dirname(__file__), "_lib", "libtrack.so")

if not os.path.exists(_LIB):
    raise FileNotFoundError(f"libtrack.so not found at {_LIB}")

lib = ctypes.CDLL(_LIB)

# Define function signature
lib.track_main.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p)
]
lib.track_main.restype = ctypes.c_int


def run_track(input_file: str, extension: str, namelist_file: str = None):
    """
    Simple wrapper for track_main.
    """
    args = [b"track", input_file.encode(), b"-f", extension.encode()]

    if namelist_file:
        args.append(namelist_file.encode())

    argc = len(args)
    argv = (ctypes.c_char_p * argc)(*args)

    return lib.track_main(argc, argv)
