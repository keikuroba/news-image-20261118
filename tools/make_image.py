#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news infographic (1024x1024 PNG).

Run once, locally, at build time. The entry program (main.py) only copies
the finished image; this script is never run by the grader. Output is
deterministic: fixed text, fixed layout, fixed colours, no clock, no
network, no randomness. Pillow is the only dependency.

Layout (newspaper front page, 1024x1024):
  masthead  -> THE WORLD IN ONE IMAGE / WEDNESDAY 18 NOVEMBER 2026
  lead      -> Gulf escalation (full width)
  row 2     -> Kerch Bridge | Nvidia (two columns)
  row 3     -> Shenzhen summit eve | Alaska Senate (two columns)
  ticker    -> the rest of the day, one dark band
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "entry.png")

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (22, 22, 22)
NAVY = (18, 34, 62)
RED = (178, 34, 26)
MUTED = (90, 86, 78)
RULE = (18, 34, 62)
LIGHT_LINE = (196, 188, 172)


def find_font(bold=False):
    """DejaVu ships with most Linux Pillow installs; fall back to default."""
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for base in ("/usr/share/fonts/truetype/dejavu",
                 "/usr/share/fonts/dejavu"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return path
    return None


def font(size, bold=False):
    path = find_font(bold)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap by pixel width; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_story(draw, x, y, w, label, headline, body, head_size=34,
               body_size=23, label_size=24):
    """Draw one story block; returns the y just below it."""
    lab_f = font(label_size, bold=True)
    draw.text((x, y), label, font=lab_f, fill=RED)
    y += label_size + 10
    head_f = font(head_size, bold=True)
    for line in wrap(draw, headline, head_f, w):
        draw.text((x, y), line, font=head_f, fill=INK)
        y += head_size + 6
    y += 4
    body_f = font(body_size)
    for line in wrap(draw, body, body_f, w):
        draw.text((x, y), line, font=body_f, fill=(52, 52, 52))
        y += body_size + 7
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 40  # side margin

    # ---- masthead ----
    d.rectangle([0, 0, W, 8], fill=NAVY)
    title_f = font(50, bold=True)
    d.text((mx, 34), "THE WORLD IN ONE IMAGE", font=title_f, fill=NAVY)
    # date badge: red disc with the day number
    d.ellipse([W - mx - 92, 26, W - mx, 118], fill=RED)
    num_f = font(46, bold=True)
    d.text((W - mx - 66, 44), "18", font=num_f, fill=(255, 255, 255))
    date_f = font(30, bold=True)
    d.text((mx, 100), "WEDNESDAY  \u00b7  18 NOVEMBER 2026",
           font=date_f, fill=RED)
    d.line([(mx, 146), (W - mx, 146)], fill=RULE, width=4)
    d.line([(mx, 154), (W - mx, 154)], fill=RULE, width=1)

    # ---- lead story: Gulf escalation ----
    y = draw_story(
        d, mx, 176, W - 2 * mx,
        "GULF ESCALATION",
        "U.S. jets hit an Iranian missile site \u2014 Iran\u2019s drones "
        "hit U.S. bases in Bahrain and Kuwait",
        "Washington struck a Guard launch site on Qeshm Island after drone "
        "attacks on a U.S. radar base in Bahrain. On Wednesday Iran fired "
        "drones at U.S. bases in Kuwait.",
        head_size=36, body_size=22)
    d.line([(mx, y + 10), (W - mx, y + 10)], fill=LIGHT_LINE, width=2)
    y += 22

    # ---- row 2: two columns ----
    col_w = (W - 2 * mx - 40) // 2
    left_y = draw_story(
        d, mx, y, col_w,
        "KERCH BRIDGE FALLS",
        "Ukraine\u2019s second-day strikes drop a span into the strait",
        "Drones and missiles hit the Crimea link again; one arch collapsed "
        "into the strait.",
        head_size=29, body_size=20)
    right_y = draw_story(
        d, mx + col_w + 40, y, col_w,
        "NVIDIA\u2019S RECORD QUARTER",
        "$115.8bn revenue \u2014 double a year ago; board says no to Huang",
        "Record results since Jensen Huang stepped down. Huang offered to "
        "return; the board refused \u2014 and the shares still rose.",
        head_size=29, body_size=20)
    y = max(left_y, right_y)
    d.line([(mx, y + 10), (W - mx, y + 10)], fill=LIGHT_LINE, width=2)
    y += 22

    # ---- row 3: two columns ----
    left_y = draw_story(
        d, mx, y, col_w,
        "SUMMIT EVE IN SHENZHEN",
        "Xi meets Putin ahead of Thursday\u2019s first Trump\u2013Xi\u2013Putin summit",
        "The three leaders gather on the APEC sidelines; Trump met the Quad "
        "in Manila first.",
        head_size=29, body_size=20)
    right_y = draw_story(
        d, mx + col_w + 40, y, col_w,
        "ALASKA FLIPS THE SENATE",
        "Peltola win gives the Democrats 56 seats",
        "Democrat Mary Peltola took Alaska\u2019s Senate seat, extending her "
        "party\u2019s majority in Washington.",
        head_size=29, body_size=20)
    y = max(left_y, right_y)

    # ---- ticker: the rest of the day (band placed after row 3) ----
    band_y = y + 16
    band_h = 100
    d.rectangle([0, band_y, W, band_y + band_h], fill=NAVY)
    tick_f = font(24, bold=True)
    d.text((mx, band_y + 12), "ALSO TODAY", font=tick_f, fill=(255, 214, 90))
    tick = ("Ebola tops 11,000 cases  \u00b7  "
            "U.S. loses measles-free status  \u00b7  "
            "NSA outage, Dow falls ~850  \u00b7  "
            "Cyclone Xavier, Cat 5  \u00b7  "
            "Siberia crash kills 19  \u00b7  "
            "Dhoni retires")
    tick_f2 = font(21)
    ty = band_y + 46
    for line in wrap(d, tick, tick_f2, W - 2 * mx):
        d.text((mx, ty), line, font=tick_f2, fill=(238, 238, 238))
        ty += 26
    assert ty - 26 + 21 <= band_y + band_h, "ticker overflows its band"

    # ---- footer ----
    foot_f = font(19)
    foot_y = band_y + band_h + 10
    d.text((mx, foot_y), "Every story first reported on 18 November 2026  \u00b7  "
           "made for make.fun", font=foot_f, fill=MUTED)
    assert foot_y + 19 <= H, "footer overflows the page"

    img.save(OUT, format="PNG", optimize=True)
    size = os.path.getsize(OUT)
    assert size <= 1048576, "image over 1 MiB: %d" % size
    print("wrote", OUT, size, "bytes")


if __name__ == "__main__":
    main()
