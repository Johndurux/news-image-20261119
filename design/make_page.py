#!/usr/bin/env python3
"""Draw the front page that sums up Thursday 19 November 2026.

The entry is one editorial front page rather than a pile of pictures: the date
is the largest thing on it, the lead story takes the top half, four more
stories sit under it, and a three-line strip closes the page.  Everything the
page states is in the LEAD / TILES / TICKER tables below, so refreshing the
day's news is an edit to those tables and a rerun of this script; nothing is
drawn that is not written down there.

Every fact was taken from reporting dated 19 November 2026:

  Shenzhen   the first three-way Trump/Putin/Xi meeting, after their
             bilateral talks on Ukraine, Iran and trade
  Berlin     Merz hosts the Coalition of the Willing on Ukraine's defence
  Riyadh     the Houthis claim cruise-missile hits on the airport and the
             financial centre
  Odisha     Cyclone Akvan: over 100,000 evacuated, landfall due on Friday
  Nasdaq     Anthropic's shares begin trading as "ANT" after an $81bn offering
  Worldwide  Grand Theft Auto VI is released
  Lagos      the state police bill reaches President Tinubu
  Bogota     Colombia to seek Congress approval for joint US military operations

Run this script (it needs Pillow and the Liberation and DejaVu fonts) and it
writes ./entry.png -- the file main.py copies into the sandbox as the entry.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFont

W = 1024
S = 2  # shapes are drawn at twice the size and scaled down, so edges stay clean

PAPER = (244, 240, 231)
INK = (26, 22, 18)
RED = (163, 30, 26)
MUTED = (76, 68, 60)
GREY = (196, 189, 177)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

MASTHEAD = "THE WORLD TODAY"
EDITION = "THURSDAY 19 NOVEMBER 2026"
STANDFIRST = "WORLD EDITION \u00b7 ONE DAY, ONE PAGE"

LEAD = {
    "kicker": "SHENZHEN, CHINA \u00b7 APEC SUMMIT",
    "headline": ["THREE POWERS,", "ONE TABLE"],
    "deck": "Trump, Putin and Xi meet at one table for the first time, in Shenzhen.",
}

# kicker, headline, the one factual line under it, pictogram
TILES = [
    (
        "BERLIN \u00b7 UKRAINE",
        "Allies pledge Kyiv's defence",
        "Merz hosts the Coalition of the Willing; US envoys meet "
        "Europe's new negotiating team.",
        "shield",
    ),
    (
        "RIYADH \u00b7 YEMEN",
        "Houthis claim Riyadh attack",
        "The group says cruise missiles hit the airport and the "
        "financial centre.",
        "strike",
    ),
    (
        "ODISHA, INDIA \u00b7 STORM",
        "Cyclone Akvan: 100,000 flee",
        "Red alert in 13 districts; landfall near Gopalpur "
        "is due on Friday.",
        "cyclone",
    ),
    (
        "NASDAQ \u00b7 MARKETS",
        "Anthropic's $81bn debut",
        "The AI group's shares are to trade as \u201cANT\u201d after "
        "the largest offering on record.",
        "chart",
    ),
]

# the three-line strip at the foot: places and fields the tiles have no room for
TICKER = [
    ("GTA VI", "Out worldwide after 13 years, with $1.5bn pre-ordered."),
    ("LAGOS", "States win their own police as the bill reaches Tinubu."),
    ("BOGOT\u00c1", "Colombia to seek joint US military operations."),
]

MARGIN = 46
COL_W = 448
GUTTER = 24
TILE_TOP = 610
TILE_STEP = 166
ICON = 80
TEXT_X = 116
HEAD_SIZE = 26


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text(draw, xy, s, f, fill=INK, anchor="la", spacing=0):
    """Draw a string, optionally letter-spaced (spacing in pixels)."""
    if not spacing:
        draw.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    x, y = xy
    if anchor[0] == "m":
        x -= (sum(f.getlength(c) for c in s) + spacing * (len(s) - 1)) / 2
    for c in s:
        draw.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(c) + spacing


def wrap(s: str, f, width: float) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and f.getlength(trial) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def block(draw, xy, s, f, width, lead, fill=INK):
    """Wrap a paragraph to `width` and draw it with `lead` line height."""
    x, y = xy
    for i, line in enumerate(wrap(s, f, width)):
        draw.text((x, y + i * lead), line, font=f, fill=fill)
    return y + len(wrap(s, f, width)) * lead


# ---------------------------------------------------------------- pictograms


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def disc_flag(base: Image.Image, cx, cy, r, which):
    """A round flag badge: a simplified national flag, clipped to a circle."""
    n = int(math.ceil(2 * r))
    flag = Image.new("RGB", (n, n), (250, 248, 244))
    fd = ImageDraw.Draw(flag)

    if which == "us":
        for i in range(7):
            if i % 2 == 0:
                fd.rectangle([0, i * n / 7, n, (i + 1) * n / 7], fill=(178, 34, 52))
        fd.rectangle([0, 0, n * 0.45, n * 0.5], fill=(38, 58, 110))
        for i in range(3):
            for j in range(3):
                sx, sy = n * (0.08 + j * 0.14), n * (0.09 + i * 0.15)
                fd.ellipse([sx - n * 0.02, sy - n * 0.02, sx + n * 0.02, sy + n * 0.02],
                           fill=(250, 248, 244))
    elif which == "ru":
        fd.rectangle([0, 0, n, n / 3], fill=(250, 248, 244))
        fd.rectangle([0, n / 3, n, 2 * n / 3], fill=(38, 58, 110))
        fd.rectangle([0, 2 * n / 3, n, n], fill=(178, 34, 52))
    else:  # cn
        fd.rectangle([0, 0, n, n], fill=(178, 34, 52))
        star(fd, n * 0.3, n * 0.3, n * 0.22, (248, 214, 96))

    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    base.paste(flag, (int(cx - r), int(cy - r)), mask)
    ImageDraw.Draw(base).ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2 * S)


def table_motif(base: Image.Image):
    """Three flags at one table: the summit, drawn rather than photographed."""
    s = S

    def box(x0, y0, x1, y1):
        return [x0 * s, y0 * s, x1 * s, y1 * s]

    d = ImageDraw.Draw(base)
    for x in (300, 700):  # table legs
        d.rectangle(box(x, 548, x + 14, 580), fill=INK)
    d.rectangle(box(262, 520, 762, 550), fill=INK)  # table top
    d.rectangle(box(250, 514, 774, 522), fill=GREY)  # its far edge, catching the light
    for x in (362, 512, 662):  # place settings, one under each flag
        d.rectangle(box(x - 34, 532, x + 34, 538), fill=PAPER)
    for x, which in ((362, "us"), (512, "ru"), (662, "cn")):
        disc_flag(base, x * s, 470 * s, 40 * s, which)


def icon(draw, x, y, size, kind):
    """Draw one pictogram inside the square (x, y, size)."""
    if kind == "shield":
        w = size
        pts = [(x + w * 0.5, y), (x + w, y + w * 0.12), (x + w, y + w * 0.5),
               (x + w * 0.5, y + w), (x, y + w * 0.5), (x, y + w * 0.12)]
        draw.polygon(pts, outline=INK, width=3 * S)
        star(draw, x + w * 0.5, y + w * 0.48, w * 0.3, RED)
    elif kind == "strike":
        # a skyline, a red burst over it and a dashed missile path coming in
        for i, h in enumerate((0.34, 0.58, 0.44, 0.78)):
            bx = x + size * (0.06 + i * 0.24)
            draw.rectangle([bx, y + size * (1 - h), bx + size * 0.17, y + size], fill=INK)
        for t in range(9):
            t0, t1 = t / 9, (t + 0.6) / 9
            draw.line([(x + size * (0.02 + 0.5 * t0), y + size * (0.16 - 0.1 * t0)),
                       (x + size * (0.02 + 0.5 * t1), y + size * (0.16 - 0.1 * t1))],
                      fill=RED, width=3 * S)
        star(draw, x + size * 0.56, y + size * 0.12, size * 0.16, RED)
    elif kind == "cyclone":
        cx, cy = x + size * 0.5, y + size * 0.46
        for arm in (0, math.pi):
            pts = []
            for step in range(96):
                t = step / 95 * 2.6 * math.pi
                rad = size * (0.06 + 0.19 * t / (2.6 * math.pi))
                ang = arm + t
                pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
            draw.line(pts, fill=INK, width=3 * S, joint="curve")
        draw.ellipse([cx - size * 0.05, cy - size * 0.05, cx + size * 0.05, cy + size * 0.05],
                     fill=RED)
        for i in range(3):  # sea, hatched under the storm
            yy = y + size * (0.86 + i * 0.05)
            draw.line([(x + size * 0.08, yy), (x + size * 0.42, yy)], fill=RED, width=2 * S)
            draw.line([(x + size * 0.52, yy), (x + size * 0.92, yy)], fill=GREY, width=2 * S)
    elif kind == "chart":
        for i, h in enumerate((0.26, 0.44, 0.63, 0.86)):
            bx = x + size * (0.06 + i * 0.24)
            draw.rectangle([bx, y + size * (1 - h), bx + size * 0.16, y + size],
                           fill=RED if i == 3 else INK)
        draw.line([(x + size * 0.05, y + size * 0.8), (x + size * 0.95, y + size * 0.12)],
                  fill=GREY, width=2 * S)


# ------------------------------------------------------------------- page


def tile_pos(idx: int) -> tuple[float, float]:
    """Where tile `idx` starts, on the two-column grid."""
    return MARGIN + (idx % 2) * (COL_W + GUTTER), TILE_TOP + (idx // 2) * TILE_STEP


def draw_page() -> Image.Image:
    shapes = Image.new("RGB", (W * S, W * S), PAPER)
    sd = ImageDraw.Draw(shapes)
    table_motif(shapes)
    for idx, (_label, _headline, _line, kind) in enumerate(TILES):
        tx, ty = tile_pos(idx)
        icon(sd, (tx + 8) * S, (ty - 2) * S, ICON * S, kind)

    page = shapes.resize((W, W), Image.LANCZOS)
    d = ImageDraw.Draw(page)

    # masthead and the date band: the day is the largest thing on the page
    text(d, (W / 2, 30), MASTHEAD, font(SERIF_BOLD, 58), spacing=4, anchor="ma")
    d.line([(MARGIN, 104), (W - MARGIN, 104)], fill=INK, width=2)
    d.rectangle([MARGIN, 112, W - MARGIN, 170], fill=INK)
    text(d, (W / 2, 128), EDITION, font(SANS_BOLD, 30), fill=PAPER, spacing=3, anchor="ma")
    text(d, (W - MARGIN - 4, 178), STANDFIRST, font(SANS, 13), fill=MUTED, anchor="ra")

    # the lead story
    text(d, (MARGIN, 192), LEAD["kicker"], font(SANS_BOLD, 15), fill=RED, spacing=3)
    y = 216
    for line in LEAD["headline"]:
        d.text((MARGIN, y), line, font=font(SERIF_BOLD, 74), fill=INK)
        y += 76
    block(d, (MARGIN, y + 18), LEAD["deck"], font(SERIF, 24), W - 2 * MARGIN, 28, MUTED)

    # rules: double under the lead, then the grid the four stories sit on
    d.line([(MARGIN, 592), (W - MARGIN, 592)], fill=INK, width=1)
    d.line([(MARGIN, 596), (W - MARGIN, 596)], fill=INK, width=3)
    d.line([(MARGIN + COL_W + GUTTER / 2, 608), (MARGIN + COL_W + GUTTER / 2, 890)],
           fill=GREY, width=1)
    d.line([(MARGIN, 744), (W - MARGIN, 744)], fill=GREY, width=1)

    for idx, (label, headline, line, _kind) in enumerate(TILES):
        tx, ty = tile_pos(idx)
        text(d, (tx + TEXT_X, ty), label, font(SANS_BOLD, 12), fill=RED, spacing=2)
        head_font = font(SERIF_BOLD, HEAD_SIZE)
        if head_font.getlength(headline) > COL_W - 120:
            raise ValueError(f"headline is too wide for its column: {headline!r}")
        d.text((tx + TEXT_X, ty + 20), headline, font=head_font, fill=INK)
        block(d, (tx + TEXT_X, ty + 60), line, font(SERIF, 18), COL_W - 126, 22, MUTED)

    # the strip at the foot
    strip = (W - 2 * MARGIN) / 3
    d.line([(MARGIN, 908), (W - MARGIN, 908)], fill=INK, width=1)
    for idx, (label, line) in enumerate(TICKER):
        tx = MARGIN + idx * strip
        if idx:
            d.line([(tx - 16, 924), (tx - 16, 1000)], fill=GREY, width=1)
        text(d, (tx, 930), label, font(SANS_BOLD, 12), fill=RED, spacing=2)
        block(d, (tx, 948), line, font(SERIF, 17), strip - 24, 20, INK)

    return page


def main() -> None:
    page = draw_page()
    page.save("entry.png", optimize=True)
    print(f"wrote entry.png ({page.width}x{page.height})")


if __name__ == "__main__":
    main()
