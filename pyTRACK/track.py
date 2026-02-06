
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


def set_track_env():
    import os

    pkgpath=os.path.dirname(__file__)
    curr=os.getcwd()

    ## paths
    os.environ["PATHI"] = curr
    os.environ["PATHO"] = curr
    os.environ["DATPATH"] = os.path.join(pkgpath, "data")
    os.environ["SPPATH"] = curr

    ## input files
    os.environ["DATIN"] = os.path.join(curr, "input.nc") 
    os.environ["DTIMAVG"] = os.path.join(curr, "TIME_AVG") ## does not pass correctly!
    os.environ["FRTIMES"] = os.path.join(curr, "times?") 
    os.environ["DATCM"] = os.path.join(pkgpath, "data", "CMAP.dat.claire")
    os.environ["DATZN"] = os.path.join(pkgpath, "data", "zone.dat") 
    os.environ["DATAD"] = os.path.join(pkgpath, "data", "adapt.dat") 

    ## out files
    os.environ["FINIT"] = os.path.join(curr, "initial") 
    os.environ["DATTHRO"] = os.path.join(curr, "throut") 
    os.environ["DOUTOBJ"] = os.path.join(curr, "objout") 
    os.environ["COMOBJ"] = os.path.join(curr, "comb_obj") 
    os.environ["NEWOBJF"] = os.path.join(curr, "objout.new") 
    os.environ["TDUMP"] = os.path.join(curr, "tdump") 
    os.environ["IDUMP"] = os.path.join(curr, "idump") 
    os.environ["TAVGE"] = os.path.join(curr, "user_tavg") 
    os.environ["TENDENCY"] = os.path.join(curr, "field_tend")
    os.environ["SPECTRAL"] = os.path.join(curr, "specfil") 
    os.environ["LANCZOS_RESP"] = os.path.join(curr, "lanczos_resp") 
    os.environ["LANCZOS_W"] = os.path.join(curr, "lanczos_w") 
    os.environ["TIME_FILT"] = os.path.join(curr, "filt_time")
    os.environ["CONVERT"] = os.path.join(curr, "conv_bin") 
    os.environ["EXTRACT"] = os.path.join(curr, "extract") 
    os.environ["SMOOTH"] = os.path.join(curr, "smooth")
    os.environ["MASK"] = os.path.join(curr, "mask") 
    os.environ["INTERP_TH"] = os.path.join(curr, "interp_th")

    ## stat out files
    os.environ["FPTTRS"] = os.path.join(curr, "tr_trs?") 
    os.environ["FILTRS"] = os.path.join(curr, "ff_trs?") 
    os.environ["GRTRS"] = os.path.join(curr, "tr_grid?") 
    os.environ["MNTRS"] = os.path.join(curr, "mean_trs?") 
    os.environ["PHTRS"] = os.path.join(curr, "phase_trs?")
    os.environ["STATTRS"] = os.path.join(curr, "stat_trs?")
    os.environ["STATTRS_SCL"] = os.path.join(curr, "stat_trs_scl?")
    os.environ["STATCOM"] = os.path.join(curr, "stat_com?") 
    os.environ["INITTRS"] = os.path.join(curr, "init_trs?") 
    os.environ["DISPTRS"] = os.path.join(curr, "disp_trs?")

    ## extras
    os.environ["CONSDAT"] = os.path.join(pkgpath, "data", "constraints.dat") 
    os.environ["CONSDAT_SMOOPY"] = os.path.join(pkgpath, "data", "constraints.dat.reg") 
    os.environ["CONSDAT_SPHERY"] = os.path.join(pkgpath, "data", "constraints.dat.sphery") 

