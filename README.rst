Versio
======

Latin

    Noun
    1. a turning, change, version


Versio is a generic version class that supports comparison and version bumping (incrementing by part, for example
you may bump the minor part of '1.2.3' yielding '1.3.0').

Four version schemes are included:

    * **Simple3VersionScheme** which supports 3 numerical part versions (A.B.C where A, B, and C are integers)
    * **Simple4VersionScheme** which supports 4 numerical part versions (A.B.C.D where A, B, C, and D are integers)
    * **Pep440VersionScheme** which supports PEP 440 (http://www.python.org/dev/peps/pep-0440/) versions
      (N[.N]+[{a|b|c|rc}N][.postN][.devN])
    * **PerlVersionScheme** which supports 2 numerical part versions where the second part is at least two digits
      (A.BB where A and B are integers and B is zero padded on the left.  For example:  1.02, 1.34, 1.567)

If you don't specify which version scheme the version instance uses, then it will use the first scheme from the
**SupportedVersionSchemes** list that successfully parses the version string

By default, **Pep440VersionScheme** is the supported scheme.  To change to a different list of schemes, use the
**Version.set_supported_version_schemes(schemes)**.  For example::

    from versio.version_scheme import Simple3VersionScheme, PerlVersionScheme
    Version.set_supported_version_schemes([Simple3VersionScheme, PerlVersionScheme])

In addition, you may define your own version scheme by creating a new VersionScheme instance.

The VersionScheme class defines the version scheme.

A version scheme consists of:

    * a name,
    * a regular expression used to parse the version string,
    * the regular expression flags to use (mainly to allow verbose regexes),
    * a format string used to reassemble the parsed version into a string,
    * an optional list of field types (if not specified, assumes all fields are strings),
    * a list of field names used for accessing the components of the version.
    * an optional subfield dictionary with the key being a field name and the value being a list of sub field names.
      For example, in the **Pep440VersionScheme**, the "Release" field may contain multiple parts, so we use
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

Installation
============

From pypi::

    pip install Versio


Usage
=====

First let's just play with the comparing and bumping versions::

    >>> from versio.version import Version
    >>> from versio.version_scheme import Pep440VersionScheme
    >>> v1 = Version('1.2.3rc4.post5.dev6', scheme=Pep440VersionScheme)
    >>> v2 = Version('1.2.3rc4.post5.dev7', scheme=Pep440VersionScheme)
    >>> v1 == v2
    False
    >>> v1 < v2
    True
    >>> v1.bump('dev')
    True
    >>> str(v1)
    '1.2.3rc4.post5.dev7'
    >>> v1 == v2
    True
    >>> v1.bump('pre')
    True

Now let's look in the PEP 440 scheme::

    >>> Pep440VersionScheme.fields
    ['release', 'pre', 'post', 'dev']
    >>> Pep440VersionScheme.format_str
    '{0}{1}{2}{3}'

The fields are used by the **bump(field)** method in the above example.  We skipped bumping the release above so let's
do it here::

    >>> v1 = Version('1.2.3rc4.post5.dev6', scheme=Pep440VersionScheme)
    >>> str(v1)
    '1.2.3rc4.post5.dev6'
    >>> v1.bump('release')
    True
    >>> str(v1)
    '1.2.4'

For PEP 440, the release part is defined as "N[.N]+".  We can bump specific parts of the release by using an
index like::

    >>> v1.bump('release', 2)
    True
    >>> str(v1)
    '1.2.5'
    >>> v1.bump('release', 1)
    True
    >>> str(v1)
    '1.3.0'
    >>> v1.bump('release', 0)
    True
    >>> str(v1)
    '2.0.0'

To use a name directly, we use the concept of subfields which are mapped to a field/index pair::

    >>> Pep440VersionScheme.subfields
    {'tiny2': ['Release', 3], 'major': ['Release', 0], 'tiny': ['Release', 2], 'minor': ['Release', 1]}

    >>> v1 = Version('1.2.3rc4.post5.dev6', scheme=Pep440VersionScheme)
    >>> str(v1)
    '1.2.3rc4.post5.dev6'
    >>> v1.bump('tiny')
    True
    >>> str(v1)
    '1.2.4'
    >>> v1.bump('minor')
    True
    >>> str(v1)
    '1.3.0'
    >>> v1.bump('major')
    True
    >>> str(v1)
    '2.0.0'

Now that you've seen the version scheme in action, let's take a look at how it is defined::

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
                                        format_str='{0}{1}{2}{3}',
                                        format_types=[str, str, str, str],
                                        clear_value=None,
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

The **parse_regex** and **parse_flags** do what you think by parsing a string into a list containing regex groups,
except the group list is zero indexed to the first matching group.

The **format_str** and **format_types** control how the version is converted to a string in **__str__()**.  Basically
**format_str.format(*args)** is called where the args is a list built by casting each of the version's groups using
the corresponding type from the  **format_types** list.  If you don't specify a **format_types**, then each group
is cast as a str.

The **clear_value** typically should be '0' for numeric versions and None for non-numeric.  Basically it specifies
what to put in the groups to the right of the group being bumped.

The **sequences** dictionary maps text to prepend to a group when formatting.  The dictionary keys must be in the
**fields** list.  To progress thru the sequence, bump the field with an index of 0.  An index of 1 bumps the numeric
part of the group.  For example::

    >>> v1 = Version('1.2.3a4.post5.dev6', scheme=Pep440VersionScheme)
    >>> str(v1)
    '1.2.3a4.post5.dev6'
    >>> v1.bump('pre', 0)
    True
    >>> str(v1)
    '1.2.3b1'
    >>> v1.bump('pre', 1)
    True
    >>> str(v1)
    '1.2.3b2'
    >>> v1.bump('pre', 0)
    True
    >>> str(v1)
    '1.2.3c1'
    >>> v1.bump('pre', 0)
    True
    >>> str(v1)
    '1.2.3rc1'
    >>> v1.bump('pre', 0)
    False
    >>> str(v1)
    '1.2.3rc1'

Notice that bumping fails at the end of the sequence and the version is not changed.

That's it.

There are more examples in *tests/version_test.py*.  You may test directly with *py.test* or against multiple
python versions with *tox*.

Enjoy!
