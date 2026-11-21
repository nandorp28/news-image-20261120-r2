#!/usr/bin/env python3
"""news-image-20261120 round 2 — "The World in One Day".

Draws one 1024x1024 PNG summing up Friday 20 November 2026: 48 sourced
stories across 7 regions, a key-figures strip, a region bar, four feature
cards, a 12-card grid, a dot-grid world map with pins, and a numbered
also-on list — rendered with pure Python 3.13 stdlib (no network, no fonts
on disk: text uses the 5x7 bitmap font defined below).

Run:  python3 main.py [--output DIR]   (default: $MAKEFUN_OUTPUT_DIR or /output)
      python3 main.py --check          (validate only, no file written)
"""

import argparse
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font, written for this entry. Each glyph is 7 rows of 5 bits.
# ---------------------------------------------------------------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

# A bullet glyph (not a letter): drawn as a filled 3x3 block by text code
# when it meets U+2022. Map it to a printable stand-in here.
FONT['\u2022'] = ("00000", "00000", "01110", "01110", "01110", "00000", "00000")


def text_width(s, scale):
    """Pixel width of string s at the given scale (6 units per glyph)."""
    return len(s) * 6 * scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single word longer than the line: hard-split it.
            while text_width(word, scale) > max_w:
                n = max(1, max_w // (6 * scale))
                lines.append(word[:n])
                word = word[n:]
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


class Canvas:
    """A plain RGB raster with the drawing primitives the layout needs."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray([bg[0], bg[1], bg[2]] * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, c)

    def triangle(self, p0, p1, p2, c):
        self.polygon([p0, p1, p2], c)

    def polygon(self, pts, c):
        """Scanline fill for a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                xa, xb = int(nodes[i]), int(nodes[i + 1])
                self.fill_rect(xa, y, max(0, xb - xa), 1, c)

    def text(self, x, y, s, scale, c, align="left"):
        """Draw a string; align may be left, center or right (x is the anchor)."""
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + col_i * scale, y + row_i * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def encode_png(canvas):
    """Encode the canvas as a true-colour (RGB) PNG, filter 0 per row."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# The day's news — 48 stories, all happened or first reported Fri 20 Nov 2026.
# Researched from AP, Reuters, AFP, WSJ, CNN, Business Wire, UN News, PANA,
# Open Chronicle, One Turn, Augerton and IANS on 21 Nov 2026.
# ---------------------------------------------------------------------------
PAPER = (246, 241, 229)
INK = (22, 22, 26)
NAVY = (20, 33, 61)
RED = (192, 57, 43)
GREY = (110, 108, 100)
CARD_BORDER = (216, 210, 194)
WHITE = (255, 255, 255)
SEA = (214, 232, 242)
LAND = (176, 160, 128)

REGIONS = [
    # (code, label, count, colour)
    ("EU", "EUROPE", 11, (31, 78, 121)),
    ("AM", "AMERICAS", 11, (183, 121, 31)),
    ("AS", "ASIA", 9, (123, 45, 139)),
    ("ME", "MIDEAST", 6, (194, 94, 0)),
    ("AF", "AFRICA", 5, (46, 125, 50)),
    ("GL", "GLOBAL", 4, (55, 71, 79)),
    ("OC", "OCEANIA", 2, (0, 131, 143)),
]
REGION_COLOUR = {r[0]: r[3] for r in REGIONS}

KPI = [
    ("$3.79bn", "GTA VI day-one sales, a record", "Take-Two"),
    ("32.5m", "GTA VI units sold pre-release", "Take-Two"),
    ("-3.7%", "S&P 500 falls into correction", "Reuters"),
    ("2 + 1", "missiles and a drone down in Poland", "AP"),
    ("$7.25bn", "Bayer Roundup deal approved", "AP"),
    ("34", "gang suspects killed in Haiti raid", "Reuters"),
]

# Feature cards: (num, region, beat, headline, summary, source, picture)
FEATURES = [
    (1, "EU", "WAR",
     "Russian missiles crash in Poland",
     "Two missiles and a drone came down in SE Poland during Russia's attack "
     "on Ukraine. NATO scrambled jets; Warsaw calls it a deliberate provocation.",
     "AP", "missiles"),
    (2, "GL", "CULTURE",
     "GTA VI: $3.79bn in one day",
     "Rockstar confirms 32.5m units sold pre-release, the biggest "
     "entertainment launch ever, with a 99 on Metacritic.",
     "Take-Two", "sunset"),
    (3, "AM", "MARKETS",
     "Wall St slides into correction",
     "S&P 500 falls 3.7% as AI shares sell off; Nikkei drops 5.1%. "
     "Nvidia faces an SEC accounting probe.",
     "Reuters", "chart"),
    (4, "GL", "CLIMATE",
     "COP31 deadlocks on fossil fuels",
     "Nearly 200 nations in Antalya run into overtime as the draft deal "
     "drops all fossil-fuel language.",
     "UN News", "globe"),
]

# Secondary cards: (num, region, beat, headline, source, picture)
SECONDARY = [
    (5, "EU", "WAR", "Russia hits Kyiv bridges; 3 killed", "RTE", "bridge"),
    (6, "EU", "DIPLOMACY", "Merz: no new Yalta over Europe", "AP", "flags"),
    (7, "EU", "DIPLOMACY", "EU-UK sign food, carbon, youth deals", "Reuters", "handshake"),
    (8, "EU", "SECURITY", "Denmark expels Russian attache", "AP", "shield"),
    (9, "ME", "SECURITY", "Iraqi forces enter militia town", "Reuters", "gate"),
    (10, "ME", "SECURITY", "Saudis stop Houthi missiles", "AFP", "intercept"),
    (11, "AM", "TECH", "Nvidia probed over China chips", "Reuters", "chip"),
    (12, "AM", "JUSTICE", "Palisades Fire arsonist guilty", "AP", "flame"),
    (13, "AM", "POLITICS", "Trump threatens tech firms' tax", "AP", "dollar"),
    (14, "AS", "DISASTER", "Cyclone Akvan hits India coast", "AFP", "storm"),
    (15, "AS", "SECURITY", "Taiwan flags 2,700 suspect accounts", "AFP", "accounts"),
    (16, "GL", "SCIENCE", "BepiColombo reaches Mercury", "ESA", "planet"),
]

# Also-on list: (num, region, one-line story)
ALSO = [
    (17, "EU", "Estonia to shut Russia border crossings"),
    (18, "EU", "Denmark OKs Greenland-US Arctic deal"),
    (19, "EU", "Spain debate: Sanchez admits mistakes"),
    (20, "EU", "Russia invites Europe to Moscow talks"),
    (21, "EU", "HIMARS strike kills 20 Russian officers"),
    (22, "EU", "Price becomes undisputed champion"),
    (23, "AS", "Japan core inflation hits year high"),
    (24, "AS", "China holds rates for 18th month"),
    (25, "AS", "Japan, India deepen defence ties"),
    (26, "AS", "S Korea: first cholera case in a decade"),
    (27, "AS", "Bangladesh troops out as Hasina returns"),
    (28, "AS", "Pakistan beat Sri Lanka, win series"),
    (29, "AS", "India A thrash Nepal by 306 runs"),
    (30, "AM", "Chile, Philippines sign trade pact"),
    (31, "ME", "Pentagon: Iran campaign cost $48.3bn"),
    (32, "ME", "Trump weighs renewed Iran strikes"),
    (33, "ME", "Gaza strikes kill Palestinians"),
    (34, "ME", "Oil tankers face mines near Hormuz"),
    (35, "AF", "Somalia orders UAE envoy out in 72 hrs"),
    (36, "AF", "Tunisia jails rights defender for 5 yrs"),
    (37, "AF", "Nigeria to end jail for suicide attempts"),
    (38, "AF", "AU chief welcomes IGAD treaty"),
    (39, "AF", "Primedia buys The Africa Channel"),
    (40, "AM", "Bayer $7.25bn Roundup deal approved"),
    (41, "AM", "Haiti police kill 34 gang suspects"),
    (42, "AM", "Bukele prepares third-term bid"),
    (43, "AM", "Brazil advances Indigenous land rights"),
    (44, "AM", "Colombia strike over tax plans"),
    (45, "AM", "Fiona the hippo dies at US zoo"),
    (46, "OC", "Cyclone Xavier monitored in S Pacific"),
    (47, "OC", "US eyes deep-sea mining near Samoa"),
    (48, "GL", "Voyager 1: signals now take a day"),
]

# Dot-grid world map: land runs (row, first col, last col) on a 60x30 grid,
# row 0 ~85N to row 29 ~55S, col 0 = 180W, col 30 = 0, col 59 ~174E.
LAND_RUNS = [
    (1, 8, 10), (1, 15, 18),
    (2, 6, 13), (2, 15, 19), (2, 30, 30), (2, 38, 55),
    (3, 2, 5), (3, 6, 13), (3, 15, 18), (3, 24, 24), (3, 36, 56),
    (4, 2, 5), (4, 5, 13), (4, 15, 17), (4, 29, 31), (4, 33, 56),
    (5, 2, 4), (5, 5, 13), (5, 27, 28), (5, 29, 32), (5, 33, 56),
    (6, 5, 12), (6, 27, 28), (6, 28, 33), (6, 34, 56),
    (7, 5, 12), (7, 28, 34), (7, 35, 52), (7, 55, 55),
    (8, 5, 13), (8, 28, 34), (8, 36, 50), (8, 54, 55),
    (9, 5, 13), (9, 29, 34), (9, 35, 38), (9, 44, 51), (9, 54, 55),
    (10, 5, 13), (10, 29, 36), (10, 36, 41), (10, 44, 51), (10, 52, 52),
    (10, 54, 55),
    (11, 5, 12), (11, 28, 36), (11, 37, 41), (11, 41, 44), (11, 44, 50),
    (12, 6, 10), (12, 28, 36), (12, 37, 41), (12, 41, 44), (12, 44, 47),
    (13, 7, 10), (13, 28, 36), (13, 37, 41), (13, 41, 43), (13, 44, 47),
    (13, 50, 50),
    (14, 9, 12), (14, 28, 36), (14, 42, 43), (14, 44, 47), (14, 49, 50),
    (15, 10, 12), (15, 28, 36), (15, 45, 47), (15, 47, 52),
    (16, 12, 16), (16, 29, 35), (16, 47, 52), (16, 53, 55),
    (17, 12, 17), (17, 29, 35), (17, 48, 52), (17, 54, 56),
    (18, 12, 17), (18, 29, 35), (18, 48, 52),
    (19, 12, 17), (19, 29, 35), (19, 36, 36), (19, 50, 55),
    (20, 13, 17), (20, 29, 35), (20, 36, 36), (20, 50, 56),
    (21, 13, 17), (21, 29, 35), (21, 36, 37), (21, 50, 56),
    (22, 13, 16), (22, 29, 34), (22, 50, 56),
    (23, 13, 16), (23, 29, 34), (23, 50, 56), (23, 57, 58),
    (24, 13, 16), (24, 30, 33), (24, 50, 55), (24, 57, 57),
    (25, 13, 15), (25, 30, 32), (25, 51, 54), (25, 57, 58),
    (26, 13, 15), (26, 57, 57),
    (27, 13, 14),
    (28, 13, 14),
    (29, 13, 13),
]

# Map pins: (num, region, grid col, grid row, display offset dx, dy)
PINS = [
    (1, "EU", 33, 7, 6, -16),
    (2, "GL", 18, 10, 8, -12),
    (3, "AM", 18, 10, 12, 10),
    (4, "GL", 35, 10, 10, 10),
    (5, "EU", 35, 8, 14, 2),
    (6, "EU", 32, 7, -18, -2),
    (7, "EU", 31, 7, -20, 10),
    (8, "EU", 32, 6, -6, -18),
    (9, "ME", 37, 11, 6, -10),
    (10, "ME", 38, 13, 8, 6),
    (11, "AM", 10, 10, 0, -12),
    (12, "AM", 10, 11, -2, 12),
    (13, "AM", 17, 10, -14, 8),
    (14, "AS", 44, 14, 0, 0),
    (15, "AS", 50, 13, 0, 0),
]


def tint(c, mix=4):
    """Lighten a colour toward white (mix parts white to 1 part colour)."""
    return tuple((v + 255 * mix) // (mix + 1) for v in c)


def picture(cv, x, y, w, h, kind):
    """Draw a small pictogram scene inside the given box."""
    if kind == "missiles":  # feature: Russian missiles over Poland
        cv.fill_rect(x, y, w, h, NAVY)
        for sx, sy in ((18, 12), (52, 22), (96, 10), (150, 18), (205, 12)):
            cv.disc(x + sx, y + sy, 1, WHITE)
        cv.fill_rect(x, y + h - 14, w, 14, (46, 90, 60))
        for tx, ty, ex, ey in ((30, 12, 70, h - 14), (120, 8, 150, h - 14),
                               (190, 14, 220, h - 14)):
            cv.line(x + tx, y + ty, x + ex, y + ey, (255, 255, 255))
            cv.disc(x + ex, y + ey - 2, 4, RED)
            cv.disc(x + tx, y + ty, 3, (255, 120, 100))
        cv.fill_rect(x + 8, y + h - 32, 26, 8, WHITE)
        cv.fill_rect(x + 8, y + h - 24, 26, 8, RED)
        cv.text(x + w - 52, y + h - 12, "POLAND", 1, WHITE)
    elif kind == "sunset":  # feature: GTA VI Vice City sunset
        cv.fill_rect(x, y, w, 30, (123, 45, 139))
        cv.fill_rect(x, y + 30, w, 28, (219, 112, 147))
        cv.fill_rect(x, y + 58, w, h - 58, (255, 165, 0))
        cv.disc(x + w // 2, y + 44, 18, (255, 230, 120))
        for bx, bw, bh in ((0, 26, 26), (30, 18, 38), (52, 30, 22),
                           (150, 22, 34), (176, 30, 24), (210, 34, 30)):
            cv.fill_rect(x + bx, y + h - bh, bw, bh, (40, 20, 60))
        cv.line(x + 100, y + h - 2, x + 112, y + h - 34, (30, 60, 30))
        for fx, fy in ((100, 52), (108, 48), (116, 48), (124, 52)):
            cv.line(x + 112, y + h - 34, x + fx, y + fy, (30, 60, 30))
        cv.text(x + 8, y + 6, "VICE CITY", 1, WHITE)
    elif kind == "chart":  # feature: markets slide
        cv.fill_rect(x, y, w, h, (22, 22, 26))
        for gy in range(y + 16, y + h - 8, 16):
            cv.hline(x + 8, gy, w - 16, (60, 60, 70))
        pts = [(12, 14), (52, 22), (92, 18), (132, 38), (172, 52), (212, 66)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            cv.line(x + ax, y + ay, x + bx, y + by, RED)
            cv.line(x + ax, y + ay + 1, x + bx, y + by + 1, RED)
        for px, py in pts:
            cv.disc(x + px, y + py, 2, (255, 120, 100))
        cv.text(x + 10, y + h - 24, "-3.7%", 2, (255, 120, 100))
        cv.text(x + w - 66, y + h - 14, "S&P 500", 1, WHITE)
    elif kind == "globe":  # feature: COP31 world
        cv.fill_rect(x, y, w, h, SEA)
        cv.disc(x + 52, y + 44, 32, (70, 140, 200))
        cv.disc(x + 42, y + 34, 12, (46, 125, 50))
        cv.disc(x + 64, y + 52, 10, (46, 125, 50))
        cv.disc(x + 58, y + 28, 6, (46, 125, 50))
        cv.ring(x + 52, y + 44, 32, (30, 90, 150), 2)
        cv.text(x + 110, y + 14, "200", 4, INK)
        cv.text(x + 110, y + 46, "NATIONS", 1, INK)
        cv.text(x + 110, y + 58, "ONE DEADLOCK", 1, RED)
        cv.triangle((x + 200, y + 66), (x + 214, y + 44), (x + 228, y + 66),
                    (46, 125, 50))
    elif kind == "bridge":  # Kyiv bridges hit
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["EU"]))
        cv.fill_rect(x, y + h - 10, w, 10, (70, 140, 200))
        for bx in (10, 60, 110):
            cv.line(x + bx, y + h - 10, x + bx + 20, y + 8, INK)
            cv.line(x + bx + 20, y + 8, x + bx + 40, y + h - 10, INK)
        cv.disc(x + 30, y + 12, 3, RED)
        cv.disc(x + 128, y + 12, 3, RED)
    elif kind == "flags":  # Germany + EU
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["EU"]))
        for i, c in enumerate(((0, 0, 0), (221, 0, 0), (255, 206, 0))):
            cv.fill_rect(x + 8, y + 6 + i * 8, 60, 8, c)
        cv.fill_rect(x + 92, y + 6, 60, 24, (0, 51, 153))
        # Ring of 8 small stars (unit-circle offsets, hand tabulated).
        for ox, oy in ((9, 0), (6, 6), (0, 9), (-6, 6),
                       (-9, 0), (-6, -6), (0, -9), (6, -6)):
            cv.disc(x + 122 + ox, y + 18 + oy, 1, (255, 204, 0))
    elif kind == "handshake":  # EU + UK flags
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["EU"]))
        cv.fill_rect(x + 8, y + 6, 60, 24, (0, 51, 153))
        cv.disc(x + 38, y + 18, 8, (255, 204, 0))
        cv.disc(x + 38, y + 18, 6, (0, 51, 153))
        cv.fill_rect(x + 92, y + 6, 60, 24, (1, 33, 105))
        cv.line(x + 92, y + 6, x + 152, y + 30, WHITE)
        cv.line(x + 152, y + 6, x + 92, y + 30, WHITE)
        cv.fill_rect(x + 118, y + 6, 8, 24, (200, 16, 46))
        cv.fill_rect(x + 92, y + 14, 60, 8, (200, 16, 46))
    elif kind == "shield":  # Denmark expels attache
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["EU"]))
        cv.fill_rect(x + 8, y + 6, 60, 24, (200, 16, 46))
        cv.fill_rect(x + 28, y + 6, 8, 24, WHITE)
        cv.fill_rect(x + 8, y + 14, 60, 8, WHITE)
        cv.polygon([(x + 122, y + 4), (x + 142, y + 4), (x + 142, y + 18),
                    (x + 132, y + 30), (x + 122, y + 18)], (31, 78, 121))
        cv.text(x + 129, y + 12, "!", 1, WHITE)
    elif kind == "gate":  # Iraqi forces enter town
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["ME"]))
        cv.fill_rect(x + 56, y + 8, 48, 22, (150, 110, 70))
        cv.disc(x + 80, y + 12, 10, (150, 110, 70))
        cv.fill_rect(x + 72, y + 16, 16, 14, (60, 40, 20))
        for i, c in enumerate(((200, 16, 46), (255, 255, 255), (0, 0, 0))):
            cv.fill_rect(x + 8, y + 6 + i * 8, 34, 8, c)
        cv.fill_rect(x + 118, y + 6, 34, 8, (0, 120, 60))
        cv.fill_rect(x + 118, y + 14, 34, 8, WHITE)
        cv.fill_rect(x + 118, y + 22, 34, 8, (0, 0, 0))
    elif kind == "intercept":  # Saudi interception
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["ME"]))
        cv.fill_rect(x + 8, y + 6, 60, 24, (0, 120, 60))
        cv.text(x + 14, y + 14, "SAUDI", 1, WHITE)
        cv.line(x + 90, y + 28, x + 140, y + 6, RED)
        cv.disc(x + 90, y + 28, 3, RED)
        cv.line(x + 130, y + 2, x + 150, y + 16, WHITE)
        cv.line(x + 150, y + 2, x + 130, y + 16, WHITE)
    elif kind == "chip":  # Nvidia probe
        cv.fill_rect(x, y, w, h, (30, 30, 36))
        cv.fill_rect(x + 56, y + 6, 40, 22, (118, 185, 0))
        for px in (64, 76, 88):
            cv.vline(x + px, y + 2, 4, (118, 185, 0))
            cv.vline(x + px, y + 28, 4, (118, 185, 0))
        cv.ring(x + 130, y + 15, 9, WHITE, 2)
        cv.line(x + 137, y + 22, x + 146, y + 30, WHITE)
    elif kind == "flame":  # Palisades fire
        cv.fill_rect(x, y, w, h, tint((194, 94, 0)))
        cv.fill_rect(x + 10, y + 16, 30, 14, (120, 80, 50))
        cv.triangle((x + 8, y + 16), (x + 25, y + 4), (x + 42, y + 16),
                    (100, 50, 30))
        cv.triangle((x + 70, y + 30), (x + 82, y + 4), (x + 94, y + 30), RED)
        cv.triangle((x + 76, y + 30), (x + 82, y + 14), (x + 88, y + 30),
                    (255, 200, 0))
        cv.triangle((x + 108, y + 30), (x + 118, y + 10), (x + 128, y + 30),
                    RED)
    elif kind == "dollar":  # Trump tech tax
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["AM"]))
        cv.text(x + 10, y + 6, "$", 3, (0, 120, 60))
        cv.fill_rect(x + 60, y + 14, 50, 16, (90, 90, 100))
        cv.fill_rect(x + 66, y + 6, 6, 10, (90, 90, 100))
        cv.fill_rect(x + 82, y + 6, 6, 10, (90, 90, 100))
        cv.text(x + 118, y + 12, "TAX", 2, RED)
    elif kind == "storm":  # Cyclone Akvan
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["AS"]))
        for r in (12, 8, 4):
            cv.ring(x + 40, y + 17, r, (80, 80, 120), 2)
        for rx in (90, 105, 120, 135):
            cv.line(x + rx, y + 6, x + rx - 4, y + 18, (70, 140, 200))
            cv.line(x + rx, y + 20, x + rx - 4, y + 30, (70, 140, 200))
    elif kind == "accounts":  # Taiwan flags accounts
        cv.fill_rect(x, y, w, h, tint(REGION_COLOUR["AS"]))
        cv.fill_rect(x + 8, y + 4, 44, 26, (200, 16, 46))
        cv.fill_rect(x + 8, y + 4, 22, 13, (0, 0, 140))
        cv.text(x + 60, y + 8, "@", 2, INK)
        for dx in (0, 14, 28):
            cv.disc(x + 96 + dx, y + 17, 5, (123, 45, 139))
        cv.text(x + 132, y + 12, "x2700", 1, RED)
    elif kind == "planet":  # BepiColombo at Mercury
        cv.fill_rect(x, y, w, h, (10, 10, 20))
        for sx, sy in ((10, 6), (30, 12), (150, 8), (140, 26)):
            cv.disc(x + sx, y + sy, 1, WHITE)
        cv.disc(x + 44, y + 17, 13, (150, 140, 130))
        cv.disc(x + 40, y + 13, 3, (110, 100, 90))
        cv.disc(x + 50, y + 21, 2, (110, 100, 90))
        cv.fill_rect(x + 96, y + 14, 10, 6, WHITE)
        cv.fill_rect(x + 82, y + 15, 12, 4, (70, 140, 200))
        cv.fill_rect(x + 108, y + 15, 12, 4, (70, 140, 200))


def draw_header(cv):
    # Kicker strip.
    cv.fill_rect(0, 0, W, 24, NAVY)
    cv.text(12, 8, "THE WORLD IN ONE DAY - ONE IMAGE", 1, WHITE)
    cv.text(W - 12, 8, "48 SOURCED STORIES - 7 REGIONS - FRI 20 NOV 2026", 1,
            WHITE, align="right")
    # Title band.
    cv.text(14, 32, "FRIDAY 20 NOVEMBER 2026", 6, INK)
    cv.fill_rect(892, 30, 118, 58, RED)
    cv.text(951, 36, "48", 4, WHITE, align="center")
    cv.text(951, 68, "STORIES", 1, WHITE, align="center")
    cv.text(14, 80,
            "Every story happened or was first reported on this day. "
            "Sources named for each one.", 1, (70, 68, 60))
    cv.fill_rect(14, 94, 996, 2, RED)


def draw_kpi(cv):
    y0, bh = 98, 52
    for i, (fig, label, _src) in enumerate(KPI):
        x = 8 + i * 168
        cv.fill_rect(x, y0, 166, bh, WHITE)
        cv.rect(x, y0, 166, bh, CARD_BORDER)
        colour = RED if fig.startswith("-") else NAVY
        cv.text(x + 8, y0 + 6, fig, 3, colour)
        for j, line in enumerate(wrap_text(label, 150, 1)[:2]):
            cv.text(x + 8, y0 + 30 + j * 9, line, 1, INK)


def draw_region_bar(cv):
    y0, bh = 154, 22
    total = sum(r[2] for r in REGIONS)
    x = 8
    for code, label, count, colour in REGIONS:
        w = round(count / total * 1008)
        if code == "OC":
            label = "OCE"
        cv.fill_rect(x, y0, w, bh, colour)
        cv.text(x + w // 2, y0 + 7, f"{label} {count}", 1, WHITE,
                align="center")
        x += w
    cv.hline(8, 180, 1008, INK)


def draw_features(cv):
    y0, ch = 184, 222
    for i, (num, region, beat, headline, summary, src, kind) in enumerate(
            FEATURES):
        x = 8 + i * 254
        w = 246
        colour = REGION_COLOUR[region]
        cv.fill_rect(x, y0, w, ch, WHITE)
        cv.rect(x, y0, w, ch, CARD_BORDER)
        picture(cv, x + 1, y0 + 1, w - 2, 86, kind)
        cv.fill_rect(x + 8, y0 + 94, 18, 18, colour)
        cv.text(x + 17, y0 + 99, str(num), 1, WHITE, align="center")
        cv.text(x + 30, y0 + 99, f"{region} - {beat}", 1, colour)
        for j, line in enumerate(wrap_text(headline, w - 16, 2)[:3]):
            cv.text(x + 8, y0 + 116 + j * 16, line, 2, INK)
        for j, line in enumerate(wrap_text(summary, w - 16, 1)[:4]):
            cv.text(x + 8, y0 + 152 + j * 9, line, 1, (50, 50, 50))
        cv.text(x + 8, y0 + 204, f"SOURCE: {src}", 1, GREY)


def draw_secondary(cv):
    for row in range(2):
        y0 = 410 + row * 106
        for col in range(6):
            num, region, beat, headline, src, kind = SECONDARY[row * 6 + col]
            x = 8 + col * 168
            w = 164
            colour = REGION_COLOUR[region]
            cv.fill_rect(x, y0, w, 104, WHITE)
            cv.rect(x, y0, w, 104, CARD_BORDER)
            picture(cv, x + 1, y0 + 1, w - 2, 34, kind)
            cv.fill_rect(x + 6, y0 + 40, 14, 14, colour)
            cv.text(x + 13, y0 + 43, str(num), 1, WHITE, align="center")
            cv.text(x + 24, y0 + 43, f"{region} - {beat}", 1, colour)
            for j, line in enumerate(wrap_text(headline, w - 12, 1)[:3]):
                cv.text(x + 6, y0 + 58 + j * 9, line, 1, INK)
            cv.text(x + 6, y0 + 88, src, 1, GREY)


def draw_bottom(cv):
    # Section headers.
    cv.text(8, 632, "WHERE IT HAPPENED - PINS 1-15", 2, INK)
    cv.text(478, 632, "ALSO ON FRIDAY 20 NOVEMBER - STORIES 17-48", 2, INK)
    cv.fill_rect(8, 650, 462, 2, RED)
    cv.fill_rect(478, 650, 538, 2, RED)
    # World map: dot grid.
    mx, my, mw, mh = 8, 656, 462, 294
    cv.fill_rect(mx, my, mw, mh, SEA)
    cv.rect(mx, my, mw, mh, CARD_BORDER)
    cell = 7.6
    ox = mx + (mw - 60 * cell) / 2
    oy = my + (mh - 30 * cell) / 2
    for r, c0, c1 in LAND_RUNS:
        for c in range(c0, c1 + 1):
            cv.disc(int(ox + c * cell + cell / 2),
                    int(oy + r * cell + cell / 2), 2, LAND)
    for num, region, gc, gr, dx, dy in PINS:
        px = int(ox + gc * cell + cell / 2)
        py = int(oy + gr * cell + cell / 2)
        qx, qy = px + dx, py + dy
        cv.line(px, py, qx, qy, (90, 90, 90))
        cv.fill_rect(qx - 7, qy - 7, 14, 14, WHITE)
        cv.fill_rect(qx - 6, qy - 6, 12, 12, REGION_COLOUR[region])
        cv.text(qx, qy - 3, str(num), 1, WHITE, align="center")
    cv.text(mx + 8, my + mh - 16,
            "16 is in space: BepiColombo at Mercury.", 1, (60, 60, 60))
    # Also-on list, two columns of 16.
    for idx, (num, region, line) in enumerate(ALSO):
        col = idx // 16
        row = idx % 16
        x = 478 + col * 272
        y = 656 + row * 18
        cv.fill_rect(x, y, 16, 14, REGION_COLOUR[region])
        cv.text(x + 8, y + 3, str(num), 1, WHITE, align="center")
        cv.text(x + 20, y + 3, line, 1, INK)


def draw_footer(cv):
    cv.fill_rect(8, 954, 1008, 42, (253, 246, 216))
    cv.rect(8, 954, 1008, 42, (210, 190, 120))
    cv.text(16, 960, "DATE CHECK:", 1, RED)
    prefix_w = text_width("DATE CHECK: ", 1)
    lines = wrap_text(
        "All 48 stories happened or were first reported Fri 20 Nov 2026. "
        "Excluded as earlier dates: Shenzhen summit (19 Nov), ICJ Myanmar "
        "ruling (19 Nov), US measles status (17 Nov), GTA VI launch (19 Nov) "
        "- only the 20 Nov sales figures counted.", 1008 - 16 - prefix_w, 1)
    cv.text(16 + prefix_w, 960, lines[0], 1, INK)
    for j, line in enumerate(lines[1:3]):
        cv.text(16, 970 + j * 10, line, 1, INK)
    cv.text(16, 1004,
            "Sources: AP - Reuters - AFP - BBC - WSJ - CNN - Business Wire - "
            "UN News - PANA - Open Chronicle - One Turn - Augerton - IANS - "
            "NASA - Take-Two", 1, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    draw_kpi(cv)
    draw_region_bar(cv)
    draw_features(cv)
    draw_secondary(cv)
    draw_bottom(cv)
    draw_footer(cv)
    return cv


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=None, help="output directory")
    ap.add_argument("--check", action="store_true", help="validate only")
    args = ap.parse_args(argv)

    outdir = args.output or os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    canvas = render()
    data = encode_png(canvas)
    if len(data) > 1048576:
        print(f"ERROR: entry.png is {len(data)} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    if args.check:
        print(f"check ok: {len(data)} bytes, {W}x{H}")
        return 0
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
