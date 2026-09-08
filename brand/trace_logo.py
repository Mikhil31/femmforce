"""
Trace the FemmForce bird from the low-resolution source into clean vector.

The source is 124x102 with the bird occupying roughly 86x64 px, so the goal is
not to invent detail but to recover the straight edges that the rasteriser
destroyed. The mark is built from flat, straight-sided facets, which is the one
case where tracing genuinely reconstructs artwork instead of guessing at it.

Method:
  1. k-means the real bird pixels to learn the actual palette, rather than
     assuming hex values.
  2. Upsample before quantising. The antialiased edge carries sub-pixel
     information about where the true boundary sits; thresholding at 6x keeps
     it, thresholding at 1x throws it away.
  3. Label connected regions per colour, drop specks.
  4. Walk each region's boundary along pixel cracks, then simplify with
     Ramer-Douglas-Peucker. Aggressive epsilon is correct here: the true edges
     are straight, so anything that survives is signal and anything removed was
     staircase noise.

    python trace_logo.py
"""
import math
import os
import random
from collections import deque

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW = os.path.join(HERE, "preview")
SRC = os.path.join(HERE, "source-logo.png")

UPSCALE = 8         # trace at this multiple of the source
K = 5               # palette size
BIRD_ROWS = 76      # everything above the wordmark
MIN_AREA = 60       # px at UPSCALE; drops antialiasing specks
RDP_EPS = 8.5       # px at UPSCALE; ~0.7 source px
OUT_W = 1024        # viewBox width of the emitted SVG

# Measured from the highest-chroma pixels in the source rather than clustered.
# k-means kept electing blend tones (#F9B07C, #D48750) because the antialiasing
# halo outnumbers the facet interiors at this resolution, and those blends then
# flooded the large regions and washed the whole mark out.
PALETTE = [
    (0xC8, 0x1E, 0x14),   # deep red — shards, wing tips
    (0xEC, 0x40, 0x08),   # vermilion — wing blades
    (0xF0, 0x73, 0x1A),   # orange — body
    (0xDB, 0xA2, 0x2E),   # gold — head and beak
]


