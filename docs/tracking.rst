Feature tracking
================

.. autofunction:: pyTRACK.track_uv

The track_uv function currently requires a particular infile file format. Below is a code snippet on python that 
demonstrates how you can meet most of these.

.. code-block:: bash

    dat=xr.open_dataset(f)
    dat=dat.transpose("time", "plev", "lat", "lon") # Ensures that the order is correct, skip plev if only lat-lon
    dat.lon.attrs["units"]="degrees_east"; dat.lat.attrs["units"]="degrees_north" # needs these units
    dat=dat[['U', 'V']].rename_vars({'U':'ua', 'V':'va'})#.drop_vars(['plev']) # should be names ua and va
    dat=dat.sel(plev=85000) # skip if only lat-lon
    dat.to_netcdf('', unlimited_dims={'time'})

.. note::

   The sdate argument should be passed with care if you decide to split years. IF ysplit is true, then sdate relies on first 
   date_time being the same every year. Hence, it's a useful feature if you want to track JJA cyclones across years - input data 
   for JJA and pass ysplit=True and sdate='060100'. To track DJF (Or any other time period that is cross-year), input data 
   shifted such that seasons are in the same year and pass ysplit=True and sdate='110100'. This also assumes a Gregorian calendar, 
   so be mindful of the differences if the data is on a different calendar like noleap for instance.

The track_uv() function creates folders named {hemisphere}_y{year} in the outdirectory. Inside each of these folder, many files 
are written. For vorticity, both positive and negative anomalies are tracked. Cyclones are associated with positive anomalies in the
Northern Hemisphere and negative anomalies in the Southern Hemisphere. The \*pos files are associated with positive vorticity
and the \*neg files are associated with negative vorticities. The tr\* files contain all tracks and the ff\* files contain
only filtered tracks that last longer than 48 hours and travel at least 1000 km. The \*.nc files are netCDF files with or without 
Gregorian date_time (depending on if sdate was passed) and the other files are ASCII files with the same data.

The track_uv() function outputs 

.. autofunction:: pyTRACK.track_splice