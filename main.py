#!/usr/bin/env python3
"""news-image-20261118: emit the 18 November 2026 news image.

The finished artwork ships inside this repository as assets/entry.png
(it was drawn at build time by tools/make_image.py from the stories
reported on Wednesday 18 November 2026). This program only copies it,
byte for byte, to the grader's output file. It touches no network, reads
no clock and rolls no dice, so two runs write identical bytes.

Where the file goes: $MAKEFUN_OUTPUT_DIR first, then
$ENTRY_OUTPUT_DIR, then /output.
"""

import hashlib
import os
import sys
import zlib

HERE = os.path.dirname(os.path.realpath(__file__))
BUNDLED = os.path.join(HERE, "assets", "entry.png")
ONE_MIB = 1024 * 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


class BadImage(Exception):
    """The bundled artwork failed a structural check."""


def _u32be(buf, off):
    return int.from_bytes(buf[off:off + 4], "big")


def _chunks(blob):
    """Yield (kind, data) for every chunk of a PNG byte string."""
    if blob[:8] != SIGNATURE:
        raise BadImage("not a PNG (bad signature)")
    pos = 8
    while pos < len(blob):
        if pos + 8 > len(blob):
            raise BadImage("truncated chunk header")
        size = _u32be(blob, pos)
        kind = blob[pos + 4:pos + 8]
        end = pos + 8 + size + 4
        if end > len(blob):
            raise BadImage("truncated %s chunk" % kind.decode("latin1"))
        data = blob[pos + 8:pos + 8 + size]
        want = zlib.crc32(kind + data) & 0xFFFFFFFF
        if _u32be(blob, pos + 8 + size) != want:
            raise BadImage("CRC mismatch in %s chunk" % kind.decode("latin1"))
        yield kind, data
        pos = end
        if kind == b"IEND":
            break
    else:
        raise BadImage("no IEND chunk found")
    if pos != len(blob):
        raise BadImage("bytes after IEND")


def inspect(blob):
    """Validate the bundled PNG end to end and return its dimensions."""
    if len(blob) > ONE_MIB:
        raise BadImage("image is %d bytes, over the 1 MiB cap" % len(blob))
    width = height = None
    idat = bytearray()
    seen_iend = False
    for kind, data in _chunks(blob):
        if kind == b"IHDR":
            width = _u32be(data, 0)
            height = _u32be(data, 4)
            if (width, height) != (1024, 1024):
                raise BadImage("image is %dx%d, want 1024x1024"
                               % (width, height))
            if data[8] != 8 or data[9] != 2:
                raise BadImage("want 8-bit RGB colour, got depth %d type %d"
                               % (data[8], data[9]))
            if data[12] != 0:
                raise BadImage("interlaced PNGs are not accepted here")
        elif kind == b"IDAT":
            idat += data
        elif kind == b"IEND":
            seen_iend = True
    if width is None:
        raise BadImage("no IHDR chunk")
    if not seen_iend:
        raise BadImage("no IEND chunk")
    # The pixel data itself must inflate to exactly one scanline filter
    # byte + 3 bytes per pixel, for all 1024 rows.
    raw = zlib.decompress(bytes(idat))
    if len(raw) != 1024 * (1 + 1024 * 3):
        raise BadImage("IDAT inflates to %d bytes, want %d"
                       % (len(raw), 1024 * (1 + 1024 * 3)))
    return width, height


def out_dir():
    for var in ("MAKEFUN_OUTPUT_DIR", "ENTRY_OUTPUT_DIR"):
        value = os.environ.get(var)
        if value:
            return value
    return "/output"


def main():
    with open(BUNDLED, "rb") as handle:
        blob = handle.read()
    inspect(blob)
    folder = out_dir()
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "entry.png")
    with open(target, "wb") as handle:
        handle.write(blob)
    print("wrote %s (%d bytes)" % (target, len(blob)))
    print("sha256 %s" % hashlib.sha256(blob).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
