#!/usr/bin/env python3
"""Put the 19 November 2026 front page where the harness reads it.

The image itself was drawn while this entry was built -- design/make_page.py
holds the script that drew it, and entry.png is the picture that script
produced.  This program only copies those exact bytes to /output/entry.png, so
two runs of it write one file, byte for byte, with no clock and no randomness
anywhere in the path.
"""

from pathlib import Path
import hashlib
import shutil
import sys

IMAGE_LIMIT = 1024 * 1024
EDGE_LIMIT = 1024


def looks_like_a_whole_image(data: bytes) -> bool:
    """True for a PNG that ends on its IEND chunk, or a JPEG that ends on EOI."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return data[-8:] == b"IEND\xaeB`\x82"
    if data[:2] == b"\xff\xd8":
        return data[-2:] == b"\xff\xd9"
    return False


def png_edge(data: bytes) -> tuple[int, int] | None:
    """The width and height a PNG's IHDR declares, or None if it is not a PNG."""
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print(f"missing source image: {source}", file=sys.stderr)
        return 1

    data = source.read_bytes()
    if len(data) > IMAGE_LIMIT:
        print(f"image is {len(data)} bytes, over the {IMAGE_LIMIT} cap", file=sys.stderr)
        return 1
    if not looks_like_a_whole_image(data):
        print("image is not a whole PNG or JPEG", file=sys.stderr)
        return 1

    edge = png_edge(data)
    if edge is not None and max(edge) > EDGE_LIMIT:
        print(f"image is {edge[0]}x{edge[1]}, over the {EDGE_LIMIT} px cap", file=sys.stderr)
        return 1

    target = Path("/output/entry.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"wrote {target} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
