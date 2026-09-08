#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pull candidate photographs from Pexels into candidates/<slot>/ for review.

Nothing here goes near the site. These are candidates only — once you have
picked, the chosen files move into the image pipeline and into assets/img/.

    python tools/fetch_images.py                 # every slot
    python tools/fetch_images.py 03-women-at-work    # one slot
    python tools/fetch_images.py --sheet         # rebuild the picker only

The key is read from .env.local, which is gitignored. It is never printed,
logged, or written anywhere else, and error messages are masked so a failing
request cannot leak it.

Pexels licence: free for commercial use, no attribution required, modification
allowed. Photographer name, profile and source page are still recorded in each
slot's meta.json — crediting the people whose work carries this site is the
decent thing to do even where the licence does not force it, and it is what
feeds the credits page.

Two things that will bite you:

  * Pexels sits behind Cloudflare and returns 403 (error 1010) to Python's
    default user-agent. A browser UA is mandatory, not optional.
  * `total_results` caps at 8000 on almost every query, so it tells you
    nothing about whether the query is any good. Judge by the pictures.
"""

from __future__ import annotations

import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "candidates"
API = "https://api.pexels.com/v1/search"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

PER_SLOT = 12          # how many survive per slot
PER_QUERY = 8          # fetched per query before interleaving

# Which Pexels size to keep. `large2x` is 1880px wide — enough to ship from
# after the resize pass, small enough that 150 of them download in a minute.
# meta.json records the `original` URL so a chosen file can be re-pulled at
# full resolution if a slot ever needs it.
SIZE = "large2x"

# ── slots ───────────────────────────────────────────────────────────────
# Ordered best-query-first. Results are interleaved, so the top hit of every
# query survives the per-slot cap rather than query one filling the folder.
#
# Every query is aimed at the specific page it serves. The brief is Indian
# women — a graduate, a founder, a homemaker, a woman with nothing behind
# her — so "indian" carries most of these deliberately. Generic Western
# stock is the exact thing DESIGN.md §10 warned about.
SLOTS: dict[str, list[str]] = {
    # Page heads and the home page. Wide, confident, not a headshot.
    "01-hero": [
        "indian women group confident",
        "indian woman portrait professional",
        "indian women together outdoors",
        "indian woman smiling workplace",
        "women india city street",
    ],
    # Beneficiaries → Women at Business. Founders and the self-employed.
    "02-women-at-business": [
        "indian woman small business owner",
        "woman entrepreneur india shop",
        "indian woman market seller",
        "female entrepreneur workspace",
        "indian woman boutique owner",
        "woman craft business india",
    ],
    # Beneficiaries → Women at Work. Graduates, professionals, returners.
    "03-women-at-work": [
        "indian woman office professional",
        "indian businesswoman meeting",
        "woman engineer india",
        "indian woman laptop office",
        "female technician working",
        "indian woman graduate",
    ],
    # Beneficiaries → Women at Home. Independence without leaving the house.
    "04-women-at-home": [
        "indian woman sewing machine home",
        "woman working from home india",
        "indian homemaker portrait",
        "woman tailoring business",
        "indian woman home craft work",
    ],
    # Beneficiaries → Underprivileged Women. Livelihood and literacy.
    "05-underprivileged-women": [
        "women self help group india",
        "rural indian women working",
        "indian women farmers",
        "village women india community",
        "indian women group meeting rural",
    ],
    # The nine training pages, and Campus to Corporate.
    "06-training": [
        "vocational training india",
        "women computer training class",
        "training workshop classroom india",
        "instructor teaching adults classroom",
        "skill training hands on workshop",
        "students classroom india",
    ],
    # POSH, Leadership, Soft Skill — the corporate side of the training.
    "07-corporate-training": [
        "corporate training session",
        "business meeting india office",
        "office team discussion women",
        "presentation seminar business",
        "workplace professional women india",
    ],
    # Career Coaching, and the mentoring that runs through every cohort.
    "08-mentoring": [
        "mentoring conversation two women",
        "career counselling session",
        "woman coaching mentor",
        "two women talking desk",
        "interview conversation office",
    ],
    # Our Partners. Corporate, government, institutional collaboration.
    "09-partners": [
        "business handshake partnership",
        "corporate team collaboration",
        "business people meeting room india",
        "signing agreement business",
    ],
    # Membership, and the community side of the trust.
    "10-community-network": [
        "indian women group meeting",
        "women professional networking india",
        "women business group discussion",
        "indian women workshop group",
        "women association meeting india",
    ],
    # Events, and the two event detail pages.
    "11-events": [
        "business conference india audience",
        "women conference speaker",
        "certificate presentation business",
        "workshop event participants",
        "corporate networking event",
        "panel discussion women",
    ],
    # Bengaluru. The trust is a Bangalore trust and the site has nothing local.
    "12-bengaluru": [
        "bangalore india city",
        "bengaluru street",
        "india city architecture modern",
        "bangalore skyline",
    ],
    # Small close detail, used as texture between sections. No faces.
    "13-texture-detail": [
        "hands working close up craft",
        "sewing thread fabric close up",
        "notebook pen desk minimal",
        "indian textile fabric detail",
    ],
}


def say(s: str) -> None:
    """The Windows console is cp1252 and Pexels alt text is not. Printing a
    photographer name with an accent in it killed a whole run once, after the
    downloads had already succeeded - so console output is forced to ASCII."""
    sys.stdout.write(s.encode("ascii", "replace").decode("ascii") + "\n")


def key() -> str:
    env = ROOT / ".env.local"
    if not env.exists():
        sys.exit("No .env.local. Put PEXELS_API_KEY=... in it (it is gitignored).")
    for line in io.open(env, encoding="utf-8"):
        if line.startswith("PEXELS_API_KEY="):
            k = line.split("=", 1)[1].strip()
            if k:
                return k
    sys.exit("PEXELS_API_KEY missing from .env.local")


def search(k: str, query: str, per_page: int) -> list[dict]:
    url = API + "?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": "landscape",
         "size": "large"})
    req = urllib.request.Request(url, headers={"Authorization": k, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("photos", [])
    except urllib.error.HTTPError as e:
        # Masked deliberately: the request carries the key in a header.
        say("    ! query %-38s HTTP %s" % (query[:38], e.code))
        return []
    except Exception as e:
        say("    ! query %-38s %s" % (query[:38], type(e).__name__))
        return []


def download(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


def interleave(groups: list[list[dict]], cap: int) -> list[dict]:
    """Take the best hit of every query, then the second of every query, and
    so on — so one broad query cannot crowd out a sharper one."""
    out, seen, i = [], set(), 0
    while len(out) < cap and any(i < len(g) for g in groups):
        for g in groups:
            if i < len(g) and len(out) < cap:
                p = g[i]
                if p["id"] not in seen:
                    seen.add(p["id"])
                    out.append(p)
        i += 1
    return out


def do_slot(k: str, slot: str, queries: list[str]) -> None:
    d = OUT / slot
    d.mkdir(parents=True, exist_ok=True)
    say("\n%s" % slot)

    groups = []
    for q in queries:
        photos = search(k, q, PER_QUERY)
        for p in photos:
            p["_q"] = q
        groups.append(photos)
        time.sleep(0.3)

    picked = interleave(groups, PER_SLOT)
    meta = []
    for n, p in enumerate(picked, 1):
        name = "%02d.jpg" % n
        try:
            kb = download(p["src"][SIZE], d / name) // 1024
        except Exception as e:
            say("    ! download %s %s" % (name, type(e).__name__))
            continue
        meta.append({
            "n": n, "file": name,
            "photographer": p.get("photographer", ""),
            "photographer_url": p.get("photographer_url", ""),
            "page": p.get("url", ""),
            "original": p["src"].get("original", ""),
            "alt": (p.get("alt") or "").strip(),
            "w": p.get("width"), "h": p.get("height"),
            "query": p.get("_q", ""), "kb": kb,
        })
        say("    %s  %4dKB  %-20s %s" % (
            name, kb, meta[-1]["photographer"][:20], meta[-1]["alt"][:52]))

    with io.open(d / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
    say("    -> %d images" % len(meta))


# ── the picker ──────────────────────────────────────────────────────────
SHEET_CSS = """
:root{--bg:#F3F1ED;--bg-1:#EAE7E1;--tx:#171412;--tx-2:#585149;--tx-3:#8B8279;
  --line:rgba(23,20,18,.13);--verm:#EC4008}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
  font:14px/1.5 "Familjen Grotesk",system-ui,sans-serif}
