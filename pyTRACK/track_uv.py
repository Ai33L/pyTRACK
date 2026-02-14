import shutil
import os
from typing import Literal
from math import ceil
from .track import track, track_splice
from .utils import data_indat, regrid, run_silent

try:
    from cdo import *
    cdo = Cdo()
except Exception as e:
    cdo = None

__all__ = ['track_uv', 'calc_vorticity']

def calc_vorticity(uv_file, outfile='vorticity_out.dat', ext='_ext'):

    # gather information about data
    year = cdo.showyear(input=uv_file)[0]
    uv = data_indat(uv_file)
    nx, ny = uv.get_nx_ny()
    u_name = uv.vars[-2]
    v_name = uv.vars[-1]

    indat=os.path.join(os.path.dirname(__file__), "indat", "calcvor_onelev.in")
    curr = os.getcwd()

    # generate input file and calculate vorticity using TRACK
    os.system(
    'sed -e "s/VAR1/{u}/;s/VAR2/{v}/;s/NX/{nx}/;s/NY/{ny}/;s/LEV/85000/;s/VORFILE/{out}/" {indat} > {curr}/calcvor_onelev_{ext}.in'
    .format(u=u_name, v=v_name, nx=nx, ny=ny, out=outfile, indat=indat, curr=curr, ext=ext))
    
    print("Computing vorticity and outputting to "+outfile)
    # track(input_file=uv_file, namelist=f'calcvor_onelev_{ext}.in', ext=ext)
    run_silent(track, input_file=uv_file, namelist=f'calcvor_onelev_{ext}.in', ext=ext)
    

