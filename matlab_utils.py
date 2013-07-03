import platform
from glob import glob
import os


def isWindows():
    return 'Windows' == platform.system()


def isOSX():
    return 'MacOS' == platform.system()


def isLinux():
    return 'Linux' == platform.system()


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
        base_paths = ['/usr/lib/matlab/', '/usr/local/MATLAB/', 
                      '/usr/local/']
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
        if not any(x in base_path for x in ['MATLAB', 'matlab']):
            versions = case_insensitive_glob(os.path.join(base_path, 'matlab*'))
        else:
            versions = glob(os.path.join(base_path, '*'))
        if versions:
            # Default to the latest version of Matlab.
            versions = sorted(versions, reverse=True)
            return versions[0]

    return None

