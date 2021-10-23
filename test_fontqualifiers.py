#!/usr/bin/env python
"""
Test that the reading font qualifiers works the way we expect.

SUT:    Ancilliary: Font
Area:   Qualifier Parsing
Class:  Functional
Type:   Unit test
"""

import os
import sys
import unittest

try:
    import nose
except ImportError:
    nose = None

sys.path.append(os.path.join(os.path.dirname(__file__), 'riscos/graphics'))

import fontqualifiers


class FQTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        pass


class Test10BasicStrings(FQTestCase):

    def test_01_empty(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers('')

    def test_02_bare(self):
        fq = fontqualifiers.FontQualifiers('Homerton.Medium')
        self.assertEqual(fq.fontid, 'Homerton.Medium')

    def test_03_spaces(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers('Homerton Medium')


class Test20FontIdentifier(FQTestCase):

    def test_01_missing_identifier(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers(r'\F')

    def test_02_simple_identifier(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium')
        self.assertEqual(fq.fontid, 'Homerton.Medium')

    def test_03_invalid_characters(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers(r'\F Homerton.Medium')


class Test30Encoding(FQTestCase):

    def test_01_missing_encoding(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers(r'\E')

    def test_02_simple_encoding(self):
        fq = fontqualifiers.FontQualifiers(r'\ELatin1')
        self.assertEqual(fq.encoding, 'Latin1')

    def test_03_invalid_characters(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadStringError):
            fq = fontqualifiers.FontQualifiers(r'\E Latin1')

    def test_10_with_font(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1')
        self.assertEqual(fq.fontid, 'Homerton.Medium')
        self.assertEqual(fq.encoding, 'Latin1')

    def test_11_with_font_without_F(self):
        fq = fontqualifiers.FontQualifiers(r'Homerton.Medium\ELatin1')
        self.assertEqual(fq.fontid, 'Homerton.Medium')
        self.assertEqual(fq.encoding, 'Latin1')


class Test40Matrix(FQTestCase):

    def test_01_missing_content(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M')

    def test_11_elements_1(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0')

    def test_12_elements_2(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0 0')

    def test_13_elements_3(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0 0 0')

    def test_14_elements_4(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0 0 0 0')

    def test_15_elements_5(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0 0 0 0 0')

    def test_16_elements_6(self):
        fq = fontqualifiers.FontQualifiers(r'\M0 0 0 0 0 0')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_17_elements_7(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M0 0 0 0 0 0 0')

    def test_20_negative(self):
        fq = fontqualifiers.FontQualifiers(r'\M-65536 0 0 -65536 0 -1')

    def test_21_too_large(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M2147483648 0 0 -1 0 -1')

    def test_22_elements_too_small(self):
        with self.assertRaises(fontqualifiers.FontQualifiersBadMatrixError):
            fq = fontqualifiers.FontQualifiers(r'\M-2147483648 0 0 -1 0 -1')

    def test_23_fractions(self):
        fq = fontqualifiers.FontQualifiers(r'\M32768 16384 131072 98304 1000 500')
        self.assertEqual(fq.matrix, [0.5, 0.25, 2, 1.5, 1, 0.5])


class Test50ApplyFields(FQTestCase):

    def test_01_apply_empty(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')
        fq.apply_fields(r'')

        self.assertEqual(fq.fontid, 'Homerton.Medium')
        self.assertEqual(fq.encoding, 'Latin1')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_02_apply_fontid(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')
        fq.apply_fields(r'Selwyn')

        self.assertEqual(fq.fontid, 'Selwyn')
        self.assertEqual(fq.encoding, 'Latin1')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_03_apply_qualified_fontid(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')
        fq.apply_fields(r'\FSelwyn')

        self.assertEqual(fq.fontid, 'Selwyn')
        self.assertEqual(fq.encoding, 'Latin1')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_10_remove_fontid(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')
        fq.apply_fields(r'\F')

        self.assertEqual(fq.fontid, None)
        self.assertEqual(fq.encoding, 'Latin1')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_11_remove_fontid_encoding(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')
        fq.apply_fields(r'\F\E')

        self.assertEqual(fq.fontid, None)
        self.assertEqual(fq.encoding, None)
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])

    def test_21_apply_to_empty(self):
        fq = fontqualifiers.FontQualifiers(r'', allow_empty=True)
        fq.apply_fields(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0')

        self.assertEqual(fq.fontid, 'Homerton.Medium')
        self.assertEqual(fq.encoding, 'Latin1')
        self.assertEqual(fq.matrix, [0, 0, 0, 0, 0, 0])


class Test50EncodeString(FQTestCase):

    def test_01_regular(self):
        fq = fontqualifiers.FontQualifiers('Homerton.Medium')
        self.assertEqual(fq.font_string, 'Homerton.Medium')

    def test_02_font_qualifier(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium')
        self.assertEqual(fq.font_string, 'Homerton.Medium')

    def test_03_encoding(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1')
        self.assertEqual(fq.font_string, r'\FHomerton.Medium\ELatin1')

    def test_04_matrix(self):
        fq = fontqualifiers.FontQualifiers(r'\M65536 0 0 -32768 1000 0')
        self.assertEqual(fq.font_string, r'\M65536 0 0 -32768 1000 0 ')

    def test_10_font_encoding(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1')
        self.assertEqual(fq.font_string, r'\FHomerton.Medium\ELatin1')

    def test_11_font_encoding_matrix(self):
        fq = fontqualifiers.FontQualifiers(r'\FHomerton.Medium\ELatin1\M65536 0 0 -32768 1000 0')
        self.assertEqual(fq.font_string, r'\FHomerton.Medium\ELatin1\M65536 0 0 -32768 1000 0 ')


class Test90FindField(FQTestCase):

    def test_01_absent_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0', 'X')
        self.assertIsNone(offset)

    def test_11_first_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0', 'F')
        self.assertEqual(offset, 2)

    def test_12_second_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0', 'E')
        self.assertEqual(offset, 19)

    def test_13_third_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'\FHomerton.Medium\ELatin1\M0 0 0 0 0 0', 'M')
        self.assertEqual(offset, 27)

    def test_21_bare_first_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'Homerton.Medium\ELatin1\M0 0 0 0 0 0', 'F')
        self.assertEqual(offset, 0)

    def test_22_bare_second_field(self):
        offset = fontqualifiers.FontQualifiers.find_field(r'Homerton.Medium\ELatin1\M0 0 0 0 0 0', 'E')
        self.assertEqual(offset, 17)


if __name__ == '__main__':
    __name__ = os.path.basename(sys.argv[0][:-3])  # pylint: disable=redefined-builtin
    if nose:
        env = os.environ
        env['NOSE_WITH_XUNIT'] = '1'
        env['NOSE_VERBOSE'] = '1'
        exit(nose.runmodule(env=env))
    else:
        unittest.main()
