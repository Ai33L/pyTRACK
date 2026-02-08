import os
import shutil
import subprocess
from pathlib import Path
from pyTRACK import track  # your Python track() wrapper
from math import ceil

# ------------------------------
# Configuration (replace as needed)
# ------------------------------

EXEC_EXIST=True
DATIN = "/home/requiem_at_home/dev/save/T42filt_vor850yall.dat"
INITIAL = "/home/requiem_at_home/dev/save/initial.T42_NH"
EXT="666"

ST = 1
FN = 62
BACK = 2
FOREWARD = 3
TERMFR = -1

NN = 1
EE = ceil(150/FN)

RUNDT = "RUNDATIN.VOR"
RUNOUT = "RUNDATOUT"

SRCDIR = Path('/home/requiem_at_home/dev/curr/pyTRACK/pyTRACK')
RDAT = SRCDIR / "indat"
ODAT = Path('/home/requiem_at_home/dev/save')
DIR2 = ODAT / "outputd"

DIR2.mkdir(exist_ok=True)


# ------------------------------
# Helper for sed-like replacements
# ------------------------------

import re
from pathlib import Path

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
    max_dir = DIR2 / f"DJF_MAX_{N}"
    min_dir = DIR2 / f"DJF_MIN_{N}"
    max_dir.mkdir(parents=True, exist_ok=True)
    min_dir.mkdir(parents=True, exist_ok=True)

    # --- Run TRACK for +ve field ---
    if EXEC_EXIST:
        print('starting', N, S, F)
        track(input_file=DATIN, namelist=fileA)
    else:
        track(input_file=str(fileA), namelist=None)


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
    if EXEC_EXIST:
        print('starting - ', N)
        track(input_file=DATIN, namelist=fileB)
    else:
        track(input_file=str(fileB), namelist=None)

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

shutil.move("initialyear", DIR2 / "initial")

# ------------------------------
# Splice mode
# ------------------------------

import re
from pathlib import Path

def run_splice(splice_file, out_prefix):
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
    text = text.replace("initial", str(DIR2 / "initial"))
    text = re.sub(r"^[0-9]+!", str(E), text, flags=re.MULTILINE)

    rsplice.write_text(text)

    temp_file.unlink()
    splice_file.unlink()

    # Run track in splice mode
    if EXEC_EXIST:
        track(input_file=DATIN, namelist=rsplice)
    else:
        track(input_file=str(rsplice), namelist=None)

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

            dst = DIR2 / f"{base}_{out_prefix}{ext}"
            shutil.move(str(src), str(dst))
    shutil.move(str(rsplice), DIR2 / f"RSPLICE_{out_prefix}")


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
        shutil.move(str(src), DIR2 / fname)

# Compress output directory
shutil.make_archive(str(DIR2), 'gztar', root_dir=str(DIR2))
