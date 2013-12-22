# coding=utf-8
"""
A generic version class that supports comparison and version bumping (incrementing by part, for example you may
bump the minor part of '1.2.3' yielding '1.3.0').

Four version schemes are included::

    * Simple3VersionScheme which supports 3 numerical part versions (A.B.C where A, B, and C are integers)
    * Simple4VersionScheme which supports 4 numerical part versions (A.B.C.D where A, B, C, and D are integers)
    * Pep440VersionScheme which supports PEP 440 (http://www.python.org/dev/peps/pep-0440/) versions
        (N[.N]+[{a|b|c|rc}N][.postN][.devN])
    * PerlVersionScheme which supports 2 numerical part versions where the second part is at least two digits
        (A.BB where A and B are integers and B is zero padded on the left.  For example:  1.02, 1.34, 1.567)

If you don't specify which version scheme the version instance uses, then it will use the first scheme from the
SupportedVersionSchemes list that successfully parses the version string

By default, Pep440VersionScheme is the supported scheme.  To change to a different list of schemes, use the
**Version.set_supported_version_schemes(schemes)**.  For example::

    from versio.version_scheme import Simple3VersionScheme, PerlVersionScheme
    Version.set_supported_version_schemes([Simple3VersionScheme, PerlVersionScheme])

In addition, you may define your own version scheme by extending VersionScheme.
"""

__docformat__ = 'restructuredtext en'

import re
from versio.comparable_mixin import ComparableMixin
from versio.version_scheme import Pep440VersionScheme


__all__ = ['Version']