# ------------------------------------------------------------------ palette --
def kmeans(points, k, iters=40, seed=7):
    random.seed(seed)
    cents = random.sample(points, k)
    for _ in range(iters):
        buckets = [[] for _ in range(k)]
        for p in points:
            best, bd = 0, None
            for i, c in enumerate(cents):
                d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
                if bd is None or d < bd:
                    best, bd = i, d
            buckets[best].append(p)
        moved = False
        for i, b in enumerate(buckets):
            if not b:
                continue
            n = len(b)
            nc = (sum(p[0] for p in b) // n, sum(p[1] for p in b) // n,
                  sum(p[2] for p in b) // n)
            if nc != cents[i]:
                cents[i], moved = nc, True
        if not moved:
            break
    return sorted(cents, key=lambda c: -(c[0] - c[2]))  # reddest first


def learn_palette(img):
    """Learn from saturated pixels only.

    At this resolution most pixels are antialiasing blends between a facet and
    the white ground. Clustering all of them yields washed-out centroids like
    #E6B596, which are artefacts of the rasteriser rather than colours anyone
    chose. Requiring real chroma keeps only pixels that sit inside a facet.
    """
    px = img.load()
    w, _ = img.size
    pts = []
    for y in range(BIRD_ROWS):
        for x in range(w):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            if mx < 150 or mx - mn < 95:
                continue
            pts.append((r, g, b))
    print("palette learned from %d saturated px" % len(pts))
    return kmeans(pts, K)


# ----------------------------------------------------------------- labelling --
def hue_of(r, g, b, mx, delta):
    if mx == r:
        h = 60.0 * (((g - b) / delta) % 6)
    elif mx == g:
        h = 60.0 * (((b - r) / delta) + 2)
    else:
        h = 60.0 * (((r - g) / delta) + 4)
    return h


def hue_gap(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def quantise(img, palette):
    """Return a label grid: -1 background, else palette index."""
    hues = [hue_of(c[0], c[1], c[2], max(c), max(c) - min(c)) for c in palette]
    px = img.load()
    w, h = img.size
    lab = [[-1] * w for _ in range(h)]
    for y in range(h):
        row = lab[y]
        for x in range(w):
            r, g, b = px[x, y][:3]
            mx, mn = max(r, g, b), min(r, g, b)
            delta = mx - mn
            # Saturation decides ink vs ground, hue decides which facet colour.
            #
            # RGB distance is the wrong metric here: a 50% white/vermilion blend
            # is numerically closest to gold, so halo pixels elect gold and the
            # mark floods. Blending toward white drops saturation but leaves hue
            # alone, so hue survives the rasteriser and is the reliable signal.
            if mx < 60 or delta == 0 or delta / mx < 0.21:
                row[x] = -1
                continue
            row[x] = min(range(len(hues)), key=lambda i: hue_gap(hue_of(r, g, b, mx, delta), hues[i]))
    return lab


def components(lab, w, h):
    seen = [[False] * w for _ in range(h)]
    out = []
    for y0 in range(h):
        for x0 in range(w):
            if seen[y0][x0] or lab[y0][x0] < 0:
                continue
            val = lab[y0][x0]
            q, cells = deque([(x0, y0)]), []
            seen[y0][x0] = True
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] \
                            and lab[ny][nx] == val:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            if len(cells) >= MIN_AREA:
                out.append((val, set(cells)))
    return out


# ------------------------------------------------------------------ contours --
def outline(cells):
    """Walk the boundary along pixel cracks. Returns the longest closed loop."""
    edges = {}
    for (x, y) in cells:
        if (x, y - 1) not in cells:
            edges.setdefault((x, y), []).append((x + 1, y))
        if (x + 1, y) not in cells:
            edges.setdefault((x + 1, y), []).append((x + 1, y + 1))
        if (x, y + 1) not in cells:
            edges.setdefault((x + 1, y + 1), []).append((x, y + 1))
        if (x - 1, y) not in cells:
            edges.setdefault((x, y + 1), []).append((x, y))

    loops = []
    while edges:
        start = next(iter(edges))
        loop, cur = [start], start
        while True:
            nxts = edges.get(cur)
            if not nxts:
                break
            nxt = nxts.pop()
            if not nxts:
                del edges[cur]
            if nxt == start:
                break
            loop.append(nxt)
            cur = nxt
        if len(loop) > 3:
            loops.append(loop)
    return max(loops, key=len) if loops else None


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    worst, wi = -1.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = (abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / n
             if n else math.hypot(p[0] - a[0], p[1] - a[1]))
        if d > worst:
            worst, wi = d, i
    if worst <= eps:
        return [a, b]
    return rdp(pts[:wi + 1], eps)[:-1] + rdp(pts[wi:], eps)


def simplify_closed(loop, eps):
    o = rdp(loop + [loop[0]], eps)
    return o[:-1] if len(o) > 3 else loop


def area_of(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def is_sliver(poly, min_area=95.0, min_compactness=0.045):
    """Reject hairline artefacts without rejecting genuine small facets.

    A pixel-count threshold cannot tell a real 3px facet from a 30px-long,
    1px-wide hair left behind where two facets nearly touch. Compactness can:
    the hair has almost no area for its perimeter, the facet does.
    """
    a = area_of(poly)
    if a < min_area:
        return True
    per = sum(math.dist(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
    return per <= 0 or (4 * math.pi * a / (per * per)) < min_compactness


# ---------------------------------------------------------------------- main --
def main():
    os.makedirs(PREVIEW, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    src = Image.alpha_composite(Image.new("RGBA", src.size, (255, 255, 255, 255)), src)
    src = src.convert("RGB")

    palette = PALETTE
    print("palette:")
    for c in palette:
        print("   #%02X%02X%02X" % c)

    bird = src.crop((0, 0, src.width, BIRD_ROWS))
    big = bird.resize((bird.width * UPSCALE, bird.height * UPSCALE), Image.LANCZOS)
    W, H = big.size

    lab = quantise(big, palette)
    comps = components(lab, W, H)
    print("regions kept:", len(comps))

    shapes = []
    for val, cells in comps:
        loop = outline(cells)
        if not loop:
            continue
        poly = simplify_closed(loop, RDP_EPS)
        if len(poly) >= 3 and not is_sliver(poly):
            shapes.append((palette[val], poly))
    shapes.sort(key=lambda s: -len(s[1]))
    print("polygons:", len(shapes),
          "avg points:", round(sum(len(p) for _, p in shapes) / max(len(shapes), 1), 1))

    # trim to ink and normalise into a square viewBox
    xs = [p[0] for _, poly in shapes for p in poly]
    ys = [p[1] for _, poly in shapes for p in poly]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    span = max(x1 - x0, y1 - y0)
    s = OUT_W / span
    ox = (OUT_W - (x1 - x0) * s) / 2.0
    oy = (OUT_W - (y1 - y0) * s) / 2.0

    def tx(p):
        return (round((p[0] - x0) * s + ox, 1), round((p[1] - y0) * s + oy, 1))

    body = "\n".join(
        '  <polygon fill="#%02X%02X%02X" points="%s"/>'
        % (c[0], c[1], c[2], " ".join("%g,%g" % tx(p) for p in poly))
        for c, poly in shapes
    )
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
           'role="img" aria-label="FemmForce">\n  <title>FemmForce</title>\n%s\n</svg>\n'
           % (OUT_W, OUT_W, body))
    with open(os.path.join(HERE, "femmforce-bird.svg"), "w", encoding="utf8") as f:
        f.write(svg)

    # previews: traced on white, traced transparent, and a before/after
    for name, bg in (("traced-white.png", (255, 255, 255, 255)),
                     ("traced-transparent.png", (0, 0, 0, 0))):
        im = Image.new("RGBA", (OUT_W, OUT_W), bg)
        d = ImageDraw.Draw(im)
        for c, poly in shapes:
            d.polygon([tx(p) for p in poly], fill=c)
        im.save(os.path.join(PREVIEW, name))

    cmp_im = Image.new("RGB", (OUT_W * 2 + 30, OUT_W), (255, 255, 255))
    old = bird.crop(bird.getbbox() or (0, 0, bird.width, bird.height))
    old = old.resize((OUT_W, int(OUT_W * old.height / old.width)), Image.NEAREST)
    cmp_im.paste(old, (0, (OUT_W - old.height) // 2))
    tr = Image.open(os.path.join(PREVIEW, "traced-white.png")).convert("RGB")
    cmp_im.paste(tr, (OUT_W + 30, 0))
    cmp_im.resize((cmp_im.width // 2, cmp_im.height // 2), Image.LANCZOS) \
          .save(os.path.join(PREVIEW, "before-after.png"))
    print("wrote femmforce-bird.svg + previews")


if __name__ == "__main__":
    main()
