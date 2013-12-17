# coding=utf-8

"""
Recursively remove files matching a pattern from a directory tree.
"""

__docformat__ = 'restructuredtext en'

import fnmatch
import os
from simple_logger import debug


def recursively_remove(path, pattern):
    """
    recursively remove files that match a given pattern

    :param path: The directory to start removing files from.
    :type path: str
    :param pattern: The file glob pattern to match for removal.
    :type pattern: str
    """
    files = [os.path.join(dir_path, f)
             for dir_path, dir_names, files in os.walk(path)
             for f in fnmatch.filter(files, pattern)]
    for file_ in files:
        debug("removing: %s" % file_)
        os.remove(file_)
