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
             trunc: Literal['42', '63'] = '42',
             keep_all_files: bool = False,):
    """
    Workflow to track features on 850hPa u-v wind data. Tracks both cyclones and anticyclones.

    Parameters
    ----------
    infile : str
        Name of the input file.
    """

    # copy infile to output directory and change directory
    infile = os.path.abspath(os.path.expanduser(infile))

    if outdirectory is None:
        outdir = os.getcwd()
    else:
        outdir = os.path.abspath(os.path.expanduser(outdirectory))
        os.makedirs(outdir, exist_ok=True)

    dest_file = os.path.join(outdir, os.path.basename(infile))

    if os.path.abspath(infile) != os.path.abspath(dest_file):
        shutil.copy2(infile, dest_file)

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
    if not keep_all_files:
        os.remove(infile) # keep_all_files?

    # Years
    years = cdo.showyear(input=infile_e)[0].split()
    print("Years: ", years)

    if not ysplit:
        years = ["all"]

    # do tracking for one year at a time
    
    for year in years:
        print("Running TRACK for year: " + year + "...")
        ext=hemisphere+'_y'+year

        # select year from data
        if ysplit:
            print("Splitting: " + year)
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

    #     ### extract start date and time from data file
    #     filename="indat/"+year_file
    #     sdate = subprocess.check_output(f"cdo showdate {filename} | head -n 1 | awk '{{print $1}}'", shell=True)
    #     sdate = sdate.decode('utf-8').strip()
    #     stime1 = subprocess.check_output(f"cdo showtime {filename} | head -n 1 | awk '{{print $1}}'", shell=True)
    #     stime1 = stime1.decode('utf-8').strip()
        
    #     # hotfix for start year before 1979
    #     if sdate[0]=='0':
    #         sdate='2'+sdate[1:]
        
    #     # convert initial date to string for util/count, in format YYYYMMDDHH
    #     timestring=sdate[0:4]+sdate[5:7]+sdate[8:10]+stime1[0:2]
    #     datetime=sdate[0:4]+'-'+sdate[5:7]+'-'+sdate[8:10]+' '+stime1[0:2]
    #     timedelta=6

    #     if shift:
    #         sdate=str(int(sdate[0:4])-1)+'-11-'+sdate[8:10]
    #         print('shifted start date :', sdate)
    #         timestring=sdate[0:4]+sdate[5:7]+sdate[8:10]+stime1[0:2]
    #         datetime=sdate[0:4]+'-'+sdate[5:7]+'-'+sdate[8:10]+' '+stime1[0:2]

    #     # tr2nc - turn tracks into netCDF files
    #     os.system("gunzip '" + outdir + "'/" + c_input + "/ff_trs_*")
    #     os.system("gunzip '" + outdir + "'/" + c_input + "/tr_trs_*")
    #     tr2nc_vor(outdir + "/" + c_input + "/ff_trs_pos", timestring, datetime, timedelta)
    #     tr2nc_vor(outdir + "/" + c_input + "/ff_trs_neg", timestring, datetime, timedelta)
    #     tr2nc_vor(outdir + "/" + c_input + "/tr_trs_pos", timestring, datetime, timedelta)
    #     tr2nc_vor(outdir + "/" + c_input + "/tr_trs_neg", timestring, datetime, timedelta)

    
    return

# def tr2nc_vor(input, timestring, datetime, timedelta):
#     """
#     Convert vorticity tracks from ASCII to NetCDF using TR2NC utility

#     Parameters
#     ----------

#     input : string
#         Path to ASCII file containing tracks

#     """

#     ## ASh -- to get the right date range, modify the tr2nc.meta.elinor file with the right details 
    
#     fullpath = os.path.abspath(input)
#     cwd = os.getcwd()
#     os.chdir(str(Path.home()) + "/TRACK/utils/TR2NC")
#     os.system("sed -e \"s/START/"+ str(timestring) + "/;s/DATE_TIME/" + str(datetime) + "/;s/STEP/" + str(timedelta) + "/\" tr2nc.meta.elinor > tr2nc.meta.elinor_mod")
#     os.chdir(str(Path.home()) + "/TRACK/utils/bin")
#     os.system("tr2nc '" + fullpath + "' s ../TR2NC/tr2nc.meta.elinor_mod")
#     os.chdir(cwd)
#     return

