# mlabwrap

## Acknowledgement

Building upon the work done by the chap that I forked this from, I have edited the mlabwrap project.
I liked the look of the Python 3 support - though this is currently untested - which is why I chose
to fork from this project. Unfortunately, my Anaconda environment does not seem to like building
using Microsoft Visual Studio.

[This site](http://obasic.net/how-to-install-mlabwrap-on-windows) has an ongoing discussion about
installing mlabwrap on Windows, though I've yet to get it to work. I'll happily discuss and fix
this fork as appropriate if anyone comes up with any ideas.

## Platform

One of the major 

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

## Changelog

### 1.1.4 (2013-06-25)

 * Rewrite ``setup.py`` so that it tries to guess where your Matlab folder is
 * Make ``setup.py`` work with ``pip``
 * Add flag ``--matlab-root`` to ``setup.py``
 * Fix casting bug in ``mlabwrap.cpp``
 * Remove the old code that tried to use the help command to guess the version as this doesn't work very well

### 1.1.3 (2012-11-21) - From Answeror's repository

 * using system encoding scheme to decode string in `mlabraw.eval`
 * fix memory leak in `mlabraw.put` caused by chained `char2mx` and `PyUnicode_AsUTF8String`
