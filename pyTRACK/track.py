def set_track_env():
    import os

    pkgpath=os.path.dirname(__file__)
    curr=os.getcwd()
    os.environ["DATCM"] = pkgpath
    os.environ["SPECTRAL"] = os.path.join(curr, "specfilt") 
    os.environ["FINIT"] = os.path.join(curr, "month.nc") 

def track(input_file="input.nc", namelist=None):
    """
    Run TRACK.

    Parameters
    ----------
    input_file : str
        Name of the input file (passed with -i).
    namelist : str or None
        Path to the namelist file to feed to stdin.
        If None, runs TRACK normally without stdin redirection.
    """

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

    pkgpath = os.path.dirname(__file__)

    args = [
        b"track",
        b"-i", input_file.encode("utf-8"),
        b"-f", b"year",
    ]

    argc = len(args)
    argv = (ctypes.c_char_p * argc)(*args)

    set_track_env()

    if namelist is not None:
        # If a namelist is provided, redirect stdin
        if not os.path.exists(namelist):
            raise FileNotFoundError(f"Namelist not found: {namelist}")

        import os
        old_stdin_fd = os.dup(0)
        try:
            with open(namelist, "rb") as f:
                os.dup2(f.fileno(), 0)  # redirect stdin
                lib.track_main(argc, argv)
        finally:
            os.dup2(old_stdin_fd, 0)  # restore stdin
            os.close(old_stdin_fd)
    else:
        # No namelist, call normally
        lib.track_main(argc, argv)
