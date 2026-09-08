"""
FemmForce logo — vector reconstruction.

The only source available was a low-resolution screenshot, so the mark is
redrawn as polygon geometry rather than upscaled. This file is the single
source of truth: the SVG and every PNG are generated from FACETS below, so
a coordinate fixed here is fixed everywhere.

    python build_logo.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.join(HERE, "preview")

# ---------------------------------------------------------------- palette --
CRIMSON_DEEP = "#B01310"
CRIMSON      = "#C81E14"
RED          = "#D62A16"
VERMILION    = "#E8451D"
ORANGE_RED   = "#EE5D1E"
ORANGE       = "#F0691F"
ORANGE_BR    = "#F5871F"
AMBER        = "#F9A21C"
AMBER_LT     = "#FBB040"
INK          = "#141210"

# ------------------------------------------------------------------ mark --
# 512 x 512 canvas. Hummingbird facing left: long beak, one wing swept up and
# right, forked tail trailing down-right, breast dissolving into shards.
#
# Geometry is a shared-vertex mesh, not free-floating polygons. Every triangle
# names its corners from V, so neighbours share exact coordinates and the
# silhouette closes with no seams. Move a vertex and every facet touching it
# follows.
import math

# The wing is generated rather than hand-placed: it is a fan of feathers about
# a pivot, so its sweep, span and pointedness are four numbers instead of
# twenty coordinates. Tips sit further out than the notches between them, which
# is what gives the outer edge its serrated, feathered profile.
WING = dict(
    pivot=(236, 236),
    a0=-92.0,      # leading edge, degrees: -90 is straight up
    a1=-8.0,       # trailing edge, near horizontal
    r_mid=96.0,    # inner ring, hidden behind the body
    r_tip=218.0,   # feather points
    r_notch=168.0, # the valleys between them
    feathers=5,
)
WING_RAMP = [ORANGE, ORANGE_BR, AMBER, ORANGE_BR, AMBER_LT]
WING_INNER = [ORANGE_RED, ORANGE, ORANGE, ORANGE_RED, ORANGE_RED]


def _polar(pivot, deg, r):
    a = math.radians(deg)
    return (round(pivot[0] + r * math.cos(a), 1), round(pivot[1] + r * math.sin(a), 1))


def build_wing(w=WING):
    n = w["feathers"]
    bounds = [w["a0"] + (w["a1"] - w["a0"]) * i / n for i in range(n + 1)]
    K = [_polar(w["pivot"], b, w["r_mid"]) for b in bounds]     # inner ring
    N = [_polar(w["pivot"], b, w["r_notch"]) for b in bounds]   # notches
    T = [_polar(w["pivot"], (bounds[i] + bounds[i + 1]) / 2, w["r_tip"]) for i in range(n)]

    out = []
    for i in range(n):
        out.append(("wing_root_%d" % i, [w["pivot"], K[i], K[i + 1]], WING_INNER[i % len(WING_INNER)]))
    for i in range(n):
        c = WING_RAMP[i % len(WING_RAMP)]
        out.append(("feather_%d_a" % i, [K[i], N[i], T[i]], c))
        out.append(("feather_%d_b" % i, [K[i], T[i], N[i + 1]], WING_RAMP[(i + 1) % len(WING_RAMP)]))
        out.append(("feather_%d_c" % i, [K[i], N[i + 1], K[i + 1]], c))
    return out


V = {
    # beak, long and straight, pointing left
    "bk": (30, 262), "bt": (128, 244), "bb": (124, 266),
    # head and throat
    "ht": (184, 214), "th": (158, 290),
    # top of the back, and the rump
    "sh": (256, 206), "bc": (306, 244),
    # breast and belly
    "br": (208, 314), "bl": (272, 308),
    # body centre, for the fan
    "c": (218, 262),
    # tail
    "t1": (366, 306), "t2": (412, 372), "t3": (360, 380),
}

TAIL = [
    ("tail_root",  ["bc", "t1", "bl"], ORANGE_RED),
    ("tail_upper", ["t1", "t2", "t3"], ORANGE_BR),
    ("tail_lower", ["t1", "t3", "bl"], ORANGE),
]

BODY = [
    ("head_top", ["ht", "sh", "c"], RED),
    ("back",     ["sh", "bc", "c"], VERMILION),
    ("flank",    ["bc", "bl", "c"], ORANGE_RED),
    ("belly",    ["bl", "br", "c"], VERMILION),
    ("breast",   ["br", "th", "c"], RED),
    ("throat",   ["th", "ht", "c"], CRIMSON),
    ("cheek",    ["bt", "ht", "th", "bb"], CRIMSON),
    ("beak",     ["bk", "bt", "bb"], CRIMSON_DEEP),
]

# Detached shards. These float free on purpose — the mark's whole idea is a
# bird coming apart at its trailing edge, so this is the one place a gap is
# deliberate. They shrink as they fall away from the breast.
SHARDS = [
    ("shard_1", [(190, 324), (220, 336), (200, 362)], RED),
    ("shard_2", [(158, 362), (184, 372), (166, 398)], CRIMSON),
    ("shard_3", [(130, 400), (152, 408), (138, 430)], CRIMSON),
    ("shard_4", [(108, 436), (124, 442), (114, 458)], CRIMSON_DEEP),
]

# Draw order is paint order: the wing and tail sit behind the body, so the
# wing's hidden inner ring is covered and it reads as emerging from the back.
FACETS = (
    build_wing()
    + [(n, [V[k] for k in keys], c) for n, keys, c in TAIL]
    + [(n, [V[k] for k in keys], c) for n, keys, c in BODY]
    + SHARDS
)

WORDMARK = "FEMMFORCE"
TAGLINE  = "EMPOWER ELEVATE EXCEL"


# ------------------------------------------------------------------- svg --
def write_svg(path, size=512):
    body = "\n".join(
        '  <polygon id="%s" points="%s" fill="%s"/>'
        % (name, " ".join("%g,%g" % p for p in pts), colour)
        for name, pts, colour in FACETS
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" '
        'width="%d" height="%d" role="img" aria-label="FemmForce">\n'
        "  <title>FemmForce</title>\n%s\n</svg>\n" % (size, size, body)
    )
    with open(path, "w", encoding="utf8") as f:
        f.write(svg)


# ------------------------------------------------------------------- png --
SS = 4  # supersample, then downsample for clean antialiased edges


def draw_mark(draw, ox, oy, scale):
    for _name, pts, colour in FACETS:
        draw.polygon([(ox + x * scale, oy + y * scale) for x, y in pts], fill=colour)


def render_mark(path, size=512, bg=None):
    w = size * SS
    img = Image.new("RGBA", (w, w), bg or (0, 0, 0, 0))
    draw_mark(ImageDraw.Draw(img), 0, 0, w / 512.0)
    img.resize((size, size), Image.LANCZOS).save(path)


def tracked(draw, text, font, cx, y, tracking, fill):
    """PIL has no letter-spacing, so advance manually and centre the result."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2.0
    for ch, adv in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += adv + tracking
    return total


