import glob
import os
import shutil
import sys
import fnmatch
from os.path import isdir, join

def include_patterns(*patterns):
    """ Function that can be used as shutil.copytree() ignore parameter that
    determines which files *not* to ignore, the inverse of "normal" usage.

    This is a factory function that creates a function which can be used as a
    callable for copytree()'s ignore argument, *not* ignoring files that match
    any of the glob-style patterns provided.

    ‛patterns’ are a sequence of pattern strings used to identify the files to
    include when copying the directory tree.

    Example usage:

        copytree(src_directory, dst_directory,
                 ignore=include_patterns('*.sldasm', '*.sldprt'))
    """
    def _ignore_patterns(path, all_names):
        # Determine names which match one or more patterns (that shouldn't be
        # ignored).
        keep = (name for pattern in patterns
                        for name in fnmatch.filter(all_names, pattern))
        # Ignore file names which *didn't* match any of the patterns given that
        # aren't directory names.
        dir_names = (name for name in all_names if isdir(join(path, name)))
        return set(all_names) - set(keep) - set(dir_names)

    return _ignore_patterns

def copy(src, dest):
    for file_path in glob.glob(os.path.join(src, '**', '*.html'), recursive=True):
        print(f'Copying {file_path}')
        new_path = os.path.join(dest, os.path.basename(file_path))
        shutil.copy(file_path, new_path)


if __name__ == '__main__':
    shutil.copytree(sys.argv[1], sys.argv[2], ignore = include_patterns('*.html'))
    print('Done!')



