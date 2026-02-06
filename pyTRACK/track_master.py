import os
import shutil
import subprocess
from pathlib import Path
from track_wrapper import track  # your Python track() wrapper

# ------------------------------
# Configuration (replace as needed)
# ------------------------------

EXEC_EXIST = True  # True corresponds to original script
EXT = "ext"
DATIN = "datin"
INITIAL = "!INITIAL!"

ST = 1
FN = 21
BACK = 2
FOREWARD = 3
TERMFR = -1

NN = 1
EE = 12

RUNDT = "RUNDATIN"
RUNOUT = "RUNDATOUT"

SRCDIR = Path.cwd()
EXECDIR = SRCDIR / "bin"
RDAT = SRCDIR / "indat"
ODAT = SRCDIR / "outdat"
DIR2 = SRCDIR / "outputd"
DFIL = "ioputd"
DIR3 = DIR2 / DFIL

DIR2.mkdir(exist_ok=True)
DIR3.mkdir(parents=True, exist_ok=True)

# ------------------------------
# Helper for sed-like replacements
# ------------------------------

def replace_namelist(template_file, S, F, initial=INITIAL, first_run=True):
    """ Mimics the sed commands from the csh script """
    out_lines = []
    with open(template_file) as f:
        for line in f:
            line_new = line
            line_new = line_new.replace("%INITIAL%", initial)
            if first_run:
                line_new = line_new.replace("#", str(S), 1).replace("!", str(F), 1)
                line_new = line_new.replace("i%", "i")
                line_new = line_new.replace("n~", "n")
            else:
                line_new = line_new.replace("#", str(S), 1).replace("!", str(F), 1)
                line_new = line_new.replace("i%", "y")
                if line_new.startswith("n~"):
                    continue  # delete line starting with n~
            out_lines.append(line_new)
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
    fileB.write_text(replace_namelist(templateB, S, F, INITIAL, first_run))

    # --- Create output directories ---
    max_dir = DIR3 / f"DJF_MAX_{N}"
    min_dir = DIR3 / f"DJF_MIN_{N}"
    max_dir.mkdir(parents=True, exist_ok=True)
    min_dir.mkdir(parents=True, exist_ok=True)

    # --- Run TRACK for +ve field ---
    if EXEC_EXIST:
        track(input_file=DATIN + "/" + EXT, namelist=fileA)
    else:
        track(input_file=str(fileA), namelist=None)

    # Move output files to DJF_MAX
    for fname in [f"{RUNDT}", "objout.new", "tdump", "idump"]:
        src = ODAT / (fname if fname != RUNDT else f"{RUNDT}")
        dst = max_dir / fname
        if src.exists():
            shutil.move(str(src), str(dst))
    
    # --- Run TRACK for -ve field ---
    if EXEC_EXIST:
        track(input_file=DATIN + "/" + EXT, namelist=fileB)
    else:
        track(input_file=str(fileB), namelist=None)

    # Move output files to DJF_MIN
    for fname in [f"{RUNDT}", "objout.new", "tdump", "idump"]:
        src = ODAT / (fname if fname != RUNDT else f"{RUNDT}")
        dst = min_dir / fname
        if src.exists():
            shutil.move(str(src), str(dst))

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

# ------------------------------
# Splice mode
# ------------------------------

def run_splice(splice_file, out_prefix):
    temp_file = ODAT / "RSPLICE.temp.ext"
    RSPLICE = ODAT / "RSPLICE.ext"

    # Read splice template
    with open(RDAT / "RSPLICE.in") as f_in, open(temp_file, "w") as f_temp:
        for line in f_in:
            if "!" in line:
                with open(splice_file) as sf:
                    f_temp.write(sf.read())
            f_temp.write(line)

    # Replace initial and end frame
    text = temp_file.read_text()
    text = text.replace("initial", str(DIR3 / "initial"))
    text = text.replace("!", str(E))
    RSPLICE.write_text(text)
    temp_file.unlink()
    splice_file.unlink()

    # Run track in splice mode
    if EXEC_EXIST:
        track(input_file=DATIN + "/" + EXT, namelist=RSPLICE)
    else:
        track(input_file=str(RSPLICE), namelist=None)

    # Move outputs
    for suffix in ["tr_trs", "tr_grid", "ff_trs"]:
        src = ODAT / f"{suffix}.{EXT}"
        dst = DIR3 / f"{suffix}_{out_prefix}"
        if src.exists():
            shutil.move(str(src), str(dst))
    shutil.move(str(RSPLICE), DIR3 / f"RSPLICE_{out_prefix}")

# Run splice for positive and negative
run_splice(ODAT / f"splice_max.{EXT}", "pos")
run_splice(ODAT / f"splice_min.{EXT}", "neg")

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
