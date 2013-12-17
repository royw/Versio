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
from versio.comparable_mixin import ComparableMixin
from versio.version_scheme import Pep440VersionScheme

__docformat__ = 'restructuredtext en'

import re


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
        """A key for comparisons required by ComparableMixin"""
        return self.parts

    @classmethod
    def set_supported_version_schemes(cls, schemes):
        cls.supported_version_schemes = list(schemes)

    def __init__(self, version_str=None, scheme=None):
        self.scheme, self.parts = self._parse(version_str, scheme)
        if not self.scheme:
            raise AttributeError("Can not find supported scheme for \"{ver}\"".format(ver=version_str))
        if not self.parts:
            raise AttributeError("Can not parse \"{ver}\"".format(ver=version_str))

    def _parse(self, version_str, scheme):
        if scheme is None:
            for trial_scheme in self.supported_version_schemes:
                parts = self._parse_with_scheme(version_str, trial_scheme)
                if parts:
                    return trial_scheme, parts
        else:
            return scheme, self._parse_with_scheme(version_str, scheme)

    def _parse_with_scheme(self, version_str, scheme):
        if version_str is None:
            return False
        return scheme.parse(version_str)

    def __str__(self):
        if self.parts:
            casts = self.scheme.format_types
            parts = [part or '' for part in self.parts]

            def type_cast(value, cast):
                if cast is None:
                    cast = str
                result = None
                # noinspection PyBroadException
                try:
                    result = cast(value)
                except:
                    pass
                return result

            return self.scheme.format_str.format(*map(type_cast, parts, casts))
        return "Unknown version"

    def bump(self, field_name=None, sub_index=-1):
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
        field_name = field_name.lower()

        # noinspection PyBroadException
        try:
            index = self.scheme.fields.index(field_name)
            for idx, part in enumerate(self.parts):
                if idx == index:
                    self.parts[idx] = self._bump_parse(field_name, part, sub_index)

                if idx > index:
                    self.parts[idx] = self.scheme.clear_value

            return True
        except:
            # not if fields, try subfields
            if field_name in self.scheme.subfields:
                return self.bump(*self.scheme.subfields[field_name])
            return False

    def _increment(self, field_name, value):
        if isinstance(value, (int, long)):
            value += 1
        if isinstance(value, str):
            if field_name in self.scheme.sequences:
                seq_list = self.scheme.sequences[field_name]
                if value not in seq_list:
                    raise AttributeError('Can not bump version, the current value (%s) not in sequence constraints' %
                                         value)
                idx = seq_list.index(value) + 1
                if idx < len(seq_list):
                    return seq_list[idx]
            else:
                value = chr(ord(value) + 1)
        return value

    def _part_increment(self, field_name, sub_index, separator, sub_parts):
        sub_parts[sub_index] = self._increment(field_name, sub_parts[sub_index])
        if sub_index >= 0:
            for sub_idx in range(sub_index + 1, len(sub_parts)):
                sub_parts[sub_idx] = 0
        return separator.join([str(n) for n in sub_parts])

    def _bump_parse(self, field_name, part, sub_index):
        match = re.match('^\d[\.\d]*(?<=\d)$', part)
        if match:
            # dotted numeric (ex: '1.2.3')
            return self._part_increment(field_name, sub_index, '.', [int(n) for n in part.split('.')])

        match = re.match(r'(\.?[a-zA-Z]*)(\d+)', part)
        if match:
            #  alpha + numeric (ex: 'a1', 'rc2', '.post3')
            return self._part_increment(field_name, sub_index, '', [match.group(1) or '', int(match.group(2))])

        return part