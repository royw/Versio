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

# noinspection PyUnusedName
__docformat__ = 'restructuredtext en'

import re
from versio.comparable_mixin import ComparableMixin
from versio.version_scheme import Pep440VersionScheme, VersionScheme


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

    def _cmpkey(self, other=None):
        """
        A key for comparisons required by ComparableMixin

        Here we just use the list of version parts.
        """
        parts = self.parts[:]
        if self.compare_order:
            for index, value in enumerate(self.compare_order):
                parts[index] = self.parts[value]
        # if self.parts_reverse:
        #     parts.reverse()
        key = []
        for index, part in enumerate(parts):
            if part is None:
                if self.compare_fill is None:
                    key.append('~')
                else:
                    key.append(self.compare_fill[index])
            else:
                sub_parts = part.split('.')
                for sub_part in sub_parts:
                    if sub_part:
                        try:
                            key.append(int(sub_part))
                        except ValueError:
                            key.append(sub_part)
                try:
                    if other is not None:
                        other_part = other.parts[index]
                        if other_part is not None:
                            extra_sequences = len(other_part.split('.')) - len(sub_parts)
                            if extra_sequences > 0:
                                try:
                                    key += [int(self.scheme.extend_value)] * extra_sequences
                                except ValueError:
                                    key += [self.scheme.extend_value] * extra_sequences
                except IndexError as ex:
                    print(str(ex))

        return key

    def _compare(self, other, method):
        """
        Compare an object with this object using the given comparison method.

        :param other: object ot compare with
        :type other: ComparableMixin
        :param method: a comparison method
        :type method: lambda
        :return: asserted if comparison is true
        :rtype: bool
        :raises: NotImplemented
        """

        if not isinstance(other, Version):
            try:
                other = Version(str(other), scheme=self.scheme)
            except AttributeError:
                return NotImplemented

        try:
            x_cmpkey = self._cmpkey(other)[:]
            y_cmpkey = other._cmpkey(self)[:]
            # make same length
            x_cmpkey = x_cmpkey + [self.scheme.clear_value] * (len(y_cmpkey) - len(x_cmpkey))
            y_cmpkey = y_cmpkey + [self.scheme.clear_value] * (len(x_cmpkey) - len(y_cmpkey))

            for index, x in enumerate(x_cmpkey):
                y = y_cmpkey[index]
                try:
                    if int(x) == int(y):
                        continue
                except (TypeError, ValueError):
                    if str(x) == str(y):
                        continue

                try:
                    if method(int(x), int(y)):
                        return True
                except (TypeError, ValueError):
                    if method(str(x), str(y)):
                        return True
                return False
            x0 = x_cmpkey[0]
            y0 = y_cmpkey[0]
            try:
                if method(int(x0), int(y0)):
                    return True
            except (TypeError, ValueError):
                if method(str(x0), str(y0)):
                    return True
            return False
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

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
        self.compare_order = self.scheme.compare_order
        self.compare_fill = self.scheme.compare_fill

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

    # noinspection PyMethodMayBeStatic
    def _parse_with_scheme(self, version_str, scheme):
        """
        Parse the version string with the given version scheme.

        :param version_str: the version string to parse
        :type version_str: str or None
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
            # for variable dotted scheme
            if getattr(self.scheme, 'join_str', None) is not None:
                return self.scheme.join_str.join(self.parts)

            # for other schemes
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

    def bump(self, field_name=None, sub_index=-1, sequence=-1, promote=False):
        """
        Bump the given version field by 1.  If no field name is given,
        then bump the least significant field.

        Optionally can bump by sequence index where 0 is the left most part of the version.
        If a field_name is given, then the sequence value will be ignored.

        :param field_name: the field name that matches one of the scheme's fields
        :type field_name: object
        :param sub_index: index in field
        :type sub_index: int
        :param sequence: the zero offset sequence index to bump.
        :type sequence: int
        :param promote: assert if end of field sequence causes field to be cleared
        :type promote: bool
        :return: True on success
        :rtype: bool
        """
        if field_name is None:
            if sequence >= 0:
                # noinspection PyUnusedLocal
                for idx in range(len(self.parts) - 1, sequence):
                    self.parts.append(self.scheme.clear_value)
                self.parts[sequence] = str(int(self.parts[sequence]) + 1)
                for idx in range(sequence + 1, len(self.parts)):
                    self.parts[idx] = self.scheme.clear_value
                return True
            if getattr(self.scheme, 'fields', None) is None:
                self.parts[-1] = str(int(self.parts[-1]) + 1)
                return True
            field_name = self.scheme.fields[-1]
        field_name = field_name.lower()

        index = 0
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
            if promote:
                self.parts[index] = self.scheme.clear_value
                return True
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
        :type separator: str|None
        :param sub_parts: the sub parts of a version part
        :type sub_parts: list[int|str]
        :param clear_value: the value to set parts to the right of this part to after incrementing.
        :type clear_value: str|None
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

        # noinspection RegExpRedundantEscape
        match = re.match(r'^\d[\.\d]*(?<=\d)$', part)
        if match:
            # dotted numeric (ex: '1.2.3')
            return self._part_increment(field_name, sub_index, '.', [int(n) for n in part.split('.')],
                                        self.scheme.clear_value or '0')

        match = re.match(r'(\.?[a-zA-Z+]*)(\d+)', part)
        if match:
            #  alpha + numeric (ex: 'a1', 'rc2', '.post3')
            return self._part_increment(field_name, sub_index, '', [match.group(1) or '', int(match.group(2))],
                                        self.scheme.clear_value or '1')

        return part
