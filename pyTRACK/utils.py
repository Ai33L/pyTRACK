import os
from netCDF4 import Dataset
from pathlib import Path
import subprocess
import xarray as xr

try:
    from cdo import *
    cdo = Cdo()
except Exception as e:
    cdo = None
    print("WARNING: CDO not available — CDO-dependent functionality will be disabled.")
    print("If on a conda env, conda install conda-forge::python-cdo to resolve this")

class data_indat(object):
    """Class to obtain basic information about the CMIP6/ERA input data."""
    def __init__(self, filename):
        """
        Reads the netCDF file and scans its variables.

        Parameters
        ----------


        filename : string
            Filename of a .nc file containing CMIP6 sea level pressure or wind
            velocity data.

        """
        self.filename = filename
        self.data = Dataset(filename, 'r')
        self.vars = [var for var in self.data.variables]

    def get_nx_ny(self):
        # returns number of latitudes and longitudes in the grid
        return str(len(self.data.variables['lon'][:])), \
                str(len(self.data.variables['lat'][:]))

    def get_grid_type(self):
        # returns the grid type
        return cdo.griddes(input=self.filename)[3]

    def get_variable_type(self):
        # returns the variable type
        return self.vars[-1]

    def get_timesteps(self):
        # returns the number of timesteps
        return int(len(self.data.variables['time'][:]))

    def has_equator(self):
        # check if the data has an equator
        if 0 in self.data.variables['lat'][:]:
            return True
        else:
            return False

    def has_nh_pole(self):
        # check if the data has an NH
        if 90 in self.data.variables['lat'][:]:
            return True
        else:
            return False

    def has_sh_pole(self):
        # check if the data has an NH
        if -90 in self.data.variables['lat'][:]:
            return True
        else:
            return False

def merge_uv(file1, file2, outfile,uname,vname):
    """
    Merge  U and V files into a UV file.

    Parameters
    ----------

    file1 : string
        Path to .nc file containing either U or V data

    file2 : string
        Path to .nc file containing either V or U data, opposite of file1

    outfile : string
        Path of desired output file


    """
    data1 = data_indat(file1)
    data2 = data_indat(file2)

    if data1.get_variable_type() == uname:
        u_file = file1
        v_file = file2

    elif data1.get_variable_type() == vname:
        u_file = file2
        v_file = file1

    else:
        raise Exception("Invalid input variable type. Please input ERA5 \
                            u or v file.")

    dir_path = os.path.dirname(file1)
    
    outfile = os.path.join(dir_path, os.path.basename(outfile))

    print("Merging u&v files")
    cdo.merge(input=" ".join((u_file, v_file)), output=outfile)
    print("Merged U and V files into UV file named: ", outfile)
        
    return outfile


def regrid(input, outfile):
    """
    Detect grid of input data and regrid to gaussian grid if necessary.

    Parameters
    ----------

    input : string
        Path to .nc file containing input data

    outfile : string
        Desired path of regridded file

    """
    data = data_indat(input)

    gridtype = data.get_grid_type()

    # check if regridding is needed, do nothing if already gaussian
    if gridtype == 'gridtype  = gaussian':
        print("No regridding needed.")

    # check for resolution and regrid
    else:
        nx, ny = data.get_nx_ny()
        if int(ny) <= 80:
            cdo.remapcon("n32", input=input, output=outfile)
            grid = 'n32'
        elif int(ny) <= 112:
            cdo.remapcon("n48", input=input, output=outfile)
            grid = 'n48'
        elif int(ny) <= 150:
            cdo.remapcon("n64", input=input, output=outfile)
            grid = 'n64'
        else:
            cdo.remapcon("n80", input=input, output=outfile)
            grid = 'n80'
        print("Regridded to " + grid + " Gaussian grid.")

    return

def run_silent(func, *args, **kwargs):
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()

    old_stdout = os.dup(1)
    old_stderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)

    os.dup2(devnull, 1)
    os.dup2(devnull, 2)

    try:
        return func(*args, **kwargs)
    finally:
        os.dup2(old_stdout, 1)
        os.dup2(old_stderr, 2)
        os.close(devnull)