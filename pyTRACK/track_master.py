"""
Python reimplementation of the TRACK DJF workflow originally written in csh.

Design principles:
- Never change working directory
- TRACK always writes to current working directory
- Python immediately moves outputs to structured folders
- All paths are explicit and configurable
"""

from pathlib import Path
import shutil
import re


# ---------------------------------------------------------------------
# USER CONFIGURATION
# ---------------------------------------------------------------------

EXT = "year"

# You will set these paths explicitly
SRCDIR = Path.cwd()
INDAT = SRCDIR / "indat"
OUTDAT = SRCDIR / "outdat"
OUTPUT = SRCDIR / "outputd" / "ioputd"

RUNDT = "RUNDATIN"
RUNOUT = "RUNDATOUT"

INPUT_FILE = "input.nc"
INITIAL = "!INITIAL!"

# Loop control (matches csh defaults)
NN = 1
EE = 12

ST = 1
FN = 21
BACK = 2
TERMFR = -1


# ---------------------------------------------------------------------
# TRACK WRAPPER (UNCHANGED LOGIC, CWD-BASED)
# ---------------------------------------------------------------------

def track(input_file="input.nc", namelist=None):
    import os
    import ctypes

    _LIB = Path(__file__).parent / "_lib" / "libtrack.so"
    if not _LIB.exists():
        raise FileNotFoundError(f"libtrack.so not found at {_LIB}")

    lib = ctypes.CDLL(str(_LIB))

    lib.track_main.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_char_p)
    ]
    lib.track_main.restype = ctypes.c_int

    args = [
        b"track",
        b"-d", str(Path.cwd()).encode(),
        b"-i", input_file.encode(),
        b"-f", EXT.encode(),
    ]

    argc = len(args)
    argv = (ctypes.c_char_p * argc)(*args)

    if namelist is not None:
        old_stdin_fd = os.dup(0)
        try:
            with open(namelist, "rb") as f:
                os.dup2(f.fileno(), 0)
                lib.track_main(argc, argv)
        finally:
            os.dup2(old_stdin_fd, 0)
            os.close(old_stdin_fd)
    else:
        lib.track_main(argc, argv)


# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------

TRACK_OUTPUTS = [
    "objout.new",
    "tdump",
    "idump",
    "objout",
    "throut",
]


def render_input(text, S, F, initial, i_flag="i", drop_n=False):
    text = re.sub(r"^[0-9]*#", str(S), text, flags=re.M)
    text = re.sub(r"^[0-9]*!", str(F), text, flags=re.M)
    text = text.replace("%INITIAL%", initial)

    if i_flag == "i":
        text = re.sub(r"^i%", "i", text, flags=re.M)
    else:
        text = re.sub(r"^i%", "y", text, flags=re.M)

    if drop_n:
        text = re.sub(r"^n~.*$", "", text, flags=re.M)
    else:
        text = re.sub(r"^n~", "n", text, flags=re.M)

    return text


def run_track(namelist_text, workdir):
    workdir.mkdir(parents=True, exist_ok=True)

    namelist = workdir / "namelist.in"
    namelist.write_text(namelist_text)

    track(input_file=INPUT_FILE, namelist=str(namelist))

    for name in TRACK_OUTPUTS:
        p = Path(f"{name}.{EXT}")
        if p.exists():
            shutil.move(p, workdir / name)


# ---------------------------------------------------------------------
# MAIN WORKFLOW
# ---------------------------------------------------------------------

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    template = (INDAT / f"{RUNDT}.in").read_text()
    template_a = (INDAT / f"{RUNDT}_A.in").read_text()

    splice_max = []
    splice_min = []

    S = ST
    F = FN
    I = F - S

    N = NN
    E = EE

    while N <= E:
        # ---------- MAX ----------
        max_dir = OUTPUT / f"DJF_MAX_{N}"

        max_input = render_input(
            template,
            S,
            F,
            INITIAL,
            i_flag="i" if N == 1 else "y",
            drop_n=(N != 1),
        )

        run_track(max_input, max_dir)

        splice_max.append((max_dir / "objout.new", max_dir / "tdump", 1 if N == 1 else 3))

        # ---------- MIN ----------
        min_dir = OUTPUT / f"DJF_MIN_{N}"

        min_input = render_input(
            template_a,
            S,
            F,
            INITIAL,
            i_flag="i",
            drop_n=False,
        )

        run_track(min_input, min_dir)

        splice_min.append((min_dir / "objout.new", min_dir / "tdump", 1 if N == 1 else 3))

        # ---------- LOOP CONTROL ----------
        N += 1
        S = F - BACK

        if N < E:
            F += I
        else:
            F += I + 15

        if TERMFR > 0 and F > TERMFR:
            F = TERMFR
            E = N
            break

    # -----------------------------------------------------------------
    # SPLICING
    # -----------------------------------------------------------------

    def write_splice(entries, path):
        with open(path, "w") as f:
            for o, t, flag in entries:
                f.write(f"{o}\n{t}\n{flag}\n")

    rs_template = (INDAT / "RSPLICE.in").read_text()

    for label, entries in [("pos", splice_max), ("neg", splice_min)]:
        splice_file = OUTDAT / f"splice_{label}.{EXT}"
        write_splice(entries, splice_file)

        text = rs_template
        text = re.sub(r"^[0-9]*!", str(len(entries)), text, flags=re.M)
        text = re.sub(r"^[0-9]*!", splice_file.read_text(), text, flags=re.M)
        text = text.replace("initial", str(OUTPUT / "initial"))

        rs_file = OUTDAT / f"RSPLICE_{label}.{EXT}"
        rs_file.write_text(text)

        track(input_file=INPUT_FILE, namelist=str(rs_file))

        for name in ["tr_trs", "tr_grid", "ff_trs"]:
            p = Path(f"{name}.{EXT}")
            if p.exists():
                shutil.move(p, OUTPUT / f"{name}_{label}")

    # -----------------------------------------------------------------
    # FINAL TIDY
    # -----------------------------------------------------------------

    for f in OUTDAT.glob(f"*.{EXT}"):
        f.unlink(missing_ok=True)

    for f in ["initial", "user_tavg", "user_tavg_var", "user_tavg_varfil"]:
        p = OUTDAT / f"{f}.{EXT}"
        if p.exists():
            shutil.move(p, OUTPUT / f)

    shutil.make_archive(str(OUTPUT), "gztar", root_dir=OUTPUT)


if __name__ == "__main__":
    main()
