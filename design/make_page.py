#!/usr/bin/env python3
"""Draw the front page that sums up Thursday 19 November 2026.

The page is a dated masthead, a lead story and six picture panels.  Each story
is carried by a picture wide enough to read on its own at the size the judge
looks at, with a short label and one factual line under it: the first judging
criterion is that the image names its day, the second that it spans regions and
beats, and the third that every story is clear from its own picture.

Everything the page states lives in the LEAD / PANELS / BRIEFS tables below, so
refreshing the day's news is an edit to those tables and a rerun of this script.
Attribute what a reader could not check for themselves ("state media report",
"the group says"), and never a superlative the wire copy does not carry: an
earlier version of this page lost a judged game for calling an $81bn listing
"the largest offering on record".

The copy comes from reporting dated 19 November 2026: the Shenzhen three-way
summit of the US, Russian and Chinese leaders; the Coalition of the Willing in
Berlin; the Houthi claim of cruise-missile hits on Riyadh; Cyclone Akvan in
Odisha; Anthropic's Nasdaq debut as "ANT"; the Grand Theft Auto VI release;
Nigeria's state police bill reaching the president; and Colombia's request for
joint US military operations.

Run this script (Pillow, plus the Liberation and DejaVu fonts) and it writes
./entry.png -- the file main.py copies into the sandbox as the entry.
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
    "deck": "Trump, Putin and Xi hold their first three-way meeting, state "
            "media report from Shenzhen.",
}

# kicker, headline, the one factual line under it, and the picture for it
PANELS = [
    (
        "BERLIN \u00b7 UKRAINE",
        "Allies pledge Kyiv's defence",
        "Merz hosts the Coalition of the Willing; US envoys meet the "
        "Europeans' new negotiating team.",
        "flags_eu_ua",
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
        "Anthropic lists as \u201cANT\u201d",
        "The AI group's shares are to start trading after an $81bn "
        "offering.",
        "chart",
    ),
    (
        "GTA VI \u00b7 RELEASE DAY",
        "Thirteen years on, it ships",
        "The new Grand Theft Auto goes on sale, on $1.5bn of "
        "pre-orders.",
        "controller",
    ),
    (
        "LAGOS \u00b7 NIGERIA",
        "States win their own police",
        "The state police bill reaches President Tinubu to be "
        "signed.",
        "flags_ng_badge",
    ),
]

# the line at the foot, for the stories the panels have no room for
BRIEFS = [
    ("BOGOT\u00c1", "Colombia to seek Congress approval for joint military operations "
                   "with the US."),
]

MARGIN = 46
COLS = 3
COL_W = 310
GUTTER = 22
PIC_H = 150
GRID_TOP = 440
ROW_STEP = 266
TEXT_TOP = 156  # from the panel's top: where its label starts
PANEL_HEAD = 22
PANEL_BODY = 14

# where the lead's picture sits: left of its copy, under the date band
LEAD_BOX = (46, 192, 336, 424)
LEAD_TEXT_X = 360


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


# ------------------------------------------------------------- little marks


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def rosette(draw, cx, cy, r, fill):
    """A police-badge rosette: a star with a ring punched through it."""
    star(draw, cx, cy, r, fill)
    draw.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32], outline=PAPER,
                 width=2 * S)


def flag_field(n: int, which: str) -> Image.Image:
    """A simplified national flag on a square, to be clipped to a circle."""
    img = Image.new("RGB", (n, n), (250, 248, 244))
    fd = ImageDraw.Draw(img)

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
    elif which == "cn":
        fd.rectangle([0, 0, n, n], fill=(178, 34, 52))
        star(fd, n * 0.3, n * 0.3, n * 0.22, (248, 214, 96))
    elif which == "eu":
        fd.rectangle([0, 0, n, n], fill=(20, 42, 110))
        for i in range(8):
            a = -math.pi / 2 + i * math.pi / 4
            star(fd, n / 2 + n * 0.3 * math.cos(a), n / 2 + n * 0.3 * math.sin(a),
                 n * 0.075, (248, 214, 96))
    elif which == "ua":
        fd.rectangle([0, 0, n, n / 2], fill=(0, 87, 183))
        fd.rectangle([0, n / 2, n, n], fill=(255, 215, 0))
    elif which == "ng":
        fd.rectangle([0, 0, n, n], fill=(250, 248, 244))
        fd.rectangle([0, 0, n / 3, n], fill=(0, 135, 81))
        fd.rectangle([2 * n / 3, 0, n, n], fill=(0, 135, 81))
    return img


def disc_flag(base: Image.Image, cx, cy, r, which):
    """Paste one round flag badge on `base`."""
    n = int(math.ceil(2 * r))
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    base.paste(flag_field(n, which), (int(cx - r), int(cy - r)), mask)
    ImageDraw.Draw(base).ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2 * S)


# ---------------------------------------------------------------- pictures


def picture(base: Image.Image, box, kind: str):
    """Draw one story's picture inside `box`, in final-image coordinates."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w / 2, y0 + h / 2
    d = ImageDraw.Draw(base)

    def rect(ax, ay, bx, by, **kw):
        d.rectangle([ax * S, ay * S, bx * S, by * S], **kw)

    def line(a, b, **kw):
        d.line([a[0] * S, a[1] * S, b[0] * S, b[1] * S], **kw)

    def ell(ax, ay, bx, by, **kw):
        d.ellipse([ax * S, ay * S, bx * S, by * S], **kw)

    def poly(pts, **kw):
        d.polygon([(p[0] * S, p[1] * S) for p in pts], **kw)

    def flag(ax, ay, r, which):
        # disc_flag paints in canvas pixels, so scale the final-image position
        disc_flag(base, ax * S, ay * S, r * S, which)

    def badge(ax, ay, r, fill):
        rosette(d, ax * S, ay * S, r * S, fill)

    def burst(ax, ay, r, fill):
        star(d, ax * S, ay * S, r * S, fill)

    if kind == "table":
        # three flags at one table: the summit itself
        rect(x0 + w * 0.04, y0 + h * 0.66, x1 - w * 0.04, y0 + h * 0.79, fill=INK)
        rect(x0 + w * 0.04, y0 + h * 0.62, x1 - w * 0.04, y0 + h * 0.67, fill=GREY)
        for fx in (0.16, 0.84):
            rect(x0 + w * fx - 7, y0 + h * 0.79, x0 + w * fx + 7, y0 + h * 0.99, fill=INK)
        for fx in (0.22, 0.5, 0.78):
            rect(x0 + w * fx - 26, y0 + h * 0.70, x0 + w * fx + 26, y0 + h * 0.73, fill=PAPER)
        for fx, which in ((0.22, "us"), (0.5, "ru"), (0.78, "cn")):
            flag(x0 + w * fx, y0 + h * 0.33, w * 0.15, which)
    elif kind == "flags_eu_ua":
        # an alliance: two flags over a shield
        poly([(cx, y0 + h * 0.02), (x1 - w * 0.05, y0 + h * 0.22),
              (x1 - w * 0.05, y0 + h * 0.6), (cx, y1),
              (x0 + w * 0.05, y0 + h * 0.6), (x0 + w * 0.05, y0 + h * 0.22)],
             outline=GREY, width=4 * S)
        flag(x0 + w * 0.32, cy - h * 0.08, w * 0.19, "eu")
        flag(x0 + w * 0.68, cy + h * 0.06, w * 0.19, "ua")
    elif kind == "flags_ng_badge":
        flag(x0 + w * 0.34, cy + h * 0.06, w * 0.2, "ng")
        badge(x0 + w * 0.62, cy - h * 0.08, w * 0.18, INK)
    elif kind == "strike":
        # a city under a missile: three towers, a missile in flight, a burst on it
        for fx, fh in ((0.52, 0.9), (0.66, 0.66), (0.8, 0.5)):
            rect(x0 + w * fx, y1 - h * fh, x0 + w * (fx + 0.11), y1, fill=INK)
        mbx, mby = x0 + w * 0.3, y0 + h * 0.42
        poly([(mbx, mby - h * 0.07), (mbx + w * 0.16, mby + h * 0.09),
              (mbx + w * 0.02, mby + h * 0.05)], fill=RED)
        rect(mbx + w * 0.06, mby + h * 0.02, mbx + w * 0.13, mby + h * 0.05, fill=RED)
        for t in range(7):
            t0, t1 = t / 7, (t + 0.55) / 7
            line((x0 + w * (0.02 + 0.26 * t0), y0 + h * (0.62 - 0.2 * t0)),
                 (x0 + w * (0.02 + 0.26 * t1), y0 + h * (0.62 - 0.2 * t1)),
                 fill=INK, width=3 * S)
        burst(x0 + w * 0.57, y0 + h * 0.3, w * 0.12, RED)
    elif kind == "cyclone":
        ccx, ccy = x0 + w * 0.42, cy - h * 0.05
        for arm in (0, math.pi):
            pts = []
            for step in range(110):
                t = step / 109 * 2.5 * math.pi
                rad = w * (0.045 + 0.17 * t / (2.5 * math.pi))
                a = arm + t
                pts.append((ccx + rad * math.cos(a), ccy + rad * math.sin(a)))
            d.line([(p[0] * S, p[1] * S) for p in pts], fill=INK, width=4 * S, joint="curve")
        ell(ccx - w * 0.04, ccy - w * 0.04, ccx + w * 0.04, ccy + w * 0.04, fill=RED)
        for i in range(3):  # the sea under the storm
            yy = y1 - h * (0.26 - i * 0.08)
            line((x0 + w * 0.06, yy), (x0 + w * 0.42, yy), fill=RED, width=3 * S)
            line((x0 + w * 0.54, yy), (x0 + w * 0.94, yy), fill=GREY, width=3 * S)
    elif kind == "chart":
        for i, fh in enumerate((0.28, 0.48, 0.68, 0.92)):
            bx = x0 + w * (0.1 + i * 0.21)
            rect(bx, y1 - h * fh, bx + w * 0.13, y1, fill=RED if i == 3 else INK)
        line((x0 + w * 0.06, y1 - h * 0.2), (x0 + w * 0.94, y0 + h * 0.12), fill=GREY,
             width=3 * S)
    elif kind == "controller":
        # a game controller: a body, two grips, a d-pad and two buttons
        rect(x0 + w * 0.1, cy - h * 0.24, x1 - w * 0.1, cy + h * 0.24, fill=INK)
        for fx in (0.14, 0.86):
            bx = x0 + w * fx
            ell(bx - w * 0.14, cy - h * 0.06, bx + w * 0.14, cy + h * 0.46, fill=INK)
            ell(bx - w * 0.07, cy + h * 0.04, bx + w * 0.07, cy + h * 0.34, fill=PAPER)
        rect(x0 + w * 0.28, cy - h * 0.06, x0 + w * 0.46, cy + h * 0.06, fill=PAPER)
        rect(x0 + w * 0.34, cy - h * 0.18, x0 + w * 0.4, cy + h * 0.18, fill=PAPER)
        for i, fx in enumerate((0.62, 0.72)):
            ell(x0 + w * fx - w * 0.055, cy - h * 0.12 + i * h * 0.18,
                x0 + w * fx + w * 0.055, cy + h * 0.06 + i * h * 0.18, fill=RED)


