Installation
============

To install pyTRACK, run the following (requires Python>=3.9)

.. code-block:: bash

    pip install track-pylib

Alternatively, you can also clone this repository and install pyTRACK from it's base folder with

.. code-block:: bash

    pip install -e .

The latest tested version of the code is contained in the 'stable' branch, while the 'main' branch
is used for active development.

Then from a Python terminal anywhhere, run

.. code-block:: bash

    from pyTRACK import *
    track()

If you see the TRACK namelist open up (possibly complaining that input.nc is not found),
then pyTRACK has been installed correctly! This should behave in the exact same way as TRACK,
with the only difference being the input and output directories are set to be the current working 
directory, instead of the usual TRACK-relative paths.

Running track() should work without any additional packages. However, some other pyTRACK functionalities 
depend on having cdo and nco installed on the system. You will be prompted to install these as and when 
you need them. For the cdo functionality specifically, it's best to work on a conda environment and run

.. code-block:: bash

    conda install python-cdo

when prompted.