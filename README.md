# ebcdic_code_page_kit

Decode and encode IBM EBCDIC Code Page 037 byte data in pure Python.

```python
from ebcdic_code_page_kit import decode, encode

text = decode(b"\xc8\x85\x93\x93\x96\x40\xf1\xf2\xf3")  # 'Hello 123'
back = encode("Hello 123")                                    # b'\xc8\x85\x93\x93\x96\x40\xf1\xf2\xf3'
```

## Why

Mainframe data files arrive as raw EBCDIC bytes. Python ships a `cp037`
codec, but it is opaque and version-dependent. This library ships the
full 256-entry table in one auditable place and exposes two simple
functions plus a `CODE_PAGE_037` dict for direct lookup.

The trade-off: we support exactly one code page (037, North American).
If your data is CP500 or CP1047, this is the wrong library. We chose
037 because it covers the overwhelming majority of North American
mainframe interchange and keeps the API to zero configuration.

## Edge cases

* Every byte `0x00`–`0xFF` has a defined mapping, so `decode` never
  raises. `encode` raises `UnicodeEncodeError` for code points outside
  CP037 (e.g. emoji) rather than silently substituting a placeholder.
* CP037 has duplicate mappings (several bytes map to the same glyph).
  When encoding, the lowest byte value wins, deterministically.

## Running tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