def track_uv(infile,
             outdirectory=None,
             hemisphere: Literal['NH', 'SH'] = 'NH',
             ysplit: bool = False,
             sdate=None,
             trunc: Literal['42', '63'] = '42',
             keep_all_files: bool = False,):
    """
    Workflow to track features on 850hPa u-v wind data. Tracks both cyclones and anticyclones.
    
    First computes vortiticy from the input data and then truncates and spectrally filters out small wavenumbers.

    Tracks features on this data. Outputs to outdirectory in folders of {hemisphere}_y{year}.

    If sdate is passed, then rewrites the .nc files with date_time matching the passed sdate.

    Parameters
    ----------
    infile : str
        Name of the input file.
    outdirectory : str
        Path to the output directory, will be created if it does not already exist.
    ysplit : bool
        Should tracking be done for each year separately.
        Turn this on if you're tracking by season!
    sdate : str
        First time step in MMDDHH format.
        Start year is captured from the file directly, taking ysplit into consideration.
    trunc : str
        Spectral truncation required - defaults to T42.
        Note - setting T63 will take longer and track more cyclones!
    keep_all_files : bool
        Do you want to keep all the intermediate files? Default is no.
        Turn this on if you want to retreive these files, or during development.
    """

    # copy infile to output directory and change directory
    infile = os.path.abspath(os.path.expanduser(infile))
    infile_copied=False

    if outdirectory is None:
        outdir = os.getcwd()
    else:
        outdir = os.path.abspath(os.path.expanduser(outdirectory))
        os.makedirs(outdir, exist_ok=True)

    dest_file = os.path.join(outdir, os.path.basename(infile))

    if os.path.abspath(infile) != os.path.abspath(dest_file):
        shutil.copy2(infile, dest_file)
        infile_copied=True

    infile = dest_file
    os.chdir(outdir)

    # read data characteristics
    data = data_indat(infile)
    gridtype = data.get_grid_type()
    if ("va" not in data.vars) or ("ua" not in data.vars):
        raise Exception("Invalid input variable type. Please input eithe " +
                            "a combined uv file or both ua and va")
    
    print("Remove unnecessary variables.")
    
    infile_e = infile[:-3] + "_processed.nc"
    if "time_bnds" in data.vars:
        ncks = "time_bnds"
        if "lat_bnds" in data.vars:
            ncks += ",lat_bnds,lon_bnds"
        os.system("ncks -C -O -x -v " + ncks + " " + input + " " + infile_e)
    elif "lat_bnds" in data.vars:
        os.system("ncks -C -O -x -v lat_bnds,lon_bnds " + input + " " + infile_e)
    else:
        os.system("cp " + infile + " " + infile_e)

    # interpolate, if not gaussian
    infile_eg = infile_e[:-3] + "_gaussian.nc"
    if gridtype == 'gridtype  = gaussian':
        print("No regridding needed.")
    else:
    # regrid
        regrid(infile_e, infile_eg)
    os.system("mv " + infile_eg + " " + infile_e)

    # fill missing values, modified to be xarray for now - ASh
    infile_egf = infile_e[:-3] + "_filled.nc"

    os.system("cdo setmisstoc,0 " + infile_e +
              " " + infile_egf)
    
    # check if ncatted exists
    if shutil.which("ncatted") is None:
        raise RuntimeError("Error: 'ncatted' command not found. Please install NCO before running this script.")

    os.system("ncatted -a _FillValue,,d,, -a missing_value,,d,, " + infile_egf)
    os.system("mv " + infile_egf + " " + infile_e)
    
    # get final data info
    data = data_indat(infile_e)
    nx, ny = data.get_nx_ny()
    if (not keep_all_files) and infile_copied:
        os.remove(infile) # keep_all_files?

    # Years
    years = cdo.showyear(input=infile_e)[0].split()
    print("Years: ", years)

    if not ysplit:
        Y=years[0]
        years = ["all"]

    # do tracking for one year at a time
    
    for year in years:
        os.chdir(outdir)
        if ysplit:
            Y=year

        print("Running TRACK for year: " + year + "...")
        ext=hemisphere+'_y'+year

        # select year from data
        if ysplit:
            year_file = infile_e[:-3] + "_" + year + ".nc"
            cdo.selyear(year, input=infile_e, output=year_file)
        else:
            year_file=infile_e

        data = data_indat(year_file)
        ntime = data.get_timesteps()

        # calculate vorticity from UV
        vor850_name = "vor850_"+ext+".dat"
        calc_vorticity(year_file, outfile=vor850_name, ext=ext)
        if not keep_all_files:
            os.remove('calcvor_onelev_'+ext+'.in') # keep_all_files?
            os.remove('initial'+ext)
            if ysplit:
                os.remove(year_file)

        fname = "T"+trunc+"filt_" + vor850_name
        indat=os.path.join(os.path.dirname(__file__), "indat", "specfilt.in")
        os.system(
        'sed -e "s/NX/{nx}/;s/NY/{ny}/;s/TRUNC/{trunc}/" {indat} > spec_T{trunc}_nx{nx}_ny{ny}.in'
        .format(nx=nx, ny=ny, indat=indat, trunc=trunc)
        )
        print('T'+trunc+' truncation and filtering out small wavenumbers to output file '+fname)
        run_silent(track, input_file=vor850_name, ext=ext, namelist="spec_T"+trunc+"_nx" + nx + "_ny" + ny + ".in")
        os.system("mv "+ "specfil_band001."+ext+"_band001 " + fname)
        if not keep_all_files:
            os.remove("spec_T"+trunc+"_nx" + nx + "_ny" + ny + ".in") # keep_all_files?
            os.remove('initial'+ext)
            os.remove("specfil_band000."+ext+"_band000")
            os.remove(vor850_name)

        track_splice(fname, ext, ntime, trunc, keep_all_files=keep_all_files)
        if not keep_all_files:
            os.remove('interp_th'+ext) # keep_all_files?
            os.remove('initial'+ext)
            os.remove(fname)

        if sdate is not None:
            print('sdate passed - rewriting .nc files with Gregorian dates')
            os.chdir('output_track/'+ext)
            if len(Y)<4:
                YY=str(2000+int(Y))
                print('Year needs to be later than 1979 - shifting year to', YY)
            
            # convert initial date to string for util/count, in format YYYYMMDDHH
            datetime=YY+sdate[:2]+sdate[2:4]+sdate[4:6]
            datetime_exp=YY+'-'+sdate[:2]+'-'+sdate[2:4]+' '+sdate[4:6]
            timedelta=6

            for file in ["tr_trs_pos", "tr_trs_neg", "ff_trs_pos", "ff_trs_neg"]:
                print('Writing', file+'.nc')
                tr2nc_vor(file, datetime, datetime_exp, timedelta)
            os.remove('tr2nc.meta.elinor')

    return

def tr2nc_vor(input, datetime, datetime_exp, timedelta):
    """
    Function to rewrite .nc files with Gregorian date-time.
    """
    import os
    import ctypes

    curr=os.getcwd()
    pkgpath=os.path.dirname(__file__)
    indat=os.path.join(pkgpath, "indat", "tr2nc.meta.elinor")
    os.system(
    'sed -e "s/START/{datetime}/;s/STEP/{step}/;s/DATETIME/{datetime_exp}/" {indat} > {curr}/tr2nc.meta.elinor'
    .format(datetime=datetime, datetime_exp=datetime_exp, step=timedelta, indat=indat, curr=curr))

    _LIB = os.path.join(os.path.dirname(__file__), "_lib", "libtrackutils.so")

    if not os.path.exists(_LIB):
        raise FileNotFoundError(f"libtrackutils.so not found at {_LIB}")

    lib = ctypes.CDLL(_LIB)

    # Define function signature
    lib.tr2nc_main.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_char_p)
    ]
    lib.tr2nc_main.restype = ctypes.c_int

    args = [
        b"track",
        input.encode("utf-8"),
        b"s", (curr+'/tr2nc.meta.elinor').encode("utf-8")
    ]
    argc = len(args)
    argv = (ctypes.c_char_p * argc)(*args)

    lib.tr2nc_main(argc, argv)

    return
