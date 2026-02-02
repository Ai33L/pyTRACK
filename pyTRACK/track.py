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


def track(input_file='input.nc'):
    # Compute absolute path to grid.nc in the data folder
    pkgpath = os.path.dirname(__file__)
    if not os.path.exists(pkgpath):
        raise FileNotFoundError(f"Input file not found: {pkgpath}")

    # Prepare arguments
    args = [
        b"track",
        b"-d", pkgpath.encode("utf-8"),
        b"-i", input_file.encode("utf-8"),  # convert to bytes for ctypes
        b"-f", b"year"   
    ]

    argc = len(args)
    argv = (ctypes.c_char_p * argc)(*args)

    # for i, a in enumerate(args):
    #     print(f" argv[{i}] =", a)

    lib.track_main(argc, argv)
