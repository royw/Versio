# coding=utf-8
"""
    This class defines the version scheme used by Version.

    A version scheme consists of a::

        * name,
        * regular expression used to parse the version string,
        * the regular expression flags to use (mainly to allow verbose regexes),
        * format string used to reassemble the parsed version into a string,
        * optional list of field types (if not specified, assumes all fields are strings),
        * list of field names used for accessing the components of the version.
        * an optional subfield dictionary with the key being a field name and the value being a list of sub field names.
          For example, in the Pep440VersionScheme, the "Release" field may contain multiple parts, so we use
          subfield names for the parts.  Say we have a version of "1.2.3rc1", the "1.2.3" is the release field, then
          "1" is the "major" subfield, "2" is the "minor" subfield, and "3" is the "tiny" subfield.
        * a "clear" value used to set the field values to the right of the field being bumped,
        * a sequence dictionary where the keys are the field names and the values are a list of allowed values.
          The list must be in bump order.  Bumping the last value in the list has no effect.

    Note, you need to manually maintain consistency between the regular expression,
    the format string, the optional field types, and the fields list.  For example,
    if your version scheme has N parts, then the regular expression should match
    into N groups, the format string should expect N arguments to the str.format()
    method, and there must be N unique names in the fields list.
"""

# noinspection PyUnusedName
__docformat__ = 'restructuredtext en'

import re
from textwrap import dedent

__all__ = ('VersionScheme', 'Simple3VersionScheme', 'Simple4VersionScheme', 'Pep440VersionScheme',
           'PerlVersionScheme', 'Simple5VersionScheme', 'VariableDottedIntegerVersionScheme')


class AVersionScheme(object):
    def __init__(self, name, description=None):
        """
        The commonality between version schemes.

        :param name: the name of the versioning scheme.
        :type name: str
        :param description: the description of the versioning scheme
        :type description: str
        """
        self.name = name
        self.description = description or name
        self.compare_order = None
        self.compare_fill = None
        self.format_types = []
        self.extend_value = '0'

    # noinspection PyUnusedFunction
    def parse(self, version_str):
        """
        Parse the version using this scheme from the given string.  Returns None if unable to parse.

        :param version_str: A string that may contain a version in this version scheme.
        :returns: the parts of the version identified with the regular expression or None.
        :rtype: list of str or None
        """
        raise NotImplemented


