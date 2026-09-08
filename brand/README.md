# FemmForce — brand assets

Everything here is generated from `femmforce-bird.svg`, the master vector traced
from the client's own artwork. Nothing is hand-drawn.

To change the mark, edit the trace and re-run both scripts in order:

```bash
python trace_logo.py     # source PNG  ->  femmforce-bird.svg
python build_assets.py   # master SVG  ->  every asset below
```

## Colour

| Role | Hex | Where it appears |
|---|---|---|
| Deep red | `#C81E14` | Shards, wing tips |
| Vermilion | `#EC4008` | Wing blades. **The primary brand colour** |
| Orange | `#F0731A` | Body |
| Gold | `#DBA22E` | Head and beak |
| Ink | `#141210` | Wordmark |

Measured from the highest-chroma pixels in the source artwork, not sampled by
eye and not guessed.

### On dark backgrounds

Use the `-dark-bg` / `-ondark` variants. The deep red sits at roughly **2.5:1**
against `#141210`, which fails contrast and makes the bird's head disappear on a
dark header. The dark set lifts each colour in value while holding its hue:

`#C81E14`→`#E63A2E` · `#EC4008`→`#F4551E` · `#F0731A`→`#F58A33` · `#DBA22E`→`#E8B449`

## Files

### `svg/` — vector, scales to any size
- `mark-colour.svg` — the full mark. Default choice.
- `mark-dark-bg.svg` — lifted palette for dark grounds.
- `mark-black.svg` / `mark-white.svg` — single-colour, for stamping, embroidery, fax-grade reproduction.
- `mark-compact.svg` — 17 largest facets, for small sizes.

### `png/`
- `mark-256/512/1024.png` — transparent.
- `mark-dark-512.png` — lifted palette.
- `lockup-vertical-1x/2x/3x.png` and `lockup-horizontal-*` — transparent.
- `lockup-vertical-onwhite.png`, `lockup-horizontal-ondark.png`.

### `favicon/`
- `favicon.ico` — 16/32/48. **This is a solid silhouette, not the faceted mark**, and that is deliberate: below about 40px every facet and every white gap falls under one pixel and the mark greys out to a smudge.
- `icon-96/192/512.png` — full colour, used where the facets still read.
- `apple-touch-icon.png` — 180px, padded, on white. iOS ignores transparency and clips to a rounded square.
- `site.webmanifest` — paths assume the kit is served at `/brand/`.

### `social/`
- `og-1200x630.png` — link previews.
- `avatar-1000.png`, `avatar-dark-1000.png` — square profile images.
- `linkedin-banner.png` — 1584×396.

## Rules

**Clear space.** Keep free space on all sides equal to the height of the bird's
head. Nothing intrudes into it.

**Minimum size.** Full mark: 40px tall on screen, 15mm in print. Below that use
`mark-compact.svg`; below 32px use the silhouette.

**Don't:** recolour the mark outside these palettes, add effects or shadows,
rotate it, stretch it non-uniformly, box it in a coloured tile, or place the
colour version on a mid-toned background where the gold stops separating.

## Two things still open

1. **The wordmark typeface is a stand-in.** These files set "FEMMFORCE" in Arial
   Black. The real logo uses a squared geometric sans that I could not identify,
   and text in the 124×102 source is far too small to trace. Supply the correct
   font and re-run `build_assets.py` — drop the `.ttf` in this folder and add its
   filename to `FONT_CANDIDATES`. Otherwise Archivo Black is the recommended
   substitute: free, close in character, and already the display face on the site.

2. **The white gaps between facets are cut through to transparency.** Correct on
   light grounds. On dark grounds the gaps go dark and the bird reads as
   scattered shards rather than one body. If that is not wanted, the fix is to
   put the mark on a white or light tile in dark contexts.

## Source provenance

Traced from a 124×102 PNG in which the bird occupies roughly **86×64 px**. The
geometry is faithful to that source, but detail finer than about 2px — most
visibly the separation between wing blades and the taper of the gold beak — was
not present to recover. If original vector artwork (`.ai`, `.eps`, `.svg`, `.cdr`)
ever turns up, re-tracing from it will sharpen every asset here.
