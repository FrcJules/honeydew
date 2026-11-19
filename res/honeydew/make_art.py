#!/usr/bin/env python3
# Honeydew artwork generator (icon, store images, README banner).
# Original art drawn from code with Pillow: a halved honeydew melon seen from the cut side.
# Usage: python3 res/honeydew/make_art.py   (writes the files listed at the bottom)
# SPDX-License-Identifier: GPL-3.0-or-later

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SWITCH = os.path.join(ROOT, "src", "frontend", "switch-sdl")
FONT = "/usr/share/fonts/truetype/ubuntu/UbuntuSans[wdth,wght].ttf"

SS = 4  # supersampling factor

# palette
BG_TOP = (18, 46, 40)
BG_BOT = (8, 24, 22)
RIND = (168, 196, 112)       # outer skin, yellow-green
RIND_DARK = (128, 160, 82)
NET = (226, 232, 190)        # light netting on the skin
BAND = (238, 246, 214)       # pale band between skin and flesh
FLESH_OUT = (176, 226, 120)
FLESH_IN = (214, 242, 168)
CAVITY = (246, 238, 186)
SEED = (236, 214, 150)
SEED_EDGE = (150, 124, 70)
TITLE = (238, 248, 222)
ACCENT = (184, 232, 130)
DIM = (150, 184, 160)


def font(px, style=b"ExtraBold"):
    f = ImageFont.truetype(FONT, px)
    f.set_variation_by_name(style)
    return f


def vgradient(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return im


def radial(size, inner, outer, power=1.6):
    im = Image.new("RGB", (size, size))
    px = im.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            t = min(1.0, math.hypot(x - c, y - c) / c) ** power
            px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(3))
    return im


def circle_mask(size, r, cx=None, cy=None):
    m = Image.new("L", (size, size), 0)
    cx = size / 2 if cx is None else cx
    cy = size / 2 if cy is None else cy
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def melon(d):
    """Halved honeydew of diameter d (RGBA, already downscaled)."""
    S = d * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    R = S / 2

    # skin with a soft shade and a light netting
    skin = Image.new("RGB", (S, S), RIND)
    sd = ImageDraw.Draw(skin)
    for k in range(40):
        t = k / 39
        r = R * (1 - t * 0.04)
        col = tuple(int(RIND_DARK[i] + (RIND[i] - RIND_DARK[i]) * t) for i in range(3))
        sd.ellipse([R - r, R - r, R + r, R + r], fill=col)
    rng = random.Random(7)
    w = max(1, int(S * 0.006))
    for _ in range(110):
        a = rng.uniform(0, 2 * math.pi)
        rr = R * rng.uniform(0.885, 0.985)
        x0, y0 = R + rr * math.cos(a), R + rr * math.sin(a)
        a2 = a + rng.uniform(0.08, 0.22) * rng.choice((-1, 1))
        rr2 = R * rng.uniform(0.885, 0.985)
        x1, y1 = R + rr2 * math.cos(a2), R + rr2 * math.sin(a2)
        sd.line([(x0, y0), (x1, y1)], fill=NET, width=w)
    im.paste(skin, (0, 0), circle_mask(S, R))

    # pale band
    rb = R * 0.87
    ImageDraw.Draw(im).ellipse([R - rb, R - rb, R + rb, R + rb], fill=BAND)

    # flesh (lighter toward the middle)
    rf = R * 0.83
    fs = int(rf * 2)
    flesh = radial(fs, FLESH_IN, FLESH_OUT, power=2.2)
    off = int(R - rf)
    im.paste(flesh, (off, off), circle_mask(fs, rf))

    # seed cavity: a soft, slightly lobed shape with seeds pointing outward
    cav = Image.new("L", (S, S), 0)
    cd = ImageDraw.Draw(cav)
    pts = []
    for k in range(180):
        a = 2 * math.pi * k / 180
        r = R * (0.36 + 0.03 * math.cos(5 * a))
        pts.append((R + r * math.cos(a), R + r * math.sin(a)))
    cd.polygon(pts, fill=255)
    cav = cav.filter(ImageFilter.GaussianBlur(S * 0.006))
    im.paste(Image.new("RGB", (S, S), CAVITY), (0, 0), cav)

    seeds = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for ring, (rr, n, ln) in enumerate(((0.235, 11, 0.1),)):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * ring) / n + 0.1
            sl, sw = R * ln, R * ln * 0.42
            sim = Image.new("RGBA", (int(sl * 2.4), int(sl * 2.4)), (0, 0, 0, 0))
            c = sim.size[0] / 2
            ImageDraw.Draw(sim).ellipse([c - sl, c - sw, c + sl, c + sw], fill=SEED, outline=SEED_EDGE,
                                        width=max(1, int(S * 0.004)))
            sim = sim.rotate(-math.degrees(a), resample=Image.BICUBIC)
            x = R + R * rr * math.cos(a) - c
            y = R + R * rr * math.sin(a) - c
            seeds.alpha_composite(sim, (int(x), int(y)))
    im.alpha_composite(seeds)

    # gloss highlight on the upper left of the flesh
    gl = Image.new("L", (S, S), 0)
    ImageDraw.Draw(gl).ellipse([R - rf * 0.78, R - rf * 0.86, R - rf * 0.05, R - rf * 0.35], fill=70)
    gl = gl.filter(ImageFilter.GaussianBlur(S * 0.03))
    im.paste(Image.new("RGB", (S, S), (255, 255, 240)), (0, 0), Image.composite(gl, Image.new("L", (S, S), 0), circle_mask(S, rf)))

    # soft drop shadow
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = circle_mask(S, R * 0.97, R + S * 0.012, R + S * 0.03).filter(ImageFilter.GaussianBlur(S * 0.02))
    out.paste(Image.new("RGBA", (S, S), (0, 0, 0, 110)), (0, 0), sh)
    out.alpha_composite(im)
    return out.resize((d, d), Image.LANCZOS)


