# coding=utf-8
"""
Package version support using "major.minor.tiny" version scheme (a subset of PEP 386 and PEP 440).

Provides *version* and *bump* tasks.

Old style used a package/VERSION.txt file that contained a version string.
This old style is deprecated to the more pythoneese style of having a global __version__
attribute located in package/__init__.py.

# note, if the __init__.py does not have a __version__= line, then we append one to the end of the file.
This might violate PEP 8 which states that::

    "These lines should be included after the module's docstring, before any other code, separated by a
    blank line above and below."

Usage:

.. code-block: python

    package_name = 'root_package'
    setProjectVersion('0.1.2', package_name)
    ver = getProjectVersion(package_name)
    print('# Version: %s' % ver)
    # Version: 0.1.2
    bump()
    print('# Version: %s' % getProjectVersion(package_name)
    # Version: 0.1.3

.. code-block: bash

    ➤ grep version root_package/__init__.py
    __version__ = '0.1.3'

"""

__docformat__ = 'restructuredtext en'

import os
import re
from herring.herring_app import task
from safe_edit import safe_edit
from simple_logger import info, error, debug
from versio.version_scheme import Pep440VersionScheme
from project_settings import Project
from versio.version import Version


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'

Version.set_supported_version_schemes([Pep440VersionScheme])


def _file_spec(basename, project_package=None):
    """build the file spec in the project"""
    parts = [Project.herringfile_dir, project_package, basename]
    return os.path.join(*[f for f in parts if f is not None])


def get_version_from_file(project_package=None):
    """ get the version from VERSION.txt """
    try:
        parts = [Project.herringfile_dir, project_package, 'VERSION.txt']
        version_file = os.path.join(*[f for f in parts if f is not None])
        Project.version_file = version_file
        print "version_file => %s" % version_file
        with open(version_file, 'r') as file_:
            return str(Version(file_.read().strip()))
    except IOError:
        pass
    return '0.0'


def get_project_version(project_package=None):
    r"""
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :param project_package: the root package
    :type project_package: str
    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = _file_spec('__init__.py', project_package)
        debug("version_file => %s" % file_name)
        with open(file_name, 'r') as in_file:
            for line in in_file.readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = _file_spec('VERSION.txt', project_package)
        info("version_file => %s" % file_name)
        with open(file_name, 'r') as in_file:
            return in_file.read().strip()
    except IOError:
        pass

    # no joy again, so set to initial version and try again
    set_project_version('0.0.1', project_package)
    return get_project_version(project_package)


def set_project_version(version_str, project_package=None):
    """
    Set the version in __init__.py

    :param version_str: the new version string
    :type version_str: str
    :param project_package: the root package
    :type project_package: str
    """

    def version_line(ver_str):
        """
        return python line for setting the __version__ attribute

        :param ver_str: the version string
         :type ver_str: str
        """
        return "__version__ = '{version}'".format(version=ver_str)

    try:
        file_name = _file_spec('__init__.py', project_package)
        with safe_edit(file_name) as files:
            replaced = False
            for line in files['in'].readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    line = re.sub(VERSION_REGEX, version_line(version_str), line)
                    replaced = True
                files['out'].write(line)
            if not replaced:
                files['out'].write("\n")
                files['out'].write(version_line(version_str))
                files['out'].write("\n")

        file_name = _file_spec('VERSION.txt', project_package)
        if os.path.exists(file_name):
            os.remove(file_name)

    except IOError as ex:
        error(ex)
        file_name = _file_spec('VERSION.txt', project_package)
        with open(file_name, 'w') as version_file:
            version_file.write(version_str)


@task()
def bump():
    """
    Bumps the Tiny (Major.Minor.Tiny.Tiny2) version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    return bump_tiny()


@task()
def bump_tiny():
    """
    Bumps the Minor (Major.Minor.Tiny.Tiny2) version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    return bump_field('Tiny')


@task()
def bump_minor():
    """
    Bumps the Minor (Major.Minor.Tiny.Tiny2) version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    return bump_field('Minor')


@task()
def bump_major():
    """
    Bumps the Major (Major.Minor.Tiny.Tiny2) version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    return bump_field('Major')


def bump_field(field):
    original_version_str = get_project_version(project_package=Project.package)
    ver = Version(original_version_str)
    info('ver before bump: %s' % str(ver))
    ver.bump(field)
    info('ver after bump: %s' % str(ver))
    set_project_version(str(ver), project_package=Project.package)
    Project.version = get_project_version(project_package=Project.package)
    info("Bumped version from %s to %s" % (original_version_str, Project.version))
    return str(ver)


@task()
def version():
    """Show the current version"""
    info("Current version is: %s" % get_project_version(project_package=Project.package))
