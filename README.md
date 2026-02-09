### pyTRACK

This is a python-wrapped implementation of the TRACK software.

To install, simply run 

```
pip install track-pylib
```

or git clone this repository and from its base folder run

```
pip install -e .
```

Then from a Python terminal, run

```
from pyTRACK import *
track()
```

This should start the TRACK namelist.

To get the tracks from an 850hPa u-v wind file, run

```
from pyTRACK import *
track_uv(path_to_file)
```