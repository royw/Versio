from unittest import TestCase
from versio.version import Version
from versio.version_scheme import Pep440VersionScheme, Simple3VersionScheme, Simple4VersionScheme, PerlVersionScheme


# noinspection PyProtectedMember
class VersionTest(TestCase):
    def setUp(self):
        Version.set_supported_version_schemes((Simple3VersionScheme, Simple4VersionScheme, Pep440VersionScheme,))

    def tearDown(self):
        pass

    def checkParsing(self, version, release, pre=None, post=None, dev=None):
        scheme = Pep440VersionScheme        
        return (scheme._is_match(version) and
                scheme._release(version) == release and
                scheme._pre(version) == pre and
                scheme._post(version) == post and
                scheme._dev(version) == dev)

    def test_pep440_parse(self):
        """check basic parsing capability"""
        self.assertTrue(self.checkParsing(version='1', release='1'))
        self.assertTrue(self.checkParsing(version='1.2', release='1.2'))
        self.assertTrue(self.checkParsing(version='1.2.3a4', release='1.2.3', pre='a4'))
        self.assertTrue(self.checkParsing(version='1.2.3b4', release='1.2.3', pre='b4'))
        self.assertTrue(self.checkParsing(version='1.2.3c4', release='1.2.3', pre='c4'))
        self.assertTrue(self.checkParsing(version='1.2.3rc4', release='1.2.3', pre='rc4'))
        self.assertTrue(self.checkParsing(version='1.2.3rc4.post5', release='1.2.3', pre='rc4', post='.post5'))
        self.assertTrue(self.checkParsing(version='1.2.3rc4.post5.dev6', release='1.2.3', pre='rc4', post='.post5',
                                          dev='.dev6'))
        self.assertTrue(self.checkParsing(version='1.2.3.post5.dev6', release='1.2.3', post='.post5', dev='.dev6'))
        self.assertTrue(self.checkParsing(version='1.2.3.post5', release='1.2.3', post='.post5'))
        self.assertTrue(self.checkParsing(version='1.2.3.dev6', release='1.2.3', dev='.dev6'))

        self.assertTrue(not Pep440VersionScheme._is_match('1.'))
        self.assertTrue(not Pep440VersionScheme._is_match('1.2.3.rc4'))
        self.assertTrue(not Pep440VersionScheme._is_match('1.2.3-rc4'))
        self.assertTrue(not Pep440VersionScheme._is_match('1.2.3_rc4'))

    def test_simple3_parse(self):
        """check basic parsing capability"""
        self.assertTrue(Simple3VersionScheme._is_match('1.2.3'))
        self.assertTrue(not Simple3VersionScheme._is_match('1.2'))
        self.assertTrue(not Simple3VersionScheme._is_match('1.2.3.4'))

    def test_simple4_parse(self):
        """check basic parsing capability"""
        self.assertTrue(Simple4VersionScheme._is_match('1.2.3.4'))
        self.assertTrue(not Simple4VersionScheme._is_match('1.2.3'))
        self.assertTrue(not Simple4VersionScheme._is_match('1.2.3.4.5'))

    def test_perl_version(self):
        """roundtrip, parse then convert back to string"""

        def round_trip(version_str):
            """roundtrip, parse then convert back to string"""
            self.assertEqual(str(Version(version_str, scheme=PerlVersionScheme)), version_str)
            self.assertEqual(str(Version(version_str)), version_str)

        round_trip('1.02')
        round_trip('10.302')

    def test_pep440_version(self):
        """roundtrip, parse then convert back to string"""

        def round_trip(version_str):
            """roundtrip, parse then convert back to string"""
            self.assertEqual(str(Version(version_str, scheme=Pep440VersionScheme)), version_str)
            self.assertEqual(str(Version(version_str)), version_str)

        round_trip('1')
        round_trip('1.2')
        round_trip('1.2.3')
        round_trip('1.2.3a4')
        round_trip('1.2.3b4')
        round_trip('1.2.3c4')
        round_trip('1.2.3rc4')
        round_trip('1.2.3rc4.post5')
        round_trip('1.2.3rc4.post5.dev6')
        round_trip('1.2.3rc4.dev6')
        round_trip('1.2.3.post5')
        round_trip('1.2.3.post5.dev6')
        round_trip('1.2.3.dev6')

    def test_pep440_version_errors(self):
        """garbage in check, bad versions"""
        self.assertRaises(AttributeError, lambda: Version('1.', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1-2', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1_2', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.a4', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3-a4', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3_a4', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3a4-foo5', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3a4.foo5', scheme=Simple3VersionScheme))

    def test_simple3_version(self):
        """roundtrip, parse then convert back to string"""
        self.assertEqual(str(Version('1.2.3', scheme=Simple3VersionScheme)), '1.2.3')
    
    def test_simple3_version_errors(self):
        """garbage in check, bad versions"""
        self.assertRaises(AttributeError, lambda: Version('1.2', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.', scheme=Simple3VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.4', scheme=Simple3VersionScheme))

    def test_simple4_version(self):
        """roundtrip, parse then convert back to string"""
        self.assertEqual(str(Version('1.2.3.4', scheme=Simple4VersionScheme)), '1.2.3.4')

    def test_simple4_version_errors(self):
        """garbage in check, bad versions"""
        self.assertRaises(AttributeError, lambda: Version('1.2.3', scheme=Simple4VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.', scheme=Simple4VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.4.', scheme=Simple4VersionScheme))
        self.assertRaises(AttributeError, lambda: Version('1.2.3.4.5', scheme=Simple4VersionScheme))

    def test_simple3_bump(self):
        """version bumps"""
        v1 = Version('1.2.3', scheme=Simple3VersionScheme)
        self.assertTrue(v1.bump())
        self.assertEqual(str(v1), '1.2.4')
        self.assertTrue(v1.bump('Minor'))
        self.assertEqual(str(v1), '1.3.0')
        self.assertTrue(v1.bump('minor'))
        self.assertEqual(str(v1), '1.4.0')
        self.assertTrue(v1.bump('Tiny'))
        self.assertEqual(str(v1), '1.4.1')
        self.assertTrue(v1.bump('tiny'))
        self.assertEqual(str(v1), '1.4.2')
        self.assertTrue(v1.bump('Major'))
        self.assertEqual(str(v1), '2.0.0')

    def test_simple3_bump_errors(self):
        """bad bump commands"""
        v1 = Version('1.2.3', scheme=Simple3VersionScheme)
        self.assertFalse(v1.bump(''))
        self.assertEqual(str(v1), '1.2.3')
        self.assertFalse(v1.bump('foo'))
        self.assertEqual(str(v1), '1.2.3')

    def test_simple4_bump(self):
        """version bumps"""
        v1 = Version('1.2.3.4', scheme=Simple4VersionScheme)
        self.assertTrue(v1.bump())
        self.assertEqual(str(v1), '1.2.3.5')
        self.assertTrue(v1.bump('Minor'))
        self.assertEqual(str(v1), '1.3.0.0')
        self.assertTrue(v1.bump('Tiny'))
        self.assertEqual(str(v1), '1.3.1.0')
        self.assertTrue(v1.bump('Tiny2'))
        self.assertEqual(str(v1), '1.3.1.1')
        self.assertTrue(v1.bump('Major'))
        self.assertEqual(str(v1), '2.0.0.0')

    def test_pep440_bump(self):
        """version bumps"""
        v1 = Version('1.2.3a4.post5.dev6', scheme=Pep440VersionScheme)
        self.assertTrue(v1.bump('dev'))
        self.assertEqual(str(v1), '1.2.3a4.post5.dev7')
        self.assertTrue(v1.bump('dev', 0))
        self.assertEqual(str(v1), '1.2.3a4.post5.dev0')
        self.assertTrue(v1.bump('dev', 1))
        self.assertEqual(str(v1), '1.2.3a4.post5.dev1')

        v1.bump('post')
        self.assertEqual(str(v1), '1.2.3a4.post6')
        v1.bump('post', 0)
        self.assertEqual(str(v1), '1.2.3a4.post0')
        v1.bump('post', 1)
        self.assertEqual(str(v1), '1.2.3a4.post1')

        v1.bump('pre')
        self.assertEqual(str(v1), '1.2.3a5')
        v1.bump('pre', 0)
        self.assertEqual(str(v1), '1.2.3b0')
        v1.bump('pre', 0)
        self.assertEqual(str(v1), '1.2.3c0')
        v1.bump('pre', 0)
        self.assertEqual(str(v1), '1.2.3rc0')
        v1.bump('pre', 0)
        self.assertEqual(str(v1), '1.2.3rc0')

        v1.bump('release')
        self.assertEqual(str(v1), '1.2.4')
        v1.bump('release', 2)
        self.assertEqual(str(v1), '1.2.5')
        v1.bump('release', 1)
        self.assertEqual(str(v1), '1.3.0')
        v1.bump('release', 0)
        self.assertEqual(str(v1), '2.0.0')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('post')
        self.assertEqual(str(v1), '1.2.3a4.post6')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('pre')
        self.assertEqual(str(v1), '1.2.3a5')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('pre', 0)
        self.assertEqual(str(v1), '1.2.3b0')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('release')
        self.assertEqual(str(v1), '1.2.4')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('release', 2)
        self.assertEqual(str(v1), '1.2.4')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('release', 1)
        self.assertEqual(str(v1), '1.3.0')

        v1 = Version('1.2.3a4.post5.dev6')
        v1.bump('release', 0)
        self.assertEqual(str(v1), '2.0.0')

    def test_pep440_bump_subfields(self):
        v1 = Version('1.2.3.4', scheme=Pep440VersionScheme)
        v1.bump('Tiny2')
        self.assertEqual(str(v1), '1.2.3.5')
        v1.bump('Tiny')
        self.assertEqual(str(v1), '1.2.4.0')
        v1.bump('Minor')
        self.assertEqual(str(v1), '1.3.0.0')
        v1.bump('Major')
        self.assertEqual(str(v1), '2.0.0.0')


    def test_pep440_bump_errors(self):
        v1 = Version('1.2.3a4.post5.dev6')
        self.assertFalse(v1.bump('release', 3))
        self.assertEqual(str(v1), '1.2.3a4.post5.dev6')
