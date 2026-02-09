import shutil
import os
from math import ceil
from .track import track
from .utils import data_indat, regrid

try:
    from cdo import *
    cdo = Cdo()
except Exception as e:
    cdo = None
    print("WARNING: CDO not available — CDO-dependent functionality will be disabled.")

__all__ = ['track_uv', 'calc_vorticity']

def calc_vorticity(uv_file, outfile='vorticity_out.dat'):

    # gather information about data
    year = cdo.showyear(input=uv_file)[0]
    uv = data_indat(uv_file)
    nx, ny = uv.get_nx_ny()
    u_name = uv.vars[-2]
    v_name = uv.vars[-1]

    indat=os.path.join(os.path.dirname(__file__), "indat", "calcvor_onelev.in")
    curr = os.getcwd()

    print(indat, curr)

    # generate input file and calculate vorticity using TRACK
    os.system(
    'sed -e "s/VAR1/{u}/;s/VAR2/{v}/;s/NX/{nx}/;s/NY/{ny}/;s/LEV/85000/;s/VORFILE/{out}/" {indat} > {curr}/calcvor_onelev_spec.in'
    .format(u=u_name, v=v_name, nx=nx, ny=ny, out=outfile, indat=indat, curr=curr))
    track(input_file=uv_file, namelist='calcvor_onelev_spec.in')
    

def track_uv(infile, outdirectory, NH=True, ysplit=False):

    # set outdir -- full path the output track directory
    outdir = os.path.abspath(os.path.expanduser(outdirectory))
    print(outdir)

    # read data charactheristics
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

    ################## END OF PROCESSING ####################################################################

    # Years
    years = cdo.showyear(input=infile_e)[0].split()
    print("Years: ", years)

    if not ysplit:
        years = ["all"]

    if NH == True:
        hemisphere = "NH"
    else:
        hemisphere = "SH"

    # do tracking for one year at a time
    
    for year in years:
        print("Running TRACK for year: " + year + "...")

        # select year from data
        if ysplit:
            print("Splitting: " + year)
            year_file = infile_e[:-3] + "_" + year + ".nc"
            cdo.selyear(year, input=infile_e, output=year_file)
        else:
            year_file=infile_e

        # directory containing year specific track output
        c_input = hemisphere + "_" + year 

        # get number of timesteps and number of chunks for tracking
        data = data_indat(year_file)
        ntime = data.get_timesteps()
        nchunks = ceil(ntime/62)

        # calculate vorticity from UV
        vor850_name = "vor850y"+year+".dat"
        calc_vorticity(year_file, outfile=vor850_name)

        fname = "T42filt_" + vor850_name
        indat=os.path.join(os.path.dirname(__file__), "indat", "specfilt.in")
        os.system(
        'sed -e "s/NX/{nx}/;s/NY/{ny}/;s/TRUNC/42/" {indat} > spec_T42_nx{nx}_ny{ny}.in'
        .format(nx=nx, ny=ny, indat=indat)
        )
        track(input_file=vor850_name, namelist=outdir+"/spec_T42_nx" + nx + "_ny" + ny + ".in")
        os.system("mv "+ outdir+"/specfil_band001.year_band001 " + fname)
        

        print(ntime)
        
        # line_4 = "master -c=" + c_input + " -e=track.linux -d=now -i=" + \
        #     fname + " -f=y" + year + \
        #     " -j=RUN_AT.in -k=initial.T42_" + hemisphere + \
        #     " -n=1,62," + \
        #     str(nchunks) + " -o='" + outdir + \
        #     "' -r=RUN_AT_ -s=RUNDATIN.VOR"

    #     # executing the lines to run TRACK
    #     print("Spectral filtering...")
    #     # os.system(line_1)
    #     # os.system(line_2)
    #     # os.system(line_3)

    #     # print("Running TRACK...")
    #     # os.system(line_4)

    #     print("Turning track output to netCDF...")

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

    #     ### cleanup fortran files ###########################

    #     if True: ## Change to false to keep files for debugging
    #         os.system("rm outdat/specfil*")
    #         os.system("rm outdat/ff_trs*")
    #         os.system("rm outdat/tr_trs*")
    #         os.system("rm outdat/interp_*")
    #         os.system("rm indat/"+year_file)
    #         os.system("rm indat/"+fname)
    #         os.system("rm indat/"+vor850_name)
    #     # os.system("rm indat/calcvor_onelev_" + ext + ".in")
    
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

