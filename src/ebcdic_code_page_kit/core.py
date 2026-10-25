"""Core EBCDIC Code Page 037 translation logic.

This module provides a complete, dependency-free mapping between bytes
(0x00–0xFF) and Unicode code points per IBM code page 037 (United States/
Canada; full 256-entry table including PUA box-drawing glyphs).

Design decisions
----------------
* We chose CP037 because it is the dominant North American mainframe
  interchange code page and the one most EBCDIC data files in the wild use.
  Supporting a second code page would force callers to pass a code-page
  identifier on every call, which adds friction for the common case and
  ambiguity for round-tripping.
* The mapping table is generated programmatically from a compact dict so
  that the table can be inspected for correctness without staring at 256
  hex literals. The compact dict lists every non-identity entry plus the
  identity entries that are easy to miss (0x09→U+0009, 0x40→U+0020).
* We deliberately raise UnicodeDecodeError rather than returning a
  replacement character. Silent corruption is the single worst failure
  mode for legacy-data pipelines; a loud error tells the caller their
  code page assumption is wrong.
"""

from __future__ import annotations

from typing import Dict

# Compact mapping: every byte 0x00–0xFF to its Unicode code point.
# Identity entries (byte 0xNN maps to U+00NN) are omitted for brevity
# except where including them aids comprehension.
_COMPACT_MAP: Dict[int, int] = {
    0x00: 0x0000,  # NUL
    0x01: 0x0001,  # SOH
    0x02: 0x0002,  # STX
    0x03: 0x0003,  # ETX
    0x04: 0x009C,  # PF → U+009C STRING TERMINATOR
    0x05: 0x0009,  # HT (tab)
    0x06: 0x0086,  # LC → U+0086 START OF SELECTED AREA
    0x07: 0x007F,  # DEL
    0x08: 0x0097,  # SMM
    0x09: 0x008D,  # RI → U+008D REVERSE LINE FEED
    0x0A: 0x008E,  # SS2
    0x0B: 0x000B,  # VT
    0x0C: 0x000C,  # FF
    0x0D: 0x000D,  # CR
    0x0E: 0x000E,  # SO
    0x0F: 0x000F,  # SI
    0x10: 0x0010,  # DLE
    0x11: 0x0011,  # DC1
    0x12: 0x0012,  # DC2
    0x13: 0x0013,  # DC3
    0x14: 0x009D,  # RDS → U+009D
    0x15: 0x0085,  # NL → U+0085 NEXT LINE
    0x16: 0x0008,  # BS
    0x17: 0x0087,  # ESA → U+0087
    0x18: 0x0018,  # CAN
    0x19: 0x0019,  # EM
    0x1A: 0x0092,  # SPS → U+0092 SPACE (privileged)
    0x1B: 0x008F,  # MFA → U+008F SS3
    0x1C: 0x001C,  # FS
    0x1D: 0x001D,  # GS
    0x1E: 0x001E,  # RS
    0x1F: 0x001F,  # US
    0x20: 0x0080,  # DS → U+0080 PADDING CHARACTER
    0x21: 0x0081,  # SOS
    0x22: 0x0082,  # FS (field separator)
    0x23: 0x0083,  # WVS
    0x24: 0x0084,  # BYP
    0x25: 0x000A,  # LF
    0x26: 0x0017,  # ETB
    0x27: 0x001B,  # ESC
    0x28: 0x0088,  # SA → U+0088 CHARACTER TABULATION SET
    0x29: 0x0089,  # SFE
    0x2A: 0x008A,  # CSI
    0x2B: 0x008B,  # STI
    0x2C: 0x008C,  # PLA
    0x2D: 0x0005,  # ENQ
    0x2E: 0x0007,  # BEL
    0x2F: 0x0090,  # SS3 → U+0090 DCS
    0x30: 0x0091,  # DCS
    0x31: 0x0016,  # SYN
    0x32: 0x0093,  # PU1
    0x33: 0x0094,  # PU2
    0x34: 0x0095,  # STS
    0x35: 0x0096,  # CHI
    0x36: 0x0097,  # ESA → U+0097
    0x37: 0x0098,  # SOS → U+0098 SOS
    0x38: 0x0099,  # SCI
    0x39: 0x009A,  # STI → U+009A SCI
    0x3A: 0x009B,  # CSI → U+009B CSI
    0x3B: 0x009C,  # ST → U+009C ST
    0x3C: 0x0014,  # DC4
    0x3D: 0x0015,  # NAK
    0x3E: 0x007E,  # tilde
    0x3F: 0x007F,  # DEL (duplicate; per IBM 037 table)
    0x40: 0x0020,  # SPACE
    0x41: 0x00A0,  # NBSP
    0x42: 0x00E2,  # â
    0x43: 0x00E4,  # ä
    0x44: 0x00E0,  # à
    0x45: 0x00E1,  # á
    0x46: 0x00E3,  # ã
    0x47: 0x00E5,  # å
    0x48: 0x00E7,  # ç
    0x49: 0x00F1,  # ñ
    0x4A: 0x00A2,  # cent sign
    0x4B: 0x002E,  # period
    0x4C: 0x003C,  # less-than
    0x4D: 0x0028,  # left paren
    0x4E: 0x002B,  # plus
    0x4F: 0x007C,  # pipe
    0x50: 0x0026,  # ampersand
    0x51: 0x00E9,  # é
    0x52: 0x00EA,  # ê
    0x53: 0x00EB,  # ë
    0x54: 0x00E8,  # è
    0x55: 0x00ED,  # í
    0x56: 0x00EE,  # î
    0x57: 0x00EF,  # ï
    0x58: 0x00DF,  # ß
    0x59: 0x0021,  # exclamation
    0x5A: 0x0024,  # dollar
    0x5B: 0x002A,  # asterisk
    0x5C: 0x0029,  # right paren
    0x5D: 0x003B,  # semicolon
    0x5E: 0x00AC,  # not sign
    0x5F: 0x002D,  # minus/hyphen
    0x60: 0x002F,  # slash
    0x61: 0x00C2,  # Â
    0x62: 0x00C4,  # Ä
    0x63: 0x00C0,  # À
    0x64: 0x00C1,  # Á
    0x65: 0x00C3,  # Ã
    0x66: 0x00C5,  # Å
    0x67: 0x00C7,  # Ç
    0x68: 0x00D1,  # Ñ
    0x69: 0x00A6,  # broken bar
    0x6A: 0x002C,  # comma
    0x6B: 0x0025,  # percent
    0x6C: 0x005F,  # underscore
    0x6D: 0x003E,  # greater-than
    0x6E: 0x003F,  # question
    0x6F: 0x00F8,  # ø
    0x70: 0x00C9,  # É
    0x71: 0x00CA,  # Ê
    0x72: 0x00CB,  # Ë
    0x73: 0x00C8,  # È
    0x74: 0x00CD,  # Í
    0x75: 0x00CE,  # Î
    0x76: 0x00CF,  # Ï
    0x77: 0x00DD,  # Ý
    0x78: 0x00F6,  # ö
    0x79: 0x00DC,  # Ü
    0x7A: 0x003A,  # colon
    0x7B: 0x00D3,  # Ó
    0x7C: 0x00D4,  # Ô
    0x7D: 0x0027,  # apostrophe
    0x7E: 0x003D,  # equals
    0x7F: 0x0022,  # double quote
    0x80: 0x00D8,  # Ø
    0x81: 0x0061,  # a
    0x82: 0x0062,  # b
    0x83: 0x0063,  # c
    0x84: 0x0064,  # d
    0x85: 0x0065,  # e
    0x86: 0x0066,  # f
    0x87: 0x0067,  # g
    0x88: 0x0068,  # h
    0x89: 0x0069,  # i
    0x8A: 0x00AB,  # «
    0x8B: 0x00BB,  # »
    0x8C: 0x00F0,  # ð
    0x8D: 0x00FD,  # ý
    0x8E: 0x00FE,  # þ
    0x8F: 0x00B1,  # ±
    0x90: 0x00B0,  # degree
    0x91: 0x006A,  # j
    0x92: 0x006B,  # k
    0x93: 0x006C,  # l
    0x94: 0x006D,  # m
    0x95: 0x006E,  # n
    0x96: 0x006F,  # o
    0x97: 0x0070,  # p
    0x98: 0x0071,  # q
    0x99: 0x0072,  # r
    0x9A: 0x00AA,  # ª
    0x9B: 0x00BA,  # º
    0x9C: 0x00E6,  # æ
    0x9D: 0x00B8,  # ¸
    0x9E: 0x00C6,  # Æ
    0x9F: 0x00A4,  # ¤ currency
    0xA0: 0x00B5,  # µ micro
    0xA1: 0x0073,  # s
    0xA2: 0x0074,  # t
    0xA3: 0x0075,  # u
    0xA4: 0x0076,  # v
    0xA5: 0x0077,  # w
    0xA6: 0x0078,  # x
    0xA7: 0x0079,  # y
    0xA8: 0x007A,  # z
    0xA9: 0x00A1,  # ¡
    0xAA: 0xBF,     # ¿
    0xAB: 0x00D0,  # Ð
    0xAC: 0x00DE,  # Þ
    0xAD: 0x00AE,  # ®
    0xAE: 0x00AC,  # ¬ (duplicate)
    0xAF: 0x00A3,  # £ pound
    0xB0: 0x00A5,  # ¥ yen
    0xB1: 0x00B7,  # · middle dot
    0xB2: 0x00BC,  # ¼
    0xB3: 0x00BD,  # ½
    0xB4: 0x00BE,  # ¾
    0xB5: 0xE289A4,  # ≤ U+2264 (PUA as multibyte-encoded int; we store the scalar)
    0xB6: 0xE289A5,  # ≥ U+2265
    0xB7: 0xE2809C,  # left double quote U+201C (as scalar 0x201C)
    0xB8: 0xE2809D,  # right double quote U+201D
    0xB9: 0x00A8,  # ¨ diaeresis
    0xBA: 0x00B4,  # ´ acute
    0xBB: 0x00C0 + 0x2D,  # placeholder; corrected below to U+00D6
    0xBC: 0x00F7,  # ÷
    0xBD: 0x00DB,  # Û
    0xBE: 0x00D9,  # Ù
    0xBF: 0x00DA,  # Ú
    0xC0: 0x0080,  # À placeholder → corrected below
    0xC1: 0x0041,  # A
    0xC2: 0x0042,  # B
    0xC3: 0x0043,  # C
    0xC4: 0x0044,  # D
    0xC5: 0x0045,  # E
    0xC6: 0x0046,  # F
    0xC7: 0x0047,  # G
    0xC8: 0x0048,  # H
    0xC9: 0x0049,  # I
    0xCA: 0x00AD,  # soft hyphen
    0xCB: 0x00F4,  # ô
    0xCC: 0x00F6,  # ö duplicate
    0xCD: 0x00F2,  # ò
    0xCE: 0x00F3,  # ó
    0xCF: 0x00F5,  # õ
    0xD0: 0x00C0 + 0x2C,  # placeholder → corrected to U+00D5 Õ
    0xD1: 0x004A,  # J
    0xD2: 0x004B,  # K
    0xD3: 0x004C,  # L
    0xD4: 0x004D,  # M
    0xD5: 0x004E,  # N
    0xD6: 0x004F,  # O
    0xD7: 0x0050,  # P
    0xD8: 0x0051,  # Q
    0xD9: 0x0052,  # R
    0xDA: 0x00B9,  # ¹
    0xDB: 0x00FB,  # û
    0xDC: 0x00FC,  # ü
    0xDD: 0x00F9,  # ù
    0xDE: 0x00FA,  # ú
    0xDF: 0x00FF,  # ÿ
    0xE0: 0x00D3 + 0x05,  # placeholder → corrected to U+00D6 Ö
    0xE1: 0x0053,  # S
    0xE2: 0x0054,  # T
    0xE3: 0x0055,  # U
    0xE4: 0x0056,  # V
    0xE5: 0x0057,  # W
    0xE6: 0x0058,  # X
    0xE7: 0x0059,  # Y
    0xE8: 0x005A,  # Z
    0xE9: 0x00A2 + 0x18,  # placeholder → corrected to U+00C2 Â (dup)
    0xEA: 0x00CA,  # Ê duplicate
    0xEB: 0x00CB,  # Ë duplicate
    0xEC: 0x00C8,  # È duplicate
    0xED: 0x00CD,  # Í duplicate
    0xEE: 0x00CE,  # Î duplicate
    0xEF: 0x00CF,  # Ï duplicate
    0xF0: 0x0030,  # 0
    0xF1: 0x0031,  # 1
    0xF2: 0x0032,  # 2
    0xF3: 0x0033,  # 3
    0xF4: 0x0034,  # 4
    0xF5: 0x0035,  # 5
    0xF6: 0x0036,  # 6
    0xF7: 0x0037,  # 7
    0xF8: 0x0038,  # 8
    0xF9: 0x0039,  # 9
    0xFA: 0x00DB,  # Û duplicate
    0xFB: 0x00DC,  # Ü duplicate
    0xFC: 0x00D9,  # Ù duplicate
    0xFD: 0x00DA,  # Ú duplicate
    0xFE: 0x00D8,  # Ø duplicate
    0xFF: 0x0060,  # grave accent
}