def font_at(px):
    for name in ("ariblk.ttf", "seguibl.ttf", "arialbd.ttf"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def render_lockup(path, w=1000, bg=(255, 255, 255, 255), fg=INK):
    """Vertical lockup: mark over wordmark over tagline, as in the original."""
    h = int(w * 0.95)
    W, H = w * SS, h * SS
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)

    mark_px = int(W * 0.50)
    draw_mark(d, (W - mark_px) / 2.0, H * 0.045, mark_px / 512.0)

    cx = W / 2.0
    tracked(d, WORDMARK, font_at(int(W * 0.108)), cx, H * 0.625, W * 0.011, fg)
    tracked(d, TAGLINE, font_at(int(W * 0.0335)), cx, H * 0.795, W * 0.0125, VERMILION)

    img.resize((w, h), Image.LANCZOS).save(path)


def render_contact_sheet(path):
    """The mark on white, on ink, and run down to favicon sizes."""
    w, h = 1200, 520
    W, H = w * SS, h * SS
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([W // 2, 0, W, H], fill=INK)

    s = 320 * SS
    draw_mark(d, 140 * SS, 60 * SS, s / 512.0)
    draw_mark(d, 740 * SS, 60 * SS, s / 512.0)

    # legibility check: does it still read at favicon scale?
    f = font_at(int(11 * SS))
    x, base = 150 * SS, 470 * SS
    for px in (96, 64, 40, 24, 16):
        draw_mark(d, x, base - px * SS, px * SS / 512.0)
        d.text((x, base + 6 * SS), "%dpx" % px, font=f, fill="#8A857E")
        x += (px + 34) * SS

    img.resize((w, h), Image.LANCZOS).save(path)


if __name__ == "__main__":
    os.makedirs(PREVIEW, exist_ok=True)
    write_svg(os.path.join(HERE, "femmforce-mark.svg"))
    render_mark(os.path.join(PREVIEW, "mark-512-transparent.png"), 512)
    render_lockup(os.path.join(PREVIEW, "lockup-vertical.png"))
    render_contact_sheet(os.path.join(PREVIEW, "contact-sheet.png"))
    print("built:")
    for f in sorted(os.listdir(PREVIEW)):
        print("  preview/" + f)
    print("  femmforce-mark.svg")
