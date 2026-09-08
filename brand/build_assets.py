"""
Generate the FemmForce brand asset kit from the traced master vector.

Everything here derives from femmforce-bird.svg, which trace_logo.py produced
from the client's own artwork. Nothing is redrawn by hand, so re-running
trace_logo.py and then this script propagates a geometry change through every
asset at once.

    python build_assets.py
"""
import json
import math
import os
import re

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "femmforce-bird.svg")

SS = 3  # supersample factor for raster output

WORDMARK = "FEMMFORCE"
TAGLINE = "EMPOWER ELEVATE EXCEL"

INK = "#141210"
WHITE = "#FFFFFF"

# On a dark ground the deep red drops to roughly 2.5:1 and the head disappears.
# These are the same hues lifted in value, not different colours.
DARK_LIFT = {
    "#C81E14": "#E63A2E",
    "#EC4008": "#F4551E",
    "#F0731A": "#F58A33",
    "#DBA22E": "#E8B449",
}

FONT_CANDIDATES = ("ArchivoBlack-Regular.ttf", "ariblk.ttf", "seguibl.ttf", "arialbd.ttf")


# --------------------------------------------------------------------- input --
def load_shapes(path=MASTER):
    """Parse the master SVG's polygons. Deliberately narrow: this reads the one
    file we generate ourselves, so a real XML parser would be overkill."""
    svg = open(path, encoding="utf8").read()
    shapes = []
    for fill, pts in re.findall(r'<polygon fill="(#[0-9A-Fa-f]{6})" points="([^"]+)"', svg):
        coords = [tuple(float(v) for v in p.split(",")) for p in pts.split()]
        if len(coords) >= 3:
            shapes.append((fill.upper(), coords))
    if not shapes:
        raise SystemExit("no polygons found in %s -- run trace_logo.py first" % path)
    return shapes


