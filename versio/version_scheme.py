"""
Generic version scheme support.
"""
import re
from textwrap import dedent

__docformat__ = 'restructuredtext en'

__all__ = ('VersionScheme', 'Simple3VersionScheme', 'Simple4VersionScheme', 'Pep440VersionScheme', 'PerlVersionScheme')


class VersionScheme(object):
    """
    This class defines the version scheme used by Version.

    A version scheme consists of a

        * name,
        * regular expression used to parse the version string,
        * the regular expression flags to use (mainly to allow verbose regexes),
        * format string used to reassemble the parsed version into a string,
        * optional list of field types (if not specified, assumes all fields are strings),
        * list of field names used for accessing the components of the version.
        * a "clear" value used to set the field values to the right of the field being bumped,
        * a sequence dictionary where the keys are the field names and the values are a list of allowed values.
          The list must be in bump order.  Bumping the last value in the list has no effect.

    Note, you need to manually maintain consistency between the regular expression,
    the format string, the optional field types, and the fields list.  For example,
    if your version scheme has N parts, then the regular expression should match
    into N groups, the format string should expect N arguments to the str.format()
    method, and there must be N unique names in the fields list.
    """

    def __init__(self, name, parse_regex, clear_value, format_str, format_types=None, fields=None, subfields=None,
                 parse_flags=0, sequences=None, description=None):
        self.name = name
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
        self.sequences = {}
        if sequences:
            for key, value in sequences.items():
                self.sequences[key.lower()] = value
        self.description = description or name

    def parse(self, version_str):
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            return [item for item in match.groups()]
        return None

    #############################################################
    # The rest of these are used by unit test for regex changes

    def _is_match(self, version_str):
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        return not (not match)

    def _release(self, version_str):
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(1)
        return result

    def _pre(self, version_str):
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(2)
        return result

    def _post(self, version_str):
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(3)
        return result

    def _dev(self, version_str):
        result = None
        match = re.match(self.parse_regex, version_str, flags=self.parse_flags)
        if match:
            result = match.group(4)
        return result


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

Pep440VersionScheme = VersionScheme(name="pep440",
                                    parse_regex=r"""
                                    ^
                                    (\d[\.\d]*(?<= \d))
                                    ((?:[abc]|rc)\d+)?
                                    (?:(\.post\d+))?
                                    (?:(\.dev\d+))?
                                    $
                                    """,
                                    parse_flags=re.VERBOSE,
                                    clear_value=None,
                                    format_str='{0}{1}{2}{3}',
                                    fields=['Release', 'Pre', 'Post', 'Dev'],
                                    subfields={'Release': ['Major', 'Minor', 'Tiny', 'Tiny2']},
                                    sequences={'Pre': ['a', 'b', 'c', 'rc'], 'Post': ['.post'], 'Dev': ['.dev']},
                                    description=dedent("""\
                                        PEP 440
                                        Public version identifiers MUST comply with the following scheme:

                                        N[.N]+[{a|b|c|rc}N][.postN][.devN]

                                        Public version identifiers MUST NOT include leading or trailing whitespace.

                                        Public version identifiers MUST be unique within a given distribution.

                                        Public version identifiers are separated into up to four segments:

                                            Release segment: N[.N]+
                                            Pre-release segment: {a|b|c|rc}N
                                            Post-release segment: .postN
                                            Development release segment: .devN
                                    """))

PerlVersionScheme = VersionScheme(name="A.B",
                                  parse_regex=r"^(\d+)\.(\d+)$",
                                  clear_value='0',
                                  format_str="{:d}.{:02d}",
                                  format_types=[int, int],
                                  fields=['Major', 'Minor'],
                                  description='perl Major.Minor version scheme')
