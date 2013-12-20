# coding=utf-8

"""
Safely edit a file by creating a backup which will be restored on any error.
"""
import re

__docformat__ = 'restructuredtext en'

import os
import shutil
from tempfile import NamedTemporaryFile
from contextlib import contextmanager


@contextmanager
def safe_edit(file_name):
    """
    Edit a file using a backup.  On any exception, restore the backup.

    Usage::

        with safeEdit(fileName) as files:
            for line in files['in'].readlines():
                # edit line
                files['out'].write(line)

    :param file_name:  source file to edit
    :type file_name: str
    :yield: dict containing open file instances for input (files['in']) and output (files['out'])
    :raises: allows IO exceptions to propagate
    """
    backup_name = file_name + '~'

    in_file = None
    tf_name = None
    tmp_file = None
    try:
        in_file = open(file_name, 'r')
        tmp_file = NamedTemporaryFile(delete=False)
        tf_name = tmp_file.name
        yield {'in': in_file, 'out': tmp_file}

    # intentionally catching any exceptions
    # pylint: disable=W0702
    except:
        # on any exception, delete the output temporary file
        if tmp_file:
            tmp_file.close()
            tmp_file = None
        if tf_name:
            os.remove(tf_name)
            tf_name = None
        raise
    finally:
        if in_file:
            in_file.close()
        if tmp_file:
            tmp_file.close()
        if tf_name:
            # ideally this block would be thread locked at os level
            # remove previous backup file if it exists
            # noinspection PyBroadException
            try:
                os.remove(backup_name)
            except:
                pass

            # Note, shutil.move will safely move even across file systems

            # backup source file
            shutil.move(file_name, backup_name)

            # put new file in place
            shutil.move(tf_name, file_name)


def quick_edit(file_name, regex_replacement_dict):
    """
    This handles replacing text by using regular expressions.

    The simple case of replacing the first occurrence in each line of 'foo' with 'bar' is::

        quick_edit(file_name, {'foo': ['bar']})
        quick_edit(file_name, {r'.*?(foo).*': ['bar']})

    To replace 'foo' with 'bar' and 'car' with 'dog' in each line::

        quick_edit(file_name, {'foo': ['bar'],
                               'car': ['dog']})

    You can use multiple groups like:

        quick_edit(file_name, {r'.*?(foo).*?(car).*': ['bar', 'dog']})


    WARNING, there are probably gotchas here.

    :param file_name: file to edit
    :param regex_replacement_dict:
    """
    with safe_edit(file_name) as files:
        for line in files['in'].readlines():
            out_line = _line_replacement(line, regex_replacement_dict)
            files['out'].write(out_line)


def _line_replacement(line, regex_replacement_dict):
    for regex in regex_replacement_dict.keys():
        line = _single_replacement(line, regex, regex_replacement_dict[regex])
    return line


def _single_replacement(line, regex, values):
    newline = line
    if '(' not in regex:
        regex = '.*(' + regex + ').*'
    match = re.match(regex, line)
    if match:
        newline = ''
        postfix = ''
        for group in range(1, len(match.groups()) + 1):
            a = 0
            if group > 1:
                a = match.end(group - 1)
            newline += line[a:match.start(group)]
            newline += values[group - 1]
            postfix = line[match.end(group):]
        newline += postfix
    return newline
