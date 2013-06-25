#!/usr/bin/env python

##############################################################################
########################### setup.py for mlabwrap ############################
##############################################################################
## o author: Alexander Schmolck (a.schmolck@gmx.net)
## o created: 2003-08-07 17:15:22+00:40
## o edited: Patrick Snape (patricksnape@gmail.com) 2013-06-25

import os
import os.path
from setuptools import setup, Extension
import sys
import subprocess
import argparse
import platform
from glob import glob
import numpy as np

# GLOBAL VARIABLES
OS = platform.system()
VALID_ARCHS = ['GLNX86', 'GLNXI64', 'GLNXA64', 'PCWIN',
               'PCWIN64', 'MAC', 'MACI', 'MACI64']


def isWindows():
    return 'Windows' == OS


def isOSX():
    return 'MacOS' == OS


def isLinux():
    return 'Linux' == OS


def check_PATH_for_folder(folder):
    """
    Checks the path for a given folder. Lower cases both the folder name and
    the path to try and get around capitalisation issues.
    """
    PATH_dirs = os.environ['PATH'].split(os.pathsep)
    folder = folder.lower()
    return [path for path in PATH_dirs if folder in path.lower()]


def case_insensitive_glob(pattern):
    """
    Performs a case insensitive GLOB on a given glob pattern
    """

    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c

    return glob(''.join(map(either, pattern)))


def find_matlab_root():
    """
    Try to find Matlab root by looking in the PATH and default installation
    directories
    """
    if isOSX():
        base_paths = ['/Applications/']
    elif isLinux():
        base_paths = ['/usr/local/MATLAB/', '/usr/local/']
    elif isWindows():
        base_paths = [os.environ["ProgramFiles"] + 'MATLAB',
                      os.environ["ProgramFiles(x86)"] + 'MATLAB',
                      os.environ["ProgramFiles"],
                      os.environ["ProgramFiles(x86)"]]
    else:
        raise Exception('Unrecognized OS')

    # Check PATH first
    path_dir = check_PATH_for_folder('matlab')
    if path_dir:
    # The PATH variable is normally the Matlab bin directory. However, multiple
        # Matlab environment variables may be set (e.g. on Windows). Therefore,
        # find the bin path and return the root directory
        try:
            path_dir = [path for path in path_dir if 'bin' in path][0]
            while 'bin' in path_dir:
                path_dir = os.path.split(path_dir)[0]
            return path_dir
        except: # Eat exception and continue
            print 'WARNING: Failed to parse PATH variable containing Matlab'

    # Otherwise loop over the given base paths
    for base_path in base_paths:
        # In older versions of Matlab/on OSX it seems it may not have installed
        # inside a directory called MATLAB, but instead just in the
        # default applications directly in a folder starting with matlab*
        # Therefore, let's make sure we've found a Matlab directory.
        if not 'MATLAB' in base_path:
            versions = case_insensitive_glob(os.path.join(base_path, 'matlab*'))
        else:
            versions = glob(os.path.join(base_path, '*'))
        if versions:
            # Default to the latest version of Matlab. 
            versions = sorted(versions, reverse=True)
            return versions[0]

    return None


def get_matlab_output(matlab_bin):
    """
    Check output doesn't exist in Python < 2.7 so we need to use the old
    communicate way. This doesn't poll and assumes that program writes output
    and then exits.
    """
    command = [matlab_bin, '-r', 'get_version', '-nosplash', '-nodesktop']
    # On Windows we can't actually write to stdout apparently so we use the
    # logfile trick and just sit and wait until Matlab is finished
    # loading the popup command window
    if isWindows():
        subprocess.call(command + ['-wait', '-logfile', 'out.txt'])
        with open('out.txt', 'r+') as f:
            return f.read()
    else:
        if sys.version_info[1] < 7:
            return subprocess.Popen(command,
                                    stdout=subprocess.PIPE).communicate()[0]
        else:
            return subprocess.check_output(command)