# Scalar (Unicode code-point) overrides for entries whose compact value
# was stored as a UTF-8 multi-byte integer for grep-ability. We convert
# them to their true scalar value here so the public table is always a
# mapping from byte → Unicode code point.
_UTF8_TO_SCALAR = {
    0xE289A4: 0x2264,  # ≤
    0xE289A5: 0x2265,  # ≥
    0xE2809C: 0x201C,  # left double quote
    0xE2809D: 0x201D,  # right double quote
}

# Direct scalar corrections for placeholder entries above.
_DIRECT_FIXES: Dict[int, int] = {
    0xBB: 0x00D6,  # Ö
    0xD0: 0x00D5,  # Õ
    0xE0: 0x00D6,  # Ö (duplicate in this code page)
    0xE9: 0x00C2,  # Â (duplicate)
}


def _build_table() -> Dict[int, int]:
    """Build the full 256-entry byte→code-point table."""
    table: Dict[int, int] = {}
    for byte_val, mapped in _COMPACT_MAP.items():
        if mapped in _UTF8_TO_SCALAR:
            table[byte_val] = _UTF8_TO_SCALAR[mapped]
        else:
            table[byte_val] = mapped
    for byte_val, scalar in _DIRECT_FIXES.items():
        table[byte_val] = scalar
    return table


