### pyTRACK

[TRACK](https://gitlab.act.reading.ac.uk/track/track) [^1] [^2] [^3] [^4] is a powerful storm tracking software package that automatically identifies and tracks storm features in model and observational data. pyTRACK is intended to be an implementation of TRACK on Python that ports over most features of TRACK, while being easy to install and use.

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
conda install conda-forge::python-cdo
```
when prompted.

pyTRACK also supports some pre-set workflows, and is under active development. To see a list of workflows currently available, and for a more extensive documentation, check out [here.](https://track-pylib.readthedocs.io/en/latest/)


[^1]: Hodges, K.I.: A General Method for Tracking Analysis and Its Application to Meteorological Data. Monthly Weather Review 122(11), 2573–2586 (1994) https://doi.org/10.1175/1520-0493(1994)122%3C2573:AGMFTA%3E2.0.CO;2 . Chap.Monthly Weather Review

[^2]: Hodges, K.I.: Feature Tracking on the Unit Sphere. Monthly Weather Review 123(12), 3458–3465 (1995) https://doi.org/10.1175/1520-0493(1995)123%3C3458:FTOTUS%3E2.0.CO;2 . Chap. Monthly Weather Review

[^3]: Hodges, K.I.: Spherical Nonparametric Estimators Applied to the UGAMP Model Integration for AMIP. Monthly Weather Review 124(12), 2914–2932 (1996) https://doi.org/10.1175/1520-0493(1996)124%3C2914:SNEATT%3E2.0.CO;2 .Chap. Monthly Weather Review

[^4]: Hodges, K.I.: Adaptive Constraints for Feature Tracking. Monthly Weather Review 127(6), 1362–1373 (1999) https://doi.org/10.1175/1520-0493(1999)127%3C1362:ACFFT%3E2.0.CO;2 . Chap. Monthly Weather Review
