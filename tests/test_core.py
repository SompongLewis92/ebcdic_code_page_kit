"""Tests for ebcdic_code_page_kit.core."""

import unittest

from ebcdic_code_page_kit import decode, encode, translate, CODE_PAGE_037


class TestDecode(unittest.TestCase):
    def test_empty_bytes(self):
        self.assertEqual(decode(b""), "")

    def test_single_space(self):
        # EBCDIC 0x40 is the space character.
        self.assertEqual(decode(b"\x40"), " ")

    def test_ascii_letters(self):
        # 'Hello' in CP037: H=C8, e=85, l=93, l=93, o=96
        self.assertEqual(decode(b"\xc8\x85\x93\x93\x96"), "Hello")

    def test_digits(self):
        # Digits 0–9 are F0–F9 in EBCDIC.
        self.assertEqual(decode(b"\xf1\xf2\xf3"), "123")

    def test_control_chars(self):
        # 0x05 maps to HT (tab, U+0009), 0x25 maps to LF (U+000A).
        self.assertEqual(decode(b"\x05\x25"), "\t\n")

    def test_full_range_no_crash(self):
        # Every byte 0x00–0xFF must be representable.
        all_bytes = bytes(range(256))
        result = decode(all_bytes)
        self.assertEqual(len(result), 256)


class TestEncode(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(encode(""), b"")

    def test_single_space(self):
        self.assertEqual(encode(" "), b"\x40")

    def test_ascii_letters(self):
        self.assertEqual(encode("Hello"), b"\xc8\x85\x93\x93\x96")

    def test_digits(self):
        self.assertEqual(encode("123"), b"\xf1\xf2\xf3")

    def test_unrepresentable_raises(self):
        # U+1F600 (😀) has no CP037 representation.
        with self.assertRaises(UnicodeEncodeError):
            encode("😀")

    def test_roundtrip_ascii(self):
        original = "The quick brown fox. 12345!"
        self.assertEqual(decode(encode(original)), original)

    def test_roundtrip_with_accented(self):
        # CP037 supports several accented Latin characters.
        original = "café résumé naïve"
        self.assertEqual(decode(encode(original)), original)


class TestTranslate(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(translate(b""), b"")

    def test_identity_for_pure_cp037(self):
        # A string of CP037 bytes whose code points map back to themselves.
        sample = b"\xf1\xf2\xf3\x40\xc8\x85\x93\x93\x96"
        self.assertEqual(translate(sample), sample)

    def test_ascii_space_is_identity(self):
        # ASCII space (0x20) maps to U+0080, whose inverse CP037 byte is 0x20.
        self.assertEqual(translate(b"\x20"), b"\x20")


class TestTable(unittest.TestCase):
    def test_table_is_complete(self):
        for b in range(256):
            self.assertIn(b, CODE_PAGE_037, f"byte 0x{b:02X} missing")

    def test_space_mapping(self):
        self.assertEqual(CODE_PAGE_037[0x40], 0x20)

    def test_a_mapping(self):
        self.assertEqual(CODE_PAGE_037[0xC1], 0x41)


if __name__ == "__main__":
    unittest.main()