def centered_text(img, text, f, y, fill):
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=f)
    d.text(((img.width - w) / 2, y), text, font=f, fill=fill)


def make_icon(path):
    img = vgradient(256, 256, BG_TOP, BG_BOT).convert("RGBA")
    m = melon(160)
    img.alpha_composite(m, (48, 18))
    centered_text(img, "Honeydew", font(42), 186, TITLE)
    img.convert("RGB").save(path, "JPEG", quality=95, subsampling=0)


def make_store_icon(path):
    img = vgradient(256, 150, BG_TOP, BG_BOT).convert("RGBA")
    img.alpha_composite(melon(96), (80, 8))
    centered_text(img, "Honeydew", font(30), 108, TITLE)
    img.convert("RGB").save(path)


def make_banner(path, w, h):
    img = vgradient(w, h, BG_TOP, BG_BOT).convert("RGBA")
    md = int(h * 0.78)
    mx = int(h * 0.14)
    img.alpha_composite(melon(md), (mx, (h - md) // 2))
    d = ImageDraw.Draw(img)
    x = mx + md + int(h * 0.16)
    d.text((x, h * 0.17), "Honeydew", font=font(int(h * 0.33)), fill=TITLE)
    d.text((x, h * 0.57), "Nintendo DS emulator for Switch", font=font(int(h * 0.105), b"SemiBold"), fill=ACCENT)
    d.text((x, h * 0.74), "based on melonDS (GPL-3.0)", font=font(int(h * 0.08), b"Medium"), fill=DIM)
    img.convert("RGB").save(path)


if __name__ == "__main__":
    make_icon(os.path.join(SWITCH, "icon.jpg"))
    make_store_icon(os.path.join(SWITCH, "store", "store-icon-256x150.png"))
    make_banner(os.path.join(SWITCH, "store", "store-banner-848x208.png"), 848, 208)
    make_banner(os.path.join(HERE, "banner.png"), 1280, 320)
    print("done")