def poly_area(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def bbox(shapes):
    xs = [p[0] for _, poly in shapes for p in poly]
    ys = [p[1] for _, poly in shapes for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def compact(shapes, keep=0.15):
    """Small-size variant.

    Below about 40px the scattered shards turn to mush and the mark reads as a
    smudge, so the favicon cannot just be the full mark scaled down. Dropping
    the smallest facets and re-cropping to what remains gives a bolder bird that
    survives 16px.
    """
    biggest = max(poly_area(p) for _, p in shapes)
    return [s for s in shapes if poly_area(s[1]) >= keep * biggest]


# -------------------------------------------------------------------- raster --
def draw_shapes(d, shapes, box, recolour=None):
    """Fit shapes into box=(x, y, w, h), preserving aspect."""
    x0, y0, x1, y1 = bbox(shapes)
    bw, bh = x1 - x0, y1 - y0
    bx, by, bwid, bhgt = box
    s = min(bwid / bw, bhgt / bh)
    ox = bx + (bwid - bw * s) / 2.0
    oy = by + (bhgt - bh * s) / 2.0
    for fill, poly in shapes:
        col = (recolour or {}).get(fill, fill)
        d.polygon([(ox + (px - x0) * s, oy + (py - y0) * s) for px, py in poly], fill=col)


def silhouette(shapes, px, colour="#EC4008", grow=0.022):
    """A solid, single-colour bird for 16-32px.

    No amount of facet-culling makes the faceted mark legible in a browser tab:
    at 16px every facet and every white gap lands under one pixel, so it greys
    out to a smudge. A filled silhouette keeps the recognisable shape and reads
    at any size. Built by dilating the rendered alpha mask rather than unioning
    polygons, which needs no geometry library.
    """
    from PIL import ImageFilter
    big = Image.new("RGBA", (px * SS, px * SS), (0, 0, 0, 0))
    draw_shapes(ImageDraw.Draw(big), shapes, (0, 0, px * SS, px * SS))
    k = max(3, int(px * SS * grow) | 1)          # odd kernel closes the gaps
    mask = big.split()[3].filter(ImageFilter.MaxFilter(k))
    out = Image.new("RGBA", big.size, colour)
    out.putalpha(mask)
    return out.resize((px, px), Image.LANCZOS)


def canvas(w, h, bg):
    return Image.new("RGBA", (w * SS, h * SS), bg)


def finish(img, w, h, path):
    img.resize((w, h), Image.LANCZOS).save(path)
    return path


def font_at(px):
    for name in FONT_CANDIDATES:
        for root in (HERE, os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")):
            p = os.path.join(root, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, px), name
    return ImageFont.load_default(), "default"


def tracked(d, text, font, cx, y, tracking, fill):
    """PIL has no letter-spacing; advance per glyph and centre the result."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2.0
    for ch, adv in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += adv + tracking
    return total


# -------------------------------------------------------------------- assets --
def write_svg(path, shapes, recolour=None, flat=None, pad=0.06):
    x0, y0, x1, y1 = bbox(shapes)
    w, h = x1 - x0, y1 - y0
    m = max(w, h) * pad
    body = "\n".join(
        '  <polygon fill="%s" points="%s"/>'
        % (flat or (recolour or {}).get(fill, fill),
           " ".join("%g,%g" % (round(px - x0 + m, 1), round(py - y0 + m, 1)) for px, py in poly))
        for fill, poly in shapes
    )
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'role="img" aria-label="FemmForce">\n  <title>FemmForce</title>\n%s\n</svg>\n'
           % (round(w + 2 * m, 1), round(h + 2 * m, 1), body))
    open(path, "w", encoding="utf8").write(svg)
    return path


def lockup_vertical(path, shapes, w, bg, fg, recolour=None):
    h = int(w * 0.95)
    img = canvas(w, h, bg)
    d = ImageDraw.Draw(img)
    W, H = img.size
    draw_shapes(d, shapes, (W * 0.22, H * 0.04, W * 0.56, H * 0.50), recolour)
    fw, _ = font_at(int(W * 0.108))
    ft, _ = font_at(int(W * 0.0335))
    tracked(d, WORDMARK, fw, W / 2.0, H * 0.625, W * 0.011, fg)
    tracked(d, TAGLINE, ft, W / 2.0, H * 0.795, W * 0.0125, "#EC4008")
    return finish(img, w, h, path)


def lockup_horizontal(path, shapes, w, bg, fg, recolour=None):
    h = int(w * 0.30)
    img = canvas(w, h, bg)
    d = ImageDraw.Draw(img)
    W, H = img.size
    draw_shapes(d, shapes, (W * 0.03, H * 0.12, W * 0.26, H * 0.76), recolour)
    fw, _ = font_at(int(H * 0.34))
    ft, _ = font_at(int(H * 0.105))
    cx = W * 0.64
    tracked(d, WORDMARK, fw, cx, H * 0.24, W * 0.007, fg)
    tracked(d, TAGLINE, ft, cx, H * 0.66, W * 0.0088, "#EC4008")
    return finish(img, w, h, path)


def main():
    shapes = load_shapes()
    small = compact(shapes)
    print("master facets: %d   compact facets: %d" % (len(shapes), len(small)))
    fname, used = font_at(40)
    print("wordmark font:", used)

    dirs = {k: os.path.join(HERE, k) for k in ("svg", "png", "favicon", "social")}
    for p in dirs.values():
        os.makedirs(p, exist_ok=True)
    made = []

    # ---- vector
    made += [
        write_svg(os.path.join(dirs["svg"], "mark-colour.svg"), shapes),
        write_svg(os.path.join(dirs["svg"], "mark-dark-bg.svg"), shapes, recolour=DARK_LIFT),
        write_svg(os.path.join(dirs["svg"], "mark-black.svg"), shapes, flat=INK),
        write_svg(os.path.join(dirs["svg"], "mark-white.svg"), shapes, flat=WHITE),
        write_svg(os.path.join(dirs["svg"], "mark-compact.svg"), small),
    ]

    # ---- mark rasters, transparent
    for px in (256, 512, 1024):
        img = canvas(px, px, (0, 0, 0, 0))
        draw_shapes(ImageDraw.Draw(img), shapes, (0, 0, px * SS, px * SS))
        made.append(finish(img, px, px, os.path.join(dirs["png"], "mark-%d.png" % px)))

    img = canvas(512, 512, (0, 0, 0, 0))
    draw_shapes(ImageDraw.Draw(img), shapes, (0, 0, 512 * SS, 512 * SS), DARK_LIFT)
    made.append(finish(img, 512, 512, os.path.join(dirs["png"], "mark-dark-512.png")))

    # ---- lockups, 1x/2x/3x, transparent and on white, plus a dark version
    for mult, tag in ((1, "1x"), (2, "2x"), (3, "3x")):
        w = 600 * mult
        made.append(lockup_vertical(
            os.path.join(dirs["png"], "lockup-vertical-%s.png" % tag),
            shapes, w, (0, 0, 0, 0), INK))
        made.append(lockup_horizontal(
            os.path.join(dirs["png"], "lockup-horizontal-%s.png" % tag),
            shapes, w, (0, 0, 0, 0), INK))
    made.append(lockup_vertical(os.path.join(dirs["png"], "lockup-vertical-onwhite.png"),
                                shapes, 1200, (255, 255, 255, 255), INK))
    made.append(lockup_horizontal(os.path.join(dirs["png"], "lockup-horizontal-ondark.png"),
                                  shapes, 1800, (20, 18, 16, 255), WHITE, DARK_LIFT))

    # ---- favicons
    # The .ico is the silhouette: it is only ever shown at 16-48px, where the
    # faceted mark cannot hold together. The larger PNGs keep the full colour
    # mark, since at 96px and up the facets read properly again.
    sil = silhouette(small, 256)
    sil.save(os.path.join(dirs["favicon"], "favicon.ico"),
             sizes=[(16, 16), (32, 32), (48, 48)])
    made.append(os.path.join(dirs["favicon"], "favicon.ico"))
    made.append(finish(sil.resize((32, 32), Image.LANCZOS), 32, 32,
                       os.path.join(dirs["favicon"], "icon-32-solid.png")))

    full = Image.new("RGBA", (512 * SS, 512 * SS), (0, 0, 0, 0))
    draw_shapes(ImageDraw.Draw(full), small, (0, 0, 512 * SS, 512 * SS))
    full = full.resize((512, 512), Image.LANCZOS)
    for px in (96, 192, 512):
        made.append(finish(full.resize((px, px), Image.LANCZOS), px, px,
                           os.path.join(dirs["favicon"], "icon-%d.png" % px)))

    # iOS shows no transparency and clips to a rounded square, so this one is
    # padded and sits on white rather than being edge-to-edge and cut out.
    ap = canvas(180, 180, (255, 255, 255, 255))
    draw_shapes(ImageDraw.Draw(ap), small, (180 * SS * .1, 180 * SS * .12,
                                            180 * SS * .8, 180 * SS * .76))
    made.append(finish(ap, 180, 180, os.path.join(dirs["favicon"], "apple-touch-icon.png")))

    manifest = {
        "name": "FemmForce", "short_name": "FemmForce",
        "icons": [{"src": "/brand/favicon/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/brand/favicon/icon-512.png", "sizes": "512x512", "type": "image/png",
                   "purpose": "any maskable"}],
        "theme_color": "#EC4008", "background_color": "#FFFFFF", "display": "standalone",
    }
    mp = os.path.join(dirs["favicon"], "site.webmanifest")
    open(mp, "w", encoding="utf8").write(json.dumps(manifest, indent=2))
    made.append(mp)

    # ---- social
    og = canvas(1200, 630, (255, 255, 255, 255))
    d = ImageDraw.Draw(og)
    W, H = og.size
    d.rectangle([0, H - 14 * SS, W, H], fill="#EC4008")
    draw_shapes(d, shapes, (W * 0.06, H * 0.16, W * 0.34, H * 0.60))
    fw, _ = font_at(int(H * 0.115))
    ft, _ = font_at(int(H * 0.036))
    d.text((W * 0.44, H * 0.36), "FEMMFORCE", font=fw, fill=INK)
    tracked(d, TAGLINE, ft, W * 0.44 + d.textlength("FEMMFORCE", font=fw) / 2,
            H * 0.53, W * 0.004, "#EC4008")
    made.append(finish(og, 1200, 630, os.path.join(dirs["social"], "og-1200x630.png")))

    for name, bg, rc in (("avatar-1000.png", (255, 255, 255, 255), None),
                         ("avatar-dark-1000.png", (20, 18, 16, 255), DARK_LIFT)):
        av = canvas(1000, 1000, bg)
        draw_shapes(ImageDraw.Draw(av), small,
                    (1000 * SS * .10, 1000 * SS * .14, 1000 * SS * .80, 1000 * SS * .72), rc)
        made.append(finish(av, 1000, 1000, os.path.join(dirs["social"], name)))

    bn = canvas(1584, 396, (20, 18, 16, 255))
    d = ImageDraw.Draw(bn)
    W, H = bn.size
    draw_shapes(d, shapes, (W * 0.05, H * 0.15, W * 0.20, H * 0.70), DARK_LIFT)
    fw, _ = font_at(int(H * 0.24))
    ft, _ = font_at(int(H * 0.072))
    d.text((W * 0.30, H * 0.34), "FEMMFORCE", font=fw, fill=WHITE)
    d.text((W * 0.302, H * 0.60), TAGLINE, font=ft, fill="#F4551E")
    made.append(finish(bn, 1584, 396, os.path.join(dirs["social"], "linkedin-banner.png")))

    print("\nwrote %d files:" % len(made))
    for p in sorted(made):
        print("  " + os.path.relpath(p, HERE).replace("\\", "/"))


if __name__ == "__main__":
    main()