class Version(ComparableMixin):
    """
    A version class that supports multiple versioning schemes, version comparisons,
    and version bumping.
    """

    # Version uses the SupportedVersionSchemes list when trying to parse a string where
    # the given scheme is None.  The parsing attempts will be sequentially thru this list
    # until a match is found.
    supported_version_schemes = [
        # Simple3VersionScheme,
        # Simple4VersionScheme,
        Pep440VersionScheme,
    ]

    def _cmpkey(self):
        """
        A key for comparisons required by ComparableMixin

        Here we just use the list of version parts.
        """
        return self.parts

    @classmethod
    def set_supported_version_schemes(cls, schemes):
        """
        Set the list of version schemes used when parsing a string.

        :param schemes:  list of version schemes.
        """
        cls.supported_version_schemes = list(schemes)

    def __init__(self, version_str=None, scheme=None):
        """
        Creates a version instance which is bound to a version scheme.

        :param version_str: the initial version as a string
        :type version_str: str or None
        :param scheme: the version scheme to use to parse the version string or None to try all supported
        version schemes.
        :type scheme: VersionScheme or None
        """
        self.scheme, self.parts = self._parse(version_str, scheme)
        if not self.scheme:
            raise AttributeError("Can not find supported scheme for \"{ver}\"".format(ver=version_str))
        if not self.parts:
            raise AttributeError("Can not parse \"{ver}\"".format(ver=version_str))

    def _parse(self, version_str, scheme):
        """
        Parse the given version string using the given version scheme.  If the given version scheme
        is None, then try all supported version schemes stopping with the first one able to successfully
        parse the version string.

        :param version_str: the version string to parse
        :type version_str: str
        :param scheme: the version scheme to use
        :type scheme: VersionScheme or None
        :return: the version scheme that can parse the version string, and the version parts as parsed.
        :rtype: VersionScheme or None, list
        """
        if scheme is None:
            for trial_scheme in self.supported_version_schemes:
                parts = self._parse_with_scheme(version_str, trial_scheme)
                if parts:
                    return trial_scheme, parts
        else:
            return scheme, self._parse_with_scheme(version_str, scheme)
        return None

    def _parse_with_scheme(self, version_str, scheme):
        """
        Parse the version string with the given version scheme.

        :param version_str: the version string to parse
        :type version_str: str
        :param scheme: the version scheme to use
        :type scheme: VersionScheme
        :returns the parts of the version identified with the regular expression or None.
        :rtype: list of str or None
        """
        if version_str is None:
            return False
        return scheme.parse(version_str)

    def __str__(self):
        """
        Render to version to a string.

        :return: the version as a string.
        :rtype: str
        """
        if self.parts:
            casts = self.scheme.format_types
            casts = casts + [str] * (len(self.scheme.fields) - len(casts))   # right fill with str types

            parts = [part or '' for part in self.parts]
            parts = parts + [''] * (len(self.scheme.fields) - len(parts))   # right fill with blanks

            def _type_cast(value, cast):
                """cast the given value to the given cast or str if cast is None"""
                if cast is None:
                    cast = str
                result = None
                try:
                    result = cast(value)
                except ValueError:
                    pass
                return result

            args = list(map(_type_cast, parts, casts))
            return self.scheme.format_str.format(*args)
        return "Unknown version"

    def bump(self, field_name=None, sub_index=-1):
        """
        Bump the given version field by 1.  If no field name is given,
        then bump the least significant field.

        :param field_name: the field name that matches one of the scheme's fields
        :type field_name: object
        :param sub_index: index in field
        :type sub_index: int
        :return: True on success
        :rtype: bool
        """
        if field_name is None:
            field_name = self.scheme.fields[-1]
        field_name = field_name.lower()

        # noinspection PyBroadException
        try:
            bumped = False
            index = self.scheme.fields.index(field_name)
            for idx, part in enumerate(self.parts):
                if idx == index:
                    bumped_part = self._bump_parse(field_name, part, sub_index)
                    if self.parts[idx] != bumped_part:
                        self.parts[idx] = bumped_part
                        bumped = True

                if idx > index:
                    self.parts[idx] = self.scheme.clear_value
            return bumped
        except (IndexError, ValueError):
            # not if fields, try subfields
            if field_name in self.scheme.subfields:
                return self.bump(*self.scheme.subfields[field_name])
            return False

    def _increment(self, field_name, value):
        """
        Increment the value for the given field.

        :param field_name: the field we are incrementing
        :type field_name: str
        :param value: the field's value
        :type value: int or str
        :return: the value after incrementing
        :rtype: int or str
        """
        if isinstance(value, int):
            value += 1
        if isinstance(value, str):
            if field_name in self.scheme.sequences:
                seq_list = self.scheme.sequences[field_name]
                if not value:
                    return seq_list[0]
                if value not in seq_list:
                    raise AttributeError('Can not bump version, the current value (%s) not in sequence constraints' %
                                         value)
                idx = seq_list.index(value) + 1
                if idx < len(seq_list):
                    return seq_list[idx]
                else:
                    raise IndexError('Can not increment past end of sequence')
            else:
                value = chr(ord(value) + 1)
        return value

    def _part_increment(self, field_name, sub_index, separator, sub_parts, clear_value):
        """
        Increment a version part, including handing parts to the right of the field being incremented.

        :param field_name: the field we are incrementing
        :type field_name: str
        :param sub_index: the index of the sub part we are incrementing
        :type sub_index: int
        :param separator: the separator between sub parts
        :type separator: str or None
        :param sub_parts: the sub parts of a version part
        :type sub_parts: list of int or str
        :param clear_value: the value to set parts to the right of this part to after incrementing.
        :type clear_value: str or None
        :return:
        :rtype:
        """
        sub_parts[sub_index] = self._increment(field_name, sub_parts[sub_index])
        if sub_index >= 0:
            for sub_idx in range(sub_index + 1, len(sub_parts)):
                sub_parts[sub_idx] = clear_value
        return separator.join([str(n) for n in sub_parts])

    def _bump_parse(self, field_name, part, sub_index):
        """
        Bump (increment) the given field of a version.

        :param field_name: the field we are incrementing
        :type field_name: str
        :param part: the version part being incremented
        :type part: str or None
        :param sub_index:
        :type sub_index:
        :return: the version part after incrementing
        :rtype: int or str or None
        """
        if part is None:
            value = self.scheme.clear_value or '1'
            return '{seq}{value}'.format(seq=self.scheme.sequences[field_name][0], value=value)

        match = re.match(r'^\d[\.\d]*(?<=\d)$', part)
        if match:
            # dotted numeric (ex: '1.2.3')
            return self._part_increment(field_name, sub_index, '.', [int(n) for n in part.split('.')],
                                        self.scheme.clear_value or '0')

        match = re.match(r'(\.?[a-zA-Z]*)(\d+)', part)
        if match:
            #  alpha + numeric (ex: 'a1', 'rc2', '.post3')
            return self._part_increment(field_name, sub_index, '', [match.group(1) or '', int(match.group(2))],
                                        self.scheme.clear_value or '1')

        return part
