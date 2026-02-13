Feature tracking
================

.. autofunction:: pyTRACK.track_uv

The track_uv function currently requires a particular file format. Here is a code snippet on python that 
demonstrate how you can meet most of these.

.. code-block:: bash

    dat=xr.open_dataset(f)
    dat=dat.transpose("time", "plev", "lat", "lon") # Ensures that the order is correct, skip plev if only lat-lon
    dat.lon.attrs["units"]="degrees_east"; dat.lat.attrs["units"]="degrees_north" # needs these units
    dat=dat[['U', 'V']].rename_vars({'U':'ua', 'V':'va'})#.drop_vars(['plev']) # should be names ua and va
    dat=dat.sel(plev=85000) # skip if only lat-lon
    dat.to_netcdf('', unlimited_dims={'time'})

.. autofunction:: pyTRACK.track_splice