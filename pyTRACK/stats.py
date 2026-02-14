import shutil
import os
from typing import Literal
from math import ceil
from .track import track, track_splice
from .utils import data_indat, regrid, run_silent
from pathlib import Path

__all__ = ['stats_track']

def stats_track(outdirectory=None, keep_all_files=False):
    """
    Workflow to compute statistics from features tracked using track_uv().

    The statistics file are output inside the corresponding {hemisphere}_y{year} folder in the outdirectory.

    Parameters
    ----------
    outdirectory : str
        Path to the output directory, same as that passed to track_uv()
    keep_all_files : bool
        Do you want to keep all the intermediate files? Default is no.
        Turn this on if you want to retreive these files, or during development.
    """


    pkgpath=os.path.dirname(__file__)
    indat=os.path.join(pkgpath, "indat", "STATS_template_area.in")
    indat_def=os.path.join(pkgpath, "data", "gridT63.nc")

    if outdirectory is not None:
        os.chdir(outdirectory+'/output_track')
    else:
        os.chdir('output_track')
    
    dirs = [
    str(p.resolve())
    for p in Path(".").iterdir()
    if p.is_dir() and p.name.startswith(("NH", "SH"))
    ]

    for dir in dirs:
        os.chdir(dir)

        for file in ["ff_trs_pos", "ff_trs_neg"]:

            os.system('sed -e "s/FILE_NAME/{file}/" {indat} > {dir}/track_stats.in'
            .format(file=file, indat=indat, dir=dir))

            track(input_file=indat_def, namelist=dir+'/track_stats.in')
            os.system("mv "+ "stat_trs_scl_ext_1.nc stats_"+file+".nc")

            if not keep_all_files:
                os.remove('disp_trs_ext')
                os.remove('gstat1.dat')
                os.remove('init_trs_ext')
                os.remove('initial_ext')
                os.remove('phase_trs_ext')
                os.remove('stat_trs_ext')
                os.remove('stat_trs_ext_1.nc')
                os.remove('stat_trs_scl_ext')
                os.remove('track_stats.in')
                os.remove('ff_trs_ext')
                os.remove('ff_trs_ext.nc')






