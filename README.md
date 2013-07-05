# mlabwrap

## Acknowledgement

Building upon the work done by the chap that I forked this from, I have edited the mlabwrap project.
I liked the look of the Python 3 support - though this is currently untested - which is why I chose
to fork from this project. Unfortunately, my Anaconda environment does not seem to like building
using Microsoft Visual Studio.

## Platform

One of the major reasons for using this fork was also because it claimed to allow building on
Windows. However, I haven't gotten it to work. I've maintained the logic that was apparent
in the fork so that, hopefully, it should be possible to make small changes to ``setup.py``
to allow installation on Windows.

[This site](http://obasic.net/how-to-install-mlabwrap-on-windows) has an ongoing discussion about
installing mlabwrap on Windows, though I've yet to get it to work. I'll happily discuss and fix
this fork as appropriate if anyone comes up with any ideas.

## Installation

**NOTE:** Matlab root refers to the main Matlab folder, e.g: ``/usr/local/MATLAB/R2013a/``

To install using ``pip``:
```
pip install git+https://github.com/patricksnape/mlabwrap.git
```

To manually set the Matlab root directory, use the following command:
```
pip install git+https://github.com/patricksnape/mlabwrap.git --install-option="--matlab-root=PATH_TO_MATLAB_ROOT"
```

To install using ``setup.py`` (with optional parameter ``--matlab-root``):
```
python setup.py install --matlab-root=PATH_TO_MATLAB_ROOT
```

## Usage
To import mlabwrap we do the following **(note the explict call to ``init``)**:
```
from mlabwrap import mlab
mlab.init()
import numpy as np
```

Then we can call a function as follows:
```
mlab.svd(np.array([[1,2], [1,3]]))
```

If we want to pass in an explicit version of Matlab, we simply specify the root directory:
```
from mlabwrap import mlab
mlab.init(matlab_root='/usr/local/MATLAB/R2013a')
```

## Changelog

### 1.1.6 (2013-07-05)
 * Fix ``setup.py`` so that it does correct comparisons for Matlab version numbers

### 1.1.5 (2013-06-25)
 * Change the interface to mlabwrap such that you must explicitly call the init function. 
   This allows you to pass in the matlab version you want more easily. 
   This is achieved by way of the ``matlab_root`` keyword arg that can be passed in to the ``init`` function. 
   This function is simply the old constructor.

### 1.1.4 (2013-06-25)

 * Rewrite ``setup.py`` so that it tries to guess where your Matlab folder is
 * Make ``setup.py`` work with ``pip``
 * Add flag ``--matlab-root`` to ``setup.py``
 * Fix casting bug in ``mlabwrap.cpp``
 * Remove the old code that tried to use the help command to guess the version as this doesn't work very well

### 1.1.3 (2012-11-21) - From Answeror's repository

 * using system encoding scheme to decode string in `mlabraw.eval`
 * fix memory leak in `mlabraw.put` caused by chained `char2mx` and `PyUnicode_AsUTF8String`
