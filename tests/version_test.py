# coding=utf-8
"""
py.test unit tests for Versio.
"""
from _pytest.python import raises
from versio.version import Version
from versio.version_scheme import Pep440VersionScheme, Simple3VersionScheme, Simple4VersionScheme, PerlVersionScheme


Version.set_supported_version_schemes((Simple3VersionScheme, Simple4VersionScheme, Pep440VersionScheme,))


# noinspection PyProtectedMember,PyDocstring
class TestVersion(object):
    def _check_parsing(self, version, release, pre=None, post=None, dev=None):
        """helper for checking the parsing"""
        scheme = Pep440VersionScheme
        return (scheme._is_match(version) and
                scheme._release(version) == release and
                scheme._pre(version) == pre and
                scheme._post(version) == post and
                scheme._dev(version) == dev)

    def test_pep440_parse(self):
        """check basic parsing capability"""
        assert (self._check_parsing(version='1', release='1'))
        assert (self._check_parsing(version='1.2', release='1.2'))
        assert (self._check_parsing(version='1.2.3a4', release='1.2.3', pre='a4'))
        assert (self._check_parsing(version='1.2.3b4', release='1.2.3', pre='b4'))
        assert (self._check_parsing(version='1.2.3c4', release='1.2.3', pre='c4'))
        assert (self._check_parsing(version='1.2.3rc4', release='1.2.3', pre='rc4'))
        assert (self._check_parsing(version='1.2.3rc4.post5', release='1.2.3', pre='rc4', post='.post5'))
        assert (self._check_parsing(version='1.2.3rc4.post5.dev6', release='1.2.3', pre='rc4', post='.post5',
                                    dev='.dev6'))
        assert (self._check_parsing(version='1.2.3.post5.dev6', release='1.2.3', post='.post5', dev='.dev6'))
        assert (self._check_parsing(version='1.2.3.post5', release='1.2.3', post='.post5'))
        assert (self._check_parsing(version='1.2.3.dev6', release='1.2.3', dev='.dev6'))

        assert (not Pep440VersionScheme._is_match('1.'))
        assert (not Pep440VersionScheme._is_match('1.2.3.rc4'))
        assert (not Pep440VersionScheme._is_match('1.2.3-rc4'))
        assert (not Pep440VersionScheme._is_match('1.2.3_rc4'))

    def test_simple3_parse(self):
        """check basic parsing capability"""
        assert (Simple3VersionScheme._is_match('1.2.3'))
        assert (not Simple3VersionScheme._is_match('1.2'))
        assert (not Simple3VersionScheme._is_match('1.2.3.4'))

    def test_simple4_parse(self):
        """check basic parsing capability"""
        assert (Simple4VersionScheme._is_match('1.2.3.4'))
        assert (not Simple4VersionScheme._is_match('1.2.3'))
        assert (not Simple4VersionScheme._is_match('1.2.3.4.5'))

    def test_perl_version(self):
        """roundtrip, parse then convert back to string"""

        def _round_trip(version_str):
            """roundtrip, parse then convert back to string"""
            assert (str(Version(version_str, scheme=PerlVersionScheme)) == version_str)

        _round_trip('1.02')
        _round_trip('10.302')

    def test_pep440_version(self):
        """roundtrip, parse then convert back to string"""

        def _round_trip(version_str):
            """roundtrip, parse then convert back to string"""
            assert (str(Version(version_str, scheme=Pep440VersionScheme)) == version_str)
            assert (str(Version(version_str)) == version_str)

        _round_trip('1')
        _round_trip('1.2')
        _round_trip('1.2.3')
        _round_trip('1.2.3a4')
        _round_trip('1.2.3b4')
        _round_trip('1.2.3c4')
        _round_trip('1.2.3rc4')
        _round_trip('1.2.3rc4.post5')
        _round_trip('1.2.3rc4.post5.dev6')
        _round_trip('1.2.3rc4.dev6')
        _round_trip('1.2.3.post5')
        _round_trip('1.2.3.post5.dev6')
        _round_trip('1.2.3.dev6')

    def test_pep440_version_errors(self):
        """garbage in check, bad versions"""
        raises(AttributeError, lambda: Version('1.', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1-2', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1_2', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.a4', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3-a4', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3_a4', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3a4-foo5', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3a4.foo5', scheme=Simple3VersionScheme))

    def test_simple3_version(self):
        """roundtrip, parse then convert back to string"""
        assert (str(Version('1.2.3', scheme=Simple3VersionScheme)) == '1.2.3')

    def test_simple3_version_errors(self):
        """garbage in check, bad versions"""
        raises(AttributeError, lambda: Version('1.2', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.', scheme=Simple3VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.4', scheme=Simple3VersionScheme))

    def test_simple4_version(self):
        """roundtrip, parse then convert back to string"""
        assert (str(Version('1.2.3.4', scheme=Simple4VersionScheme)) == '1.2.3.4')

    def test_simple4_version_errors(self):
        """garbage in check, bad versions"""
        raises(AttributeError, lambda: Version('1.2.3', scheme=Simple4VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.', scheme=Simple4VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.4.', scheme=Simple4VersionScheme))
        raises(AttributeError, lambda: Version('1.2.3.4.5', scheme=Simple4VersionScheme))

    def test_simple3_bump(self):
        """version bumps"""
        v1 = Version('1.2.3', scheme=Simple3VersionScheme)
        assert (v1.bump())
        assert (str(v1) == '1.2.4')
        assert (v1.bump('Minor'))
        assert (str(v1) == '1.3.0')
        assert (v1.bump('minor'))
        assert (str(v1) == '1.4.0')
        assert (v1.bump('Tiny'))
        assert (str(v1) == '1.4.1')
        assert (v1.bump('tiny'))
        assert (str(v1) == '1.4.2')
        assert (v1.bump('Major'))
        assert (str(v1) == '2.0.0')

    def test_simple3_bump_errors(self):
        """bad bump commands"""
        v1 = Version('1.2.3', scheme=Simple3VersionScheme)
        assert (not v1.bump(''))
        assert (str(v1) == '1.2.3')
        assert (not v1.bump('foo'))
        assert (str(v1) == '1.2.3')

    def test_simple4_bump(self):
        """version bumps"""
        v1 = Version('1.2.3.4', scheme=Simple4VersionScheme)
        assert (v1.bump())
        assert (str(v1) == '1.2.3.5')

        assert (v1.bump('Minor'))
        assert (str(v1) == '1.3.0.0')

        assert (v1.bump('Tiny'))
        assert (str(v1) == '1.3.1.0')

        assert (v1.bump('Tiny2'))
        assert (str(v1) == '1.3.1.1')

        assert (v1.bump('Major'))
        assert (str(v1) == '2.0.0.0')

    def test_pep440_bump(self):
        """version bumps"""
        v1 = Version('1.2.3a4.post5.dev6', scheme=Pep440VersionScheme)
        assert (v1.bump('dev'))
        assert (str(v1) == '1.2.3a4.post5.dev7')

        assert (not v1.bump('dev', 0))
        assert (str(v1) == '1.2.3a4.post5.dev7')

        assert (v1.bump('dev', 1))
        assert (str(v1) == '1.2.3a4.post5.dev8')

        assert (v1.bump('post'))
        assert (str(v1) == '1.2.3a4.post6')
        assert (not v1.bump('post', 0))
        assert (str(v1) == '1.2.3a4.post6')
        assert (v1.bump('post', 1))
        assert (str(v1) == '1.2.3a4.post7')

        assert (v1.bump('pre'))
        assert (str(v1) == '1.2.3a5')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3b1')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3c1')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3rc1')
        assert (not v1.bump('pre', 0))
        assert (str(v1) == '1.2.3rc1')

        assert (v1.bump('release'))
        assert (str(v1) == '1.2.4')
        assert (v1.bump('release', 2))
        assert (str(v1) == '1.2.5')
        assert (v1.bump('release', 1))
        assert (str(v1) == '1.3.0')
        assert (v1.bump('release', 0))
        assert (str(v1) == '2.0.0')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('post'))
        assert (str(v1) == '1.2.3a4.post6')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('pre'))
        assert (str(v1) == '1.2.3a5')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3b1')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('release'))
        assert (str(v1) == '1.2.4')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('release', 2))
        assert (str(v1) == '1.2.4')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('release', 1))
        assert (str(v1) == '1.3.0')

        v1 = Version('1.2.3a4.post5.dev6')
        assert (v1.bump('release', 0))
        assert (str(v1) == '2.0.0')

    def test_pep440_bump_subfields(self):
        """PEP 440 subfield bumps"""

        v1 = Version('1.2.3.4', scheme=Pep440VersionScheme)
        v1.bump('Tiny2')
        assert (str(v1) == '1.2.3.5')
        v1.bump('Tiny')
        assert (str(v1) == '1.2.4.0')
        v1.bump('Minor')
        assert (str(v1) == '1.3.0.0')
        v1.bump('Major')
        assert (str(v1) == '2.0.0.0')

    def test_pep440_bump_errors(self):
        """PEP 440 bump errors"""

        v1 = Version('1.2.3a4.post5.dev6', scheme=Pep440VersionScheme)
        assert (not v1.bump('release', 3))
        assert (str(v1) == '1.2.3a4.post5.dev6')

    def test_pep440_bump_sequences(self):
        """PEP 440 sequence bumps"""

        v1 = Version('1.2.3a4.post5.dev6', scheme=Pep440VersionScheme)
        assert (not v1.bump('dev', 0))
        assert (str(v1) == '1.2.3a4.post5.dev6')

        assert (not v1.bump('post', 0))
        assert (str(v1) == '1.2.3a4.post5.dev6')

        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3b1')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3c1')
        assert (v1.bump('pre', 0))
        assert (str(v1) == '1.2.3rc1')
        assert (not v1.bump('pre', 0))
        assert (str(v1) == '1.2.3rc1')

    def test_pep440_bump_pre(self):
        """PEP 440 field bumps that start new version parts"""

        v1 = Version('1.2.3', scheme=Pep440VersionScheme)
        assert (v1.bump('pre', 0), str(v1))
        assert (str(v1) == '1.2.3a1')
        assert (v1.bump('pre', 1), str(v1))
        assert (str(v1) == '1.2.3a2')

        assert (v1.bump('post', 0), str(v1))
        assert (str(v1) == '1.2.3a2.post1')

        assert (v1.bump('dev', 0), str(v1))
        assert (str(v1) == '1.2.3a2.post1.dev1')

    def test_simple3_version_comparisons(self):
        """test comparison operators on Simple3VersionScheme"""
        # load versions with increasing version numbers
        versions = [Version(vstr, scheme=Simple3VersionScheme) for vstr in [
            '0.0.0',
            '0.0.1',
            '0.0.2',
            '0.0.9',
            '0.3.0',
            '0.3.4',
            '0.3.5',
            '0.4.0',
            '0.4.9',
            '1.0.0',
            '1.0.1',
            '1.10.0',
            '2.0.0',
            '2.0.11',
            '2.3.0',
            '10.0.0',
            '10.0.18',
            '10.22.0',
            '999.999.999'
        ]]

        # check each adjacent version numbers
        for index, version in enumerate(versions[0:-1]):
            assert versions[index] < versions[index + 1], \
                "{v1} < {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] > versions[index], \
                "{v1} > {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] <= versions[index + 1], \
                "{v1} <= {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] >= versions[index], \
                "{v1} >= {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] != versions[index + 1], \
                "{v1} != {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert Version(str(versions[index]), scheme=Simple3VersionScheme) == versions[index], \
                "{v1} == {v2}".format(v1=Version(str(versions[index])), v2=versions[index])

    def test_simple4_version_comparisons(self):
        """test comparison operators on Simple4VersionScheme"""
        # load versions with increasing version numbers
        versions = [Version(vstr, scheme=Simple4VersionScheme) for vstr in [
            '0.0.0.0',
            '0.0.0.1',
            '0.0.0.2',
            '0.0.0.9',
            '0.0.3.0',
            '0.0.3.4',
            '0.0.3.5',
            '0.0.4.0',
            '0.0.4.9',
            '0.1.0.0',
            '0.1.0.1',
            '0.1.10.0',
            '0.2.0.0',
            '0.2.0.11',
            '0.2.3.0',
            '0.10.0.0',
            '0.10.0.18',
            '0.10.22.0',
            '1.0.0.0',
            '1.0.0.1',
            '1.0.1.0',
            '1.1.0.0',
            '1.10.0.0',
            '1.10.10.0',
            '1.10.10.10',
            '10.10.10.10',
            '999.999.999.999'
        ]]

        # check each adjacent version numbers
        for index, version in enumerate(versions[0:-1]):
            assert versions[index] < versions[index + 1], \
                "{v1} < {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] > versions[index], \
                "{v1} > {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] <= versions[index + 1], \
                "{v1} <= {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] >= versions[index], \
                "{v1} >= {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] != versions[index + 1], \
                "{v1} != {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert Version(str(versions[index]), scheme=Simple4VersionScheme) == versions[index], \
                "{v1} == {v2}".format(v1=Version(str(versions[index])), v2=versions[index])

    def test_perl_version_comparisons(self):
        """test comparison operators on PerlVersionScheme"""
        # load versions with increasing version numbers
        versions = [Version(vstr, scheme=PerlVersionScheme) for vstr in [
            '0.00',
            '0.01',
            '0.20',
            '0.90',
            '3.00',
            '3.04',
            '3.50',
            '4.00',
            '4.09',
            '10.00',
            '10.18',
            '999.999'
        ]]

        # check each adjacent version numbers
        for index, version in enumerate(versions[0:-1]):
            assert versions[index] < versions[index + 1], \
                "{v1} < {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] > versions[index], \
                "{v1} > {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] <= versions[index + 1], \
                "{v1} <= {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] >= versions[index], \
                "{v1} >= {v2}".format(v1=versions[index + 1], v2=versions[index])
            assert versions[index] != versions[index + 1], \
                "{v1} != {v2}".format(v1=versions[index], v2=versions[index + 1])
            assert Version(str(versions[index]), scheme=PerlVersionScheme) == versions[index], \
                "{v1} == {v2}".format(v1=Version(str(versions[index])), v2=versions[index])

    def test_pep440_version_comparisons(self):
        """test comparison operators on Pep440VersionScheme"""
        # load versions with increasing version numbers
        versions = [Version(vstr, scheme=Pep440VersionScheme) for vstr in [
            '0.0.0.0',
            '0.0.0.1',
            '0.0.0.2',
            '0.0.0.9',
            '0.0.3.0',
            '0.0.3.4',
            '0.0.3.5',
            '0.0.4.0',
            '0.0.4.9',
            '0.1.0.0',
            '0.1.0.1',
            '0.1.10.0',
            '0.2.0.0',
            '0.2.0.11',
            '0.2.3.0',
            '0.10.0.0',
            '0.10.0.18',
            '0.10.22.0',
            '1.0.0.0',
            '1.0.0.1',
            '1.0.1.0a1',
            '1.0.1.0a2',
            '1.0.1.0b1',
            '1.0.1.0b2',
            '1.0.1.0c1',
            '1.0.1.0c2',
            '1.0.1.0rc1',
            '1.0.1.0rc2.dev1',
            '1.0.1.0rc2.dev2',
            '1.0.1.0rc2',
            '1.0.1.0rc2.post1.dev1',
            '1.0.1.0rc2.post1.dev2',
            '1.0.1.0rc2.post1',
            '1.0.1.0.dev1',
            '1.0.1.0.dev2',
            '1.0.1.0',
            '1.1.0.0',
            '1.10.0.0',
            '1.10.10.0',
            '1.10.10.10',
            '10.10.10.10',
            '999.999.999.999'
        ]]

        # check each adjacent version numbers
        for index, version in enumerate(versions[0:-1]):
            assert versions[index] < versions[index + 1], \
                self.compare_to_str(op='<', v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] > versions[index], \
                self.compare_to_str(op='>', v1=versions[index + 1], v2=versions[index])
            assert versions[index] <= versions[index + 1], \
                self.compare_to_str(op='<=', v1=versions[index], v2=versions[index + 1])
            assert versions[index + 1] >= versions[index], \
                self.compare_to_str(op='>=', v1=versions[index + 1], v2=versions[index])
            assert versions[index] != versions[index + 1], \
                self.compare_to_str(op='!=', v1=versions[index], v2=versions[index + 1])
            assert Version(str(versions[index]), scheme=Pep440VersionScheme) == versions[index], \
                self.compare_to_str(op='==', v1=Version(str(versions[index])), v2=versions[index])

    def compare_to_str(self, op, v1, v2):
        output = "{v1}({k1}) {op} {v2}({k2}".format(op=op, v1=v1, k1=repr(v1._cmpkey()), v2=v2, k2=repr(v2._cmpkey()))
        return output