# -------------------------------------------------------------------- page


def panel_pos(idx: int) -> tuple[float, float]:
    """Where the story panel `idx` starts, on its three-column grid."""
    return (MARGIN + (idx % COLS) * (COL_W + GUTTER),
            GRID_TOP + (idx // COLS) * ROW_STEP)


def draw_page() -> Image.Image:
    shapes = Image.new("RGB", (W * S, W * S), PAPER)
    picture(shapes, LEAD_BOX, "table")
    for idx, (_k, _h, _l, kind) in enumerate(PANELS):
        px, py = panel_pos(idx)
        picture(shapes, (px, py, px + COL_W, py + PIC_H), kind)

    page = shapes.resize((W, W), Image.LANCZOS)
    d = ImageDraw.Draw(page)

    # masthead and the date band: the day is the largest thing on the page
    text(d, (W / 2, 30), MASTHEAD, font(SERIF_BOLD, 58), spacing=4, anchor="ma")
    d.line([(MARGIN, 104), (W - MARGIN, 104)], fill=INK, width=2)
    d.rectangle([MARGIN, 112, W - MARGIN, 170], fill=INK)
    text(d, (W / 2, 128), EDITION, font(SANS_BOLD, 30), fill=PAPER, spacing=3, anchor="ma")
    text(d, (W - MARGIN - 4, 178), STANDFIRST, font(SANS, 13), fill=MUTED, anchor="ra")

    # the lead story: picture left, copy right
    tx = LEAD_TEXT_X
    text(d, (tx, 208), LEAD["kicker"], font(SANS_BOLD, 15), fill=RED, spacing=3)
    y = 232
    for line in LEAD["headline"]:
        d.text((tx, y), line, font=font(SERIF_BOLD, 58), fill=INK)
        y += 60
    block(d, (tx, y + 16), LEAD["deck"], font(SERIF, 21), W - MARGIN - tx, 25, MUTED)

    d.line([(MARGIN, 430), (W - MARGIN, 430)], fill=INK, width=3)

    # six story panels, each carried by its own picture
    for idx, (kicker, headline, line_, _kind) in enumerate(PANELS):
        px, py = panel_pos(idx)
        text(d, (px, py + TEXT_TOP), kicker, font(SANS_BOLD, 11), fill=RED, spacing=2)
        head_font = font(SERIF_BOLD, PANEL_HEAD)
        if head_font.getlength(headline) > COL_W:
            raise ValueError(f"headline is too wide for its panel: {headline!r}")
        d.text((px, py + TEXT_TOP + 18), headline, font=head_font, fill=INK)
        block(d, (px, py + TEXT_TOP + 48), line_, font(SERIF, PANEL_BODY), COL_W, 17, MUTED)

    # one line of briefs at the foot
    lab_font = font(SANS_BOLD, 11)
    d.line([(MARGIN, 968), (W - MARGIN, 968)], fill=GREY, width=1)
    text(d, (MARGIN, 982), "ALSO TODAY", lab_font, fill=RED, spacing=2)
    x = MARGIN + sum(lab_font.getlength(c) for c in "ALSO TODAY") + 2 * 9 + 22
    for label, brief in BRIEFS:
        text(d, (x, 982), label, lab_font, fill=INK, spacing=2)
        x += sum(lab_font.getlength(c) for c in label) + 2 * (len(label) - 1) + 12
        d.text((x, 979), brief, font=font(SERIF, 15), fill=MUTED)
        x += font(SERIF, 15).getlength(brief) + 22

    return page


def main() -> None:
    page = draw_page()
    page.save("entry.png", optimize=True)
    print(f"wrote entry.png ({page.width}x{page.height})")


if __name__ == "__main__":
    main()
