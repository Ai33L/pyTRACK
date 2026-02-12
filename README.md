### pyTRACK

[TRACK](https://gitlab.act.reading.ac.uk/track/track) is a powerful storm tracking software package that automatically identifies and tracks storm features in model and observational data. pyTRACK is intended to be an implementation of TRACK on Python that ports over most features of TRACK, while being easy to install and use.

To install pyTRACK, simply run (Best to use a conda environment with Python>=3.9)

```
pip install track-pylib
```

Alternatively, you can also git clone this repository and from its base folder run

```
pip install -e .
```

The 'stable' branch contains the latest tested code, and the 'main' branch is used actively for development.

Then from a Python terminal anywhhere, run

```
from pyTRACK import *
track()
```

This should start the TRACK namelist and should behave exactly like if you ran bin/track.linux from the compiled TRACK folder. The input and output files are assumed to be at the current working directory.

Running track() should work without any additional packages. However, some other pyTRACK functionalities depend on having cdo and nco installed on the system. You will be prompted to install these as and when you need them. For the cdo functionality specifically, it's best to work on a conda environment and run
```
conda install python-cdo
```
when prompted.

pyTRACK also supports some pre-set workflows, and is under active development. To see a list of workflows currently available, and for a more extensive documentation, check out [here.](https://track-pylib.readthedocs.io/en/latest/)