header{padding:34px 30px 18px;border-bottom:1px solid var(--line)}
h1{margin:0 0 .5rem;font-size:1.6rem;letter-spacing:-.04em;text-transform:uppercase}
header p{margin:0;color:var(--tx-2);max-width:70ch}
h2{margin:0 0 2px;font-size:1.05rem;letter-spacing:-.03em;text-transform:uppercase}
section{padding:30px}
section + section{border-top:1px solid var(--line)}
.q{margin:0 0 16px;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--tx-3)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
figure{margin:0;background:var(--bg-1);border:1px solid var(--line);border-radius:12px;
  overflow:hidden}
figure img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover}
figcaption{padding:8px 10px;font-size:.72rem;color:var(--tx-3);line-height:1.35}
figcaption b{display:block;font-size:.9rem;color:var(--tx);letter-spacing:.06em}
figcaption i{font-style:normal;color:var(--tx-2)}
a{color:var(--verm)}
"""


def build_sheet() -> None:
    parts = ["<!doctype html><html lang=en><meta charset=utf-8>",
             "<title>FemmForce — image candidates</title>",
             "<style>%s</style>" % SHEET_CSS,
             "<header><h1>FemmForce &mdash; image candidates</h1>",
             "<p>Every photograph below is from Pexels: free for commercial use, "
             "modification allowed, <b>no attribution required</b>. Photographer is "
             "recorded anyway and will go on the credits page. Pick by the code under "
             "each image, e.g. <code>03-women-at-work / 07</code>.</p></header>"]
    total = 0
    for slot in sorted(SLOTS):
        mp = OUT / slot / "meta.json"
        if not mp.exists():
            continue
        meta = json.load(io.open(mp, encoding="utf-8"))
        total += len(meta)
        parts.append("<section><h2>%s</h2><p class=q>%d images</p><div class=grid>"
                     % (slot, len(meta)))
        for e in meta:
            parts.append(
                '<figure><img loading=lazy src="%s/%s" alt="">'
                '<figcaption><b>%s / %02d</b><i>%s</i><br>%s</figcaption></figure>'
                % (slot, e["file"], slot, e["n"],
                   (e.get("alt") or "&mdash;")[:96], e.get("photographer", "")))
        parts.append("</div></section>")
    parts.append("<section><p class=q>%d candidates total</p></section></html>" % total)
    (OUT / "index.html").write_text("\n".join(parts), encoding="utf-8")
    say("\ncandidates/index.html  —  %d candidates" % total)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "--sheet" in args:
        build_sheet()
        sys.exit(0)
    k = key()
    wanted = [a for a in args if not a.startswith("-")] or list(SLOTS)
    OUT.mkdir(exist_ok=True)
    for slot in wanted:
        if slot not in SLOTS:
            say("unknown slot: %s" % slot)
            continue
        do_slot(k, slot, SLOTS[slot])
    build_sheet()