def get_matlab_info(matlab_bin):
    """
    Run a small Matlab script to determine the Version and Architecture (32/64)
    of the given Matlab binary
    """
    output = get_matlab_output(matlab_bin)
    # Split by new line to separate information
    # Should go Header -> Version -> Arch
    output = output.split('\n')
    # Contains some rubbish for the last but of output, but we ignore this
    # by checking if this string contains the correct ARCH and returning that
    arch_str = output[-1]
    version_str = output[-2]

    matlab_arch = None
    for arch in VALID_ARCHS:
        if arch in arch_str:
            matlab_arch = arch
            break

    version_str = version_str.split(' ')
    matlab_version = version_str[0]
    # Parse version string into major/minor float
    matlab_version = matlab_version.split('.')
    matlab_version = float(
        '{0}.{1}'.format(matlab_version[0], matlab_version[1]))
    # Slice off brackets
    matlab_release = version_str[1][1:-1]

    return (matlab_version, matlab_release, matlab_arch)


def msvc_include_dirs():
    if not 'INCLUDE' in os.environ:
        raise Exception(
            'Unable to find Microsoft Visual Studio include directories. '
            'This is because the INCLUDE environment variable is not set. '
            'In order to install using MSVC you need to run Python from within '
            'a Microsft Visual Studio command prompt.')
    return os.environ['INCLUDE'].split(os.path.sep)


def msvc_library_dirs():
    if not 'LIB' in os.environ:
        raise Exception(
            'Unable to find Microsoft Visual Studio include directories. '
            'This is because the LIB environment variable is not set. '
            'In order to install using MSVC you need to run Python from within '
            'a Microsft Visual Studio command prompt.')
    return os.environ['LIB'].split(os.path.sep)


def get_extension(EXTENSION_NAME, DEFINE_MACROS, MATLAB_LIBRARY_DIRS,
                  MATLAB_LIBRARIES, CPP_LIBRARIES, MATLAB_INCLUDE_DIRS):
    """
    We have to do this due to a bug in the compiler that means that if
    the runtime library directories get passed AT ALL to the build command
    then the binary fails to build on windows
    """
    args = [EXTENSION_NAME, ['mlabraw.cpp']]
    kwargs = {
        'define_macros': DEFINE_MACROS,
        'library_dirs': MATLAB_LIBRARY_DIRS,
        'libraries': MATLAB_LIBRARIES + CPP_LIBRARIES,
        'include_dirs': MATLAB_INCLUDE_DIRS + [np.get_include()]
    }

    if not isWindows():
        kwargs['runtime_library_dirs'] = MATLAB_LIBRARY_DIRS

    return Extension(*args, **kwargs)