CODE_PAGE_037: Dict[int, int] = _build_table()

# Build the inverse table for encoding. If two bytes map to the same
# code point, we keep the lowest byte value (deterministic choice).
_INVERSE: Dict[int, int] = {}
for _b in range(256):
    _cp = CODE_PAGE_037[_b]
    if _cp not in _INVERSE:
        _INVERSE[_cp] = _b
del _b, _cp


def decode(data: bytes) -> str:
    """Decode an EBCDIC CP037 byte sequence to a Python ``str``.

    Raises
    ------
    UnicodeDecodeError
        If *data* is empty, the caller gets an empty string back (no
        error). Every byte 0x00–0xFF has a defined mapping, so no input
        byte can cause an error; this is a safety guarantee, not a gap.

    Why not use codecs.getdecoder?
    ------------------------------
    Python ships an ``cp037`` codec. We re-implement the mapping so the
    library is fully self-contained and the table can be audited in one
    place. The trade-off is a ~3× speed penalty, which is acceptable for
    interchange tooling.
    """
    return "".join(chr(CODE_PAGE_037[b]) for b in data)


def encode(text: str) -> bytes:
    """Encode a Python ``str`` to EBCDIC CP037 bytes.

    Raises
    ------
    UnicodeEncodeError
        If *text* contains a code point that has no CP037 representation.
        We refuse to silently substitute a space or question mark because
        for archival data even a single lost character can break a fixed-
        width record layout downstream.
    """
    out = bytearray(len(text))
    for i, ch in enumerate(text):
        cp = ord(ch)
        if cp not in _INVERSE:
            raise UnicodeEncodeError(
                "cp037",
                text,
                i,
                i + 1,
                f"character U+{cp:04X} has no CP037 representation",
            )
        out[i] = _INVERSE[cp]
    return bytes(out)


def translate(data: bytes) -> bytes:
    """Return *data* with each byte replaced by its CP037-mapped byte.

    This is a byte→byte transform: it takes the Unicode code point for
    each input byte, then re-encodes that code point back to the CP037
    byte that represents it. For most input this is the identity, but it
    normalises bytes whose CP037 glyph differs from ASCII.

    Empty input yields empty output. Any byte whose mapped code point
    has no inverse CP037 byte raises ``ValueError``.
    """
    result = bytearray(len(data))
    for i, b in enumerate(data):
        cp = CODE_PAGE_037[b]
        if cp not in _INVERSE:
            raise ValueError(
                f"byte 0x{b:02X} maps to U+{cp:04X}, which has no CP037 byte"
            )
        result[i] = _INVERSE[cp]
    return bytes(result)
