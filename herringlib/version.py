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
from comparable_mixin import ComparableMixin
from safe_edit import safe_edit
from simple_logger import info, error, debug

from herring.herring_app import task
from project_settings import Project


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def _file_spec(basename, project_package=None):
    """build the file spec in the project"""
    parts = [Project.herringfile_dir, project_package, basename]
    return os.path.join(*[f for f in parts if f is not None])


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


@task()
def bump():
    """
    Bumps the patch version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    original_version_str = get_project_version(project_package=Project.package)
    ver = Version(original_version_str)
    ver.bump_field('Tiny')
    set_project_version(str(ver), project_package=Project.package)
    Project.version = get_project_version(project_package=Project.package)
    info("Bumped version from %s to %s" % (original_version_str, Project.version))


@task()
def version():
    """Show the current version"""
    info("Current version is: %s" % get_project_version(project_package=Project.package))


class VersionScheme(object):
    """
    This class defines the version scheme used by Version.

    A version scheme consists of a

        * name,
        * regular expression used to parse the version string,
        * format string used to reassemble the parsed version into a string,
        * list of field names used for accessing the components of the version.

    Note, you need to manually maintain consistency between the regular expression,
    the format string, and the fields list.  For example, if your version scheme
    has N parts, then the regular expression should match into N groups, the format
    string should expect N arguments to the str.format() method, and there must be
    N unique names in the fields list.
    """
    def __init__(self, name, parse_regex, format_str, fields=None):
        self.name = name
        self.parse_regex = parse_regex
        self.format_str = format_str
        self.fields = fields or []


Simple3VersionScheme = VersionScheme(name="A.B.C",
                                     parse_regex=r"^(\d+)\.(\d+)\.(\d+)$",
                                     format_str="{0}.{1}.{2}",
                                     fields=['Major', 'Minor', 'Tiny'])

Simple4VersionScheme = VersionScheme(name="A.B.C.D",
                                     parse_regex=r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$",
                                     format_str="{0}.{1}.{2}.{3}",
                                     fields=['Major', 'Minor', 'Tiny', 'Tiny2'])

# Version uses the SupportedVersionSchemes list when trying to parse a string where
# the given scheme is None.  The parsing attempts will be sequentially thru this list
# until a match is found.
SupportedVersionSchemes = [
    Simple3VersionScheme,
    Simple4VersionScheme
]


class Version(ComparableMixin):
    """
    A version class that supports multiple versioning schemes, version comparisons,
    and version bumping.
    """

    def _cmpkey(self):
        """A key for comparisons required by ComparableMixin"""
        return self.parts

    def __init__(self, version_str=None, scheme=None):
        self.scheme = scheme
        self.parts = []
        if not self._parse(version_str):
            raise AttributeError("Can not parse \"{ver}\"".format(ver=version_str))

    def _parse(self, version_str):
        if self.scheme is None:
            for scheme in SupportedVersionSchemes:
                if self._parse_with_scheme(version_str, scheme):
                    self.scheme = scheme
                    return True
        else:
            return self._parse_with_scheme(version_str, self.scheme)

    def _parse_with_scheme(self, version_str, scheme):
        if version_str is None:
            return False
        match = re.match(scheme.parse_regex, version_str)
        if match:
            self.parts = [int(item) for item in match.groups()]
            return True
        return False

    def __str__(self):
        if self.parts:
            return self.scheme.format_str.format(*self.parts)
        return "Unknown version"

    def bump_field(self, field_name=None):
        """
        Bump the given version field by 1.  If no field name is given,
        then bump the least significant field.

        :param field_name: the field name that matches one of the scheme's fields
        :type field_name: object
        :return: True on success
        :rtype: bool
        """
        if field_name is None:
            field_name = self.scheme.fields[-1]
        # noinspection PyBroadException
        try:
            index = self.scheme.fields.index(field_name)
            self.parts[index] += 1
            self.parts[index + 1:] = [0] * (len(self.parts) - index - 1)
            return True
        except:
            return False