def main(args):
    ### SETUP BASE VARIABLES
    MATLAB_ROOT = args.matlab_root
    MATLAB_BIN = os.path.join(MATLAB_ROOT, 'bin')
    MATLAB_BINARY = os.path.join(MATLAB_BIN, 'matlab')

    # Add .exe if windows
    if isWindows():
        MATLAB_BINARY = '{0}.exe'.format(MATLAB_BINARY)

    # Let's check that we DEFINITELY have a Matlab binary to use
    if not os.path.exists(MATLAB_BINARY):
        raise Exception(
            'Unable to find Matlab binary at {0}'.format(MATLAB_BINARY))

    # Now we come against the hardest part of all - finding the Matlab version.
    # I can think of 3 valid ways to do this:
    #   1. Parse the install directory and use a hard-coded table. However,
    #      complicated by the fact that there are SP versions and that every OS
    #      stores the directory in a different manner. 
    #      e.g. 'R2013a' could be parsed in to '2013' and 'a' and this implies V8.1 
    #      (take a look at http://en.wikipedia.org/wiki/MATLAB#Release_history)
    #   2. Parse the Help command (matlab -h). 
    #      Doesn't technically run Matlab but is a pain and I can't guarantee 
    #      that all Matlab versions print the EXACT same message.
    #      e.g. R2013a doesn't print any version information using 'matlab -h'
    #   3. Run Matlab itself and query it's 'version' command. Matlab
    #      documentation tells me that this command exists at least as far back
    #      as R14. This is the method I've chosen as it also allows me to query
    #      the 'computer' command which says which architecture Matlab is
    #      running (32 bit/64 bit). I created a short Matlab script to print
    #      the appropriate output to stdout
    MATLAB_INFO = get_matlab_info(MATLAB_BINARY)

    if None in MATLAB_INFO:
        raise Exception(
            'Unable to correctly parse Matlab information. '
            'Found Matlab Version = {0}, Matlab Release = {1}, '
            'Matlab Architecture = {2}.'.format(*MATLAB_INFO))
    else:
        [MATLAB_VERSION, MATLAB_RELEASE, MATLAB_ARCH] = MATLAB_INFO

    # Setup include and lib directories for building the extension
    MATLAB_INCLUDE_DIRS = [os.path.join(MATLAB_ROOT, 'extern', 'include')]

    if isWindows():
        EXTENSION_NAME = 'mlabraw'
        # Strip off PC from PCWIN##
        PLATFORM_DIR = MATLAB_ARCH.lower()[2:]
        CPP_LIBRARIES = []
        MATLAB_LIBRARIES = ['libeng', 'libmx']

        MATLAB_LIBRARY_DIRS = [
            os.path.join(MATLAB_ROOT, 'extern', 'lib', PLATFORM_DIR,
                         'microsoft')]
        lib_dirs = msvc_library_dirs()
        inc_dirs = msvc_library_dirs()
        if lib_dirs:
            MATLAB_LIBRARY_DIRS.extend(lib_dirs)
        if inc_dirs:
            MATLAB_INCLUDE_DIRS.extend(inc_dirs)
    else: # Linux/OSX
        EXTENSION_NAME = 'mlabrawmodule'
        PLATFORM_DIR = MATLAB_ARCH.lower()
        CPP_LIBRARIES = ['stdc++']

        if MATLAB_VERSION >= 6.5:
            MATLAB_LIBRARIES = ['eng', 'mx', 'mat', 'ut']
        else:
            MATLAB_LIBRARIES = ['eng', 'mx', 'mat', 'mi', 'ut']

        if MATLAB_VERSION >= 7:
            MATLAB_LIBRARY_DIRS = [os.path.join(MATLAB_BIN, PLATFORM_DIR)]
        else:
            MATLAB_LIBRARY_DIRS = [
                os.path.join(MATLAB_ROOT, 'extern', 'lib', PLATFORM_DIR)]

    # Version dependent defines    
    DEFINE_MACROS = []
    if MATLAB_VERSION >= 6.5:
        DEFINE_MACROS.append(('_V6_5_OR_LATER', 1))
    if MATLAB_VERSION >= 7.3:
        DEFINE_MACROS.append(('_V7_3_OR_LATER', 1))

    setup(
        name="mlabwrap",
        version='1.1.4',
        description="A high-level bridge to matlab",
        author="Alexander Schmolck",
        author_email="A.Schmolck@gmx.net",
        py_modules=["mlabwrap"],
        url='http://mlabwrap.sourceforge.net',
        ext_modules=[
            get_extension(EXTENSION_NAME, DEFINE_MACROS, MATLAB_LIBRARY_DIRS,
                          MATLAB_LIBRARIES, CPP_LIBRARIES, MATLAB_INCLUDE_DIRS)
        ],
        use_2to3=True
    )


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--matlab-root',
                        help='The full path to the Matlab root '
                             'e.g. /usr/local/MATLAB/R2013a/',
                        default=find_matlab_root())
    args = parser.parse_known_args()[0]

    main(args)
