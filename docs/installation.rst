Installation
============

If you're on a Linux-based system, run the following to install pyTRACK (Best to use a conda environment with Python>=3.9)

.. code-block:: bash

    pip install track-pylib

If that doesn't work, git clone the stable branch of this repository and pip install from the base directory.

.. code-block:: bash

    git clone -b stable https://github.com/Ai33L/pyTRACK.git
    cd pyTRACK
    pip install -e .

The latest tested version of the code is contained in the 'stable' branch, while the 'main' branch
is used for active development.

Then from a Python terminal anywhere, run

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

    conda install conda-forge::python-cdo

when prompted.