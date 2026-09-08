#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turn candidates/ into something the client can open on a phone.

`candidates/` is 43MB of 1880px JPEGs and is gitignored — it is a working set,
not site content. But the client has to be able to see the photographs to pick
them, and the only place they will reliably open a link is the live site.

So this writes a small, committed review set:

    assets/img/select/<slot>-<nn>.webp   700px WebP, ~30-60KB each
    assets/img/select/manifest.json      codes, photographer, alt text

which `tools/build.py` turns into `select.html`. About 6MB total, which loads
on a phone on Indian mobile data. Full resolution stays in candidates/ and the
Pexels `original` URL is in each slot's meta.json, so a chosen photograph is
re-pulled at full size when it goes into a real slot.

    python tools/build_select.py

Delete assets/img/select/ and the footer link once the picking is done.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is needed: python -m pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "candidates"
OUT = ROOT / "assets" / "img" / "select"

WIDTH = 700
QUALITY = 72

# What each slot is for, in the client's language rather than the repo's.
PURPOSE = {
    "01-hero": "Home page and page headers",
    "02-women-at-business": "Women at Business",
    "03-women-at-work": "Women at Work",
    "04-women-at-home": "Women at Home",
    "05-underprivileged-women": "Underprivileged Women",
    "06-training": "Training pages",
    "07-corporate-training": "POSH, Leadership and Soft Skill training",
    "08-mentoring": "Career Coaching and mentoring",
    "09-partners": "Our Partners",
    "10-community-network": "Membership and community",
    "11-events": "Events",
    "12-bengaluru": "Bengaluru — local photographs",
    "13-texture-detail": "Small detail images between sections",
}


def main() -> None:
    if not CAND.exists():
        sys.exit("No candidates/ folder. Run tools/fetch_images.py first.")

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.webp"):
        old.unlink()

    manifest = []
    total = 0
    for slot_dir in sorted(CAND.iterdir()):
        meta_path = slot_dir / "meta.json"
        if not slot_dir.is_dir() or not meta_path.exists():
            continue
        slot = slot_dir.name
        meta = json.load(io.open(meta_path, encoding="utf-8"))
        kept = []
        for e in meta:
            src = slot_dir / e["file"]
            if not src.exists():
                continue
            name = "%s-%02d.webp" % (slot, e["n"])
            with Image.open(src) as im:
                im = im.convert("RGB")
                h = round(im.height * WIDTH / im.width)
                im.resize((WIDTH, h), Image.LANCZOS).save(
                    OUT / name, "WEBP", quality=QUALITY, method=6)
            kb = (OUT / name).stat().st_size // 1024
            total += kb
            kept.append({
                "code": "%s / %02d" % (slot, e["n"]),
                "file": name,
                "alt": e.get("alt", ""),
                "photographer": e.get("photographer", ""),
                "page": e.get("page", ""),
            })
        if kept:
            manifest.append({"slot": slot,
                             "purpose": PURPOSE.get(slot, ""),
                             "images": kept})
            print("%-26s %2d images" % (slot, len(kept)))

    with io.open(OUT / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)

    n = sum(len(g["images"]) for g in manifest)
    print("\n%d thumbnails, %.1f MB total -> %s" % (n, total / 1024, OUT))


if __name__ == "__main__":
    main()
