
def track(input_file="input.nc", ext='_ext', namelist=None):
    """
    Runs TRACK.

    Parameters
    ----------
    input_file : str
        Name of the input file.
    ext : str
        Extension to append to the TRACK output files.
    namelist : str or None
        The namelist file to be fed to track.
        This file should have track inputs in the right order in seperate lines.

    Equivalent to bin/track.linux -i {input_file} -f {ext} < namelist
    If no parameters are passed, then the usual TRACK namelist interface is triggered.
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

    args = [
        b"track",
        b"-i", input_file.encode("utf-8"),
        b"-f", ext.encode("utf-8")
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
    """
    Automatically called in the track() function.
    Sets and passes various paths required by TRACK.

    These paths are set and passed onto the previously pre-set paths in the
    src/TRACK-1.5.2/include/*.in files.

    The input and output paths are set below to the current working directory
    The input files needed are set to the correct location with respect to the package location
    Change the paths below if you would like to modify this behaviour
    """

    import os

    pkgpath=os.path.dirname(__file__) #location of the final package
    curr=os.getcwd() #current working directory

    ## paths - file_path.in
    os.environ["PATHI"] = curr #folder of input files
    os.environ["PATHO"] = curr #folder of output files
    os.environ["DATPATH"] = os.path.join(pkgpath, "data") #location of the data files
    os.environ["SPPATH"] = curr #location to save spectral files

    ## input files - files_in.in
    os.environ["DATIN"] = os.path.join(curr, "input.nc") #input file
    os.environ["DTIMAVG"] = os.path.join(curr, "TIME_AVG") #input file for time-avg data, does not pass correctly!
    os.environ["FRTIMES"] = os.path.join(curr, "times") #frame times
    os.environ["DATCM"] = os.path.join(pkgpath, "data", "CMAP.dat.claire") #country map data
    os.environ["DATZN"] = os.path.join(pkgpath, "data", "zone.dat") #input zonal dmax
    os.environ["DATAD"] = os.path.join(pkgpath, "data", "adapt.dat") #input adaptive phimax

    ## out files - include/files_out.in
    os.environ["FINIT"] = os.path.join(curr, "initial") #initialization file
    os.environ["DATTHRO"] = os.path.join(curr, "throut") #output file for thresholded data
    os.environ["DOUTOBJ"] = os.path.join(curr, "objout") #output files for points which constitute objects
    os.environ["COMOBJ"] = os.path.join(curr, "comb_obj") 
    os.environ["NEWOBJF"] = os.path.join(curr, "objout.new") #object data output file after feature point filtering 
    os.environ["TDUMP"] = os.path.join(curr, "tdump") #output file for final track data
    os.environ["IDUMP"] = os.path.join(curr, "idump") #output file for initial track data
    os.environ["TAVGE"] = os.path.join(curr, "user_tavg") #time average file
    os.environ["TENDENCY"] = os.path.join(curr, "field_tend") #tendency file
    os.environ["SPECTRAL"] = os.path.join(curr, "specfil") #spectraly filtered fields output stub filename
    os.environ["LANCZOS_RESP"] = os.path.join(curr, "lanczos_resp") #spectral response for Lanczos filtering
    os.environ["LANCZOS_W"] = os.path.join(curr, "lanczos_w") #Lanczos weights
    os.environ["TIME_FILT"] = os.path.join(curr, "filt_time") #time domain filtered fields output stub filename
    os.environ["CONVERT"] = os.path.join(curr, "conv_bin") #data conversion output filename stub 
    os.environ["EXTRACT"] = os.path.join(curr, "extract") #data extraction output filename stub
    os.environ["SMOOTH"] = os.path.join(curr, "smooth") #data smoothing output filename stub
    os.environ["MASK"] = os.path.join(curr, "mask") #data masking output filename stub
    os.environ["INTERP_TH"] = os.path.join(curr, "interp_th") #data output from threshold on current projection

    ## stat out files
    os.environ["FPTTRS"] = os.path.join(curr, "tr_trs") #spliced output file for track data
    os.environ["FILTRS"] = os.path.join(curr, "ff_trs") #filtered spliced track file
    os.environ["GRTRS"] = os.path.join(curr, "tr_grid") #grid point track data
    os.environ["MNTRS"] = os.path.join(curr, "mean_trs") #mean tracks output file
    os.environ["PHTRS"] = os.path.join(curr, "phase_trs") #phase speed output file
    os.environ["STATTRS"] = os.path.join(curr, "stat_trs") #statistics output file
    os.environ["STATTRS_SCL"] = os.path.join(curr, "stat_trs_scl") #scaled statistics output file
    os.environ["STATCOM"] = os.path.join(curr, "stat_com") #combined statistics output file
    os.environ["INITTRS"] = os.path.join(curr, "init_trs") #initiation output file 
    os.environ["DISPTRS"] = os.path.join(curr, "disp_trs") #disapearance output file

    ## extras 
    # - lib/include/constraint.h
    os.environ["CONSDAT"] = os.path.join(pkgpath, "data", "constraints.dat") 
    os.environ["CONSDAT_SMOOPY"] = os.path.join(pkgpath, "data", "constraints.dat.reg") 
    os.environ["CONSDAT_SPHERY"] = os.path.join(pkgpath, "data", "constraints.dat.sphery")


def track_splice(datin, ext, ntime):

    import shutil
    from pathlib import Path
    from math import ceil
    import re
    import os

    SRCDIR = Path(os.path.dirname(__file__))
    RDAT = SRCDIR / "indat"
    ODAT=Path(os.getcwd())
    DIR2 = ODAT / "output_track"
    DIR3 = DIR2 / ext

    DATIN = datin
    INITIAL = os.path.join(SRCDIR, 'data', 'initial.T42_'+ext[:2])
    EXT=ext

    ST = 1
    FN = 62
    BACK = 2
    FOREWARD = 3
    TERMFR = -1
    NN = 1

    RUNDT = "RUNDATIN.VOR"
    RUNOUT = "RUNDATOUT"

    # get number of timesteps and number of chunks for tracking
    EE = ceil(ntime/FN)

    DIR2.mkdir(exist_ok=True)
    DIR3.mkdir(exist_ok=True)

    def replace_namelist(template_file, S, F, initial, first_run=True, flag=False):
        """
        Mimics sed namelist replacements.
        
        If first_run=True: corresponds to N == 1 in csh script
        If flag=True: applies special replacement for _A.in files
        """
        out_lines = []

        with open(template_file) as f:
            for line in f:
                # Replace leading numbers + #
                if re.match(r"^[0-9]*#", line):
                    line = re.sub(r"^[0-9]*#", str(S), line)

                # Replace leading numbers + !
                if re.match(r"^[0-9]*!", line):
                    line = re.sub(r"^[0-9]*!", str(F), line)

                # First run (N==1)
                if first_run:
                    if line.lstrip().startswith("i%"):
                        line = re.sub(r"^i%", "i", line)
                    if line.lstrip().startswith("n~"):
                        line = re.sub(r"^n~", "n", line)
                # Special flag (_A.in)
                elif flag:
                    if line.lstrip().startswith("i%"):
                        line = re.sub(r"^i%", "y", line)
                    # Do NOT delete lines starting with n~ (unlike the normal else)
                # Normal else (N>1, not flag)
                else:
                    if line.lstrip().startswith("i%"):
                        line = re.sub(r"^i%", "y", line)
                    if line.lstrip().startswith("n~"):
                        continue  # delete this line

                # Replace %INITIAL% everywhere
                line = line.replace("%INITIAL%", initial)
                out_lines.append(line)

        return "".join(out_lines)



    # ------------------------------
    # Main loop
    # ------------------------------

    S = ST
    F = FN
    I = F - S

    N = NN
    E = EE
    QQ = 0

    while N <= E:

        # --- Prepare input files ---
        fileA = ODAT / f"{RUNDT}.{EXT}"
        fileB = ODAT / f"{RUNDT}_A.{EXT}"

        first_run = N == 1
        templateA = RDAT / f"{RUNDT}.in"
        templateB = RDAT / f"{RUNDT}_A.in"

        fileA.write_text(replace_namelist(templateA, S, F, INITIAL, first_run))

        # --- Create output directories ---
        max_dir = DIR3 / f"DJF_MAX_{N}"
        min_dir = DIR3 / f"DJF_MIN_{N}"
        max_dir.mkdir(parents=True, exist_ok=True)
        min_dir.mkdir(parents=True, exist_ok=True)

        # --- Run TRACK for +ve field ---
        print('starting', N, S, F)
        track(input_file=DATIN, ext=ext, namelist=fileA)


        # Move output files to DJF_MAX
        print('moving', N)
        file_list = [RUNDT, "objout.new", "objout", "tdump", "idump"]
        for fname in file_list:
            for src_file in ODAT.glob(f"{fname}*"):
                dst_file = max_dir / fname
                print(f"Moving {src_file} -> {dst_file}")
                shutil.move(str(src_file), str(dst_file))
        
        fileB.write_text(replace_namelist(templateB, S, F, INITIAL, first_run, flag=True))
        # --- Run TRACK for -ve field ---
        print('starting - ', N)
        track(input_file=DATIN, ext=ext, namelist=fileB)

        # Move output files to DJF_MIN
        print('moving - ', N)
        file_list = [RUNDT, "objout.new", "objout", "tdump", "idump"]
        for fname in file_list:
            for src_file in ODAT.glob(f"{fname}*"):
                dst_file = min_dir / fname
                print(f"Moving {src_file} -> {dst_file}")
                shutil.move(str(src_file), str(dst_file))

        # --- Prepare splice files ---
        splice_max = ODAT / f"splice_max.{EXT}"
        splice_min = ODAT / f"splice_min.{EXT}"
        mode = 1 if N == 1 else FOREWARD

        with open(splice_max, "a") as f:
            f.write(f"{max_dir}/objout.new\n{max_dir}/tdump\n{mode}\n")
        with open(splice_min, "a") as f:
            f.write(f"{min_dir}/objout.new\n{min_dir}/tdump\n{mode}\n")

        if QQ > 0:
            break

        # --- Update loop counters ---
        N += 1
        S = F - BACK
        F = F + I if N < E else F + I + 15

        if TERMFR > 0 and F > TERMFR:
            F = TERMFR
            E = N
            QQ = 1

    print('part 1 success!!')

    shutil.move("initial"+ext, DIR3 / "initial")

    # ------------------------------
    # Splice mode
    # ------------------------------

    def run_splice(splice_file, out_prefix, ext):
        temp_file = ODAT / f"RSPLICE.temp.{out_prefix}"
        rsplice = ODAT / f"RSPLICE.{out_prefix}"

        ODAT.mkdir(parents=True, exist_ok=True)

        marker_re = re.compile(r"^[0-9]+!")

        with open(RDAT / "RSPLICE.in", "r") as f_in, open(temp_file, "w") as f_temp:
            splice_text = splice_file.read_text()
            for line in f_in:
                f_temp.write(line)
                if marker_re.match(line):
                    f_temp.write(splice_text)

        text = temp_file.read_text()
        text = text.replace("initial", str(DIR3 / "initial"))
        text = re.sub(r"^[0-9]+!", str(E), text, flags=re.MULTILINE)

        rsplice.write_text(text)

        temp_file.unlink()
        splice_file.unlink()

        # Run track in splice mode
        track(input_file=DATIN, ext=ext, namelist=rsplice)

        # Move outputs

        prefixes = ["tr_trs", "tr_grid", "ff_trs"]
        for prefix in prefixes:
            for src in ODAT.glob(f"{prefix}*"):
                name = src.name

                # strip anything after the prefix, before optional .nc
                m = re.match(rf"({prefix})([^.]*)?(\.nc)?$", name)
                if not m:
                    continue
                base = m.group(1)          # tr_trs / ff_trs / tr_grid
                ext = m.group(3) or ""     # .nc or empty

                dst = DIR3 / f"{base}_{out_prefix}{ext}"
                shutil.move(str(src), str(dst))
        shutil.move(str(rsplice), DIR3 / f"RSPLICE_{out_prefix}")


    # Run splice for positive and negative
    run_splice(ODAT / f"splice_max.{EXT}", "pos", ext=ext)
    run_splice(ODAT / f"splice_min.{EXT}", "neg", ext=ext)

    # ------------------------------
    # Final cleanup
    # ------------------------------
    for f in ODAT.glob(f"{RUNDT}*.{EXT}"):
        f.unlink()
    for f in ["idump.ext", "throut.ext", "objout.ext", ".run_at.lock.ext"]:
        fp = ODAT / f
        if fp.exists():
            fp.unlink()

    # Move initial files
    for fname in ["initial.ext", "user_tavg.ext", "user_tavg.ext_var", "user_tavg.ext_varfil"]:
        src = ODAT / fname
        if src.exists():
            shutil.move(str(src), DIR3 / fname)

    # Compress output directory
    shutil.make_archive(str(DIR3), 'gztar', root_dir=str(DIR3))