class VersionScheme(AVersionScheme):
    """Describe a versioning scheme"""

    def __init__(self, name, parse_regex, clear_value, format_str, format_types=None, fields=None, subfields=None,
                 parse_flags=0, compare_order=None, compare_fill=None, sequences=None, description=None):
        """
        A versioning scheme is defined when an instance is created.
        :param name: the name of the versioning scheme.
        :type name: str
        :param parse_regex: the regular expression that parses the version from a string.
        :type parse_regex: str
        :param clear_value: the value that the fields to the right of the bumped field get set to.
        :type clear_value: str or None
        :param format_str: the format string used to reassemble the version into a string
        :type format_str: str
        :param format_types: a list of types used to case the version parts before formatting.
        :type format_types: list of type
        :param fields: the list of field names used to access the individual version parts
        :type fields: list of str
        :param subfields: a dictionary of field name/list of subfield names use to access parts within a version part
        :type subfields: dict
        :param parse_flags: the regular expression flags to use when parsing a version string
        :type parse_flags: int
        :param compare_order: The optional list containing the order to compare the parts.
        :type compare_order: list[int] or None
        :param compare_fill: The optional list containing the fill string to use when comparing the parts.
        :type compare_fill: list[str] or None
        :param sequences: a dictionary of field name/list of values used for sequencing a version part
        :type sequences: dict
        :param description: the description of the versioning scheme
        :type description: str
        """
        super(VersionScheme, self).__init__(name=name, description=description)
        self.parse_regex = parse_regex
        self.clear_value = clear_value
        self.format_str = format_str
        self.format_types = format_types or []      # unspecified format parts are cast to str
        self.fields = [field.lower() for field in (fields or [])]
        self.subfields = {}
        for key in (subfields or {}):
            for index, field_name in enumerate(subfields[key] or []):
                self.subfields[field_name.lower()] = [key, index]

        self.parse_flags = parse_flags
        self.compare_order = compare_order
        self.compare_fill = compare_fill
        self.sequences = {}
        if sequences:
            for key, value in sequences.items():
                self.sequences[key.lower()] = value

    def parse(self, version_str):
        """
        Parse the version using this scheme from the given string.  Returns None if unable to parse.

        :param version_str: A string that may contain a version in this version scheme.
        :returns: the parts of the version identified with the regular expression or None.
        :rtype: list of str or None
        """
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        result = None
        if match:
            result = []
            for item in match.groups():
                if item is None:
                    item = self.clear_value
                result.append(item)
        return result

    #############################################################
    # The rest of these are used by unit test for regex changes

    def _is_match(self, version_str):
        """
        Is this versioning scheme able to successfully parse the given string?

        :param version_str: a string containing a version
        :type version_str: str
        :return: asserted if able to parse the given version string
        :rtype: bool
        """
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        return not (not match)

    def _release(self, version_str):
        """
        Get the first matching group of the version.

        :param version_str: a string containing a version
        :type version_str: str
        :return: the first matching group of the version
        :rtype: str or None
        """
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(1)
        return result

    def _pre(self, version_str):
        """

        :param version_str: a string containing a version
        :type version_str: str
        :return: the second matching group of the version
        :rtype: str or None
        """
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(2)
        return result

    def _post(self, version_str):
        """

        :param version_str: a string containing a version
        :type version_str: str
        :return: the third matching group of the version
        :rtype: str or None
        """
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(3)
        return result

    def _dev(self, version_str):
        """

        :param version_str: a string containing a version
        :type version_str: str
        :return: the fourth matching group of the version
        :rtype: str or None
        """
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(4)
        return result

    def _local(self, version_str):
        """

        :param version_str: a string containing a version
        :type version_str: str
        :return: the fifth matching group of the version
        :rtype: str|int|None
        """
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(5)
        return result


class VersionSplitScheme(AVersionScheme):
    """
    Support splitting a version string into a variable number of segments.

    For example, "1.2.3" => ['1', '2', '3']

    When comparing versions, right pad with clear_value the segments until both versions have
    the same number of segments, then perform the compare.
    """
    def __init__(self, name, split_regex=r"\.", clear_value='0', join_str='.', description=None):
        """
        :param name: the name of the versioning scheme.
        :type name: str
        :param split_regex: the regular expression that splits the version into sequences.
        :type split_regex: str
        :param clear_value: the value that the fields to the right of the bumped field get set to.
        :type clear_value: str
        :param join_str: the sequence separator string
        :type join_str: str
        :param description: the description of the versioning scheme
        :type description: str
        """
        super(VersionSplitScheme, self).__init__(name=name, description=description)
        self.split_regex = split_regex
        self.clear_value = clear_value
        self.join_str = join_str

    def parse(self, version_str):
        """
        Parse the version using this scheme from the given string.  Returns None if unable to parse.

        :param version_str: A string that may contain a version in this version scheme.
        :returns: the parts of the version identified with the regular expression or None.
        :rtype: list of str or None
        """
        parts = re.split(self.split_regex, version_str)
        if not parts[-1]:
            raise AttributeError('Version can not end in a version separator')
        return parts

    #############################################################
    # The rest of these are used by unit test for regex changes

    def _is_match(self, version_str):
        """
        Is this versioning scheme able to successfully parse the given string?

        :param version_str: a string containing a version
        :type version_str: str
        :return: asserted if able to parse the given version string
        :rtype: bool
        """
        # noinspection PyBroadException
        try:
            self.parse(version_str)
            return True
        except Exception:
            return False

    def _release(self, version_str):
        """
        Get the first matching group of the version.

        :param version_str: a string containing a version
        :type version_str: str
        :return: the first matching group of the version
        :rtype: str or None
        """
        result = None
        parts = self.parse(version_str)
        if parts:
            result = parts[0]
        return result

# now define the supported version schemes:


Simple3VersionScheme = VersionScheme(name="A.B.C",
                                     parse_regex=r"^(\d+)\.(\d+)\.(\d+)$",
                                     clear_value='0',
                                     format_str="{0}.{1}.{2}",
                                     fields=['Major', 'Minor', 'Tiny'],
                                     description='Simple Major.Minor.Tiny version scheme')

Simple4VersionScheme = VersionScheme(name="A.B.C.D",
                                     parse_regex=r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$",
                                     clear_value='0',
                                     format_str="{0}.{1}.{2}.{3}",
                                     fields=['Major', 'Minor', 'Tiny', 'Tiny2'],
                                     description='Simple Major.Minor.Tiny.Tiny2 version scheme')

Simple5VersionScheme = VersionScheme(name="A.B.C.D.E",
                                     parse_regex=r"^(\d+)\.(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?$",
                                     clear_value='0',
                                     format_str="{0}.{1}.{2}.{3}.{4}",
                                     format_types=[int, int, int, int, int],
                                     fields=['Major', 'Minor', 'Tiny', 'Build', 'Patch'],
                                     description='Simple Major.Minor.Tiny.Build.Patch version scheme')

VariableDottedIntegerVersionScheme = VersionSplitScheme(name='A.B...',
                                                        description='A variable number of dot separated '
                                                                    'integers version scheme')

Pep440VersionScheme = VersionScheme(name="pep440",
                                    parse_regex=r"""
                                    ^
                                    (\d[\.\d]*(?<= \d))
                                    ((?:[abc]|rc)\d+)?
                                    (?:(\.post\d+))?
                                    (?:(\.dev\d+))?
                                    (?:(\+(?![.])[a-zA-Z0-9\.]*[a-zA-Z0-9]))?
                                    $
                                    """,
                                    compare_order=[0, 1, 2, 3, 4],
                                    compare_fill=['~', '~', '', '~', ''],
                                    parse_flags=re.VERBOSE,
                                    clear_value=None,
                                    format_str='{0}{1}{2}{3}{4}',
                                    fields=['Release', 'Pre', 'Post', 'Dev', 'Local'],
                                    subfields={'Release': ['Major', 'Minor', 'Tiny', 'Tiny2']},
                                    sequences={'Pre': ['a', 'b', 'c', 'rc'],
                                               'Post': ['.post'],
                                               'Dev': ['.dev'],
                                               'Local': ['+']},
                                    description=dedent("""\
                                        PEP 440
                                        Public version identifiers MUST comply with the following scheme:

                                        N[.N]+[{a|b|c|rc}N][.postN][.devN][+local]

                                        Public version identifiers MUST NOT include leading or trailing whitespace.

                                        Public version identifiers MUST be unique within a given distribution.

                                        Public version identifiers are separated into up to five segments:

                                            Release segment: N[.N]+
                                            Pre-release segment: {a|b|c|rc}N
                                            Post-release segment: .postN
                                            Development release segment: .devN
                                            Local release segment: +local

                                        The local version labels MUST be limited to the following set of permitted
                                        characters:

                                            ASCII letters ( [a-zA-Z] )
                                            ASCII digits ( [0-9] )
                                            periods ( . )

                                        Local version labels MUST start and end with an ASCII letter or digit.
                                    """))

PerlVersionScheme = VersionScheme(name="A.B",
                                  parse_regex=r"^(\d+)\.(\d+)$",
                                  clear_value='0',
                                  format_str="{0:d}.{1:02d}",
                                  format_types=[int, int],
                                  fields=['Major', 'Minor'],
                                  description='perl Major.Minor version scheme')
