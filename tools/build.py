#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FemmForce — page generator.

The site ships as plain static HTML (see DESIGN.md §3): no build step at
deploy time, no bundler, no backend. This script exists only because the
masthead and footer are duplicated across 27 pages, and hand-editing 27
copies of a nav is how a nav goes out of sync.

    python tools/build.py

It writes every .html file at the repo root and nothing else. The output is
committed; GitHub Pages serves the output, never this script. If you would
rather edit the HTML by hand, delete this file — the pages stand alone.

Copy source: FemmForce-Website-Content.docx (verbatim extraction of the 26
original Wix pages). Where a line here is not in that document it is a
connective sentence written for this build; those are marked  # authored.
"""

import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIL = "info@femmforce.in"
PHONE_HREF = "tel:+919880438607"
PHONE = "+91 98804 38607"


def mailto(subject):
    return "mailto:%s?subject=%s" % (MAIL, subject.replace(" ", "%20").replace("&", "%26"))


# ── site map ────────────────────────────────────────────────────────────
# key -> (filename, short label used in the pager and the crumb)
COHORTS = [
    ("women-at-business", "women-at-business.html", "Women at Business", "acc-biz",
     "Founders, and the women about to become one"),
    ("women-at-work", "women-at-work.html", "Women at Work", "acc-work",
     "Graduates, professionals, and returners"),
    ("women-at-home", "women-at-home.html", "Women at Home", "acc-home",
     "Independence without leaving the house"),
    ("underprivileged-women", "underprivileged-women.html", "Underprivileged Women", "acc-und",
     "Livelihood, literacy and government schemes"),
]

TRAINING = [
    ("training-posh", "training-posh.html", "POSH Training",
     "Compliance under the 2013 Act"),
    ("training-soft-skills", "training-soft-skills.html", "Soft Skill Training",
     "Communication and teamwork"),
    ("training-it-technical", "training-it-technical.html", "IT &amp; Technical",
     "Programming, networks, security"),
    ("training-career-coaching", "training-career-coaching.html", "Career Coaching",
     "Assessment and counselling"),
    ("training-sales", "training-sales.html", "Sales Training",
     "Gender-inclusive sales practice"),
    ("training-leadership", "training-leadership.html", "Leadership Training",
     "Decisions, teams, performance"),
    ("training-customised", "training-customised.html", "Customised Training",
     "Built to one organisation"),
    ("training-campus-to-corporate", "training-campus-to-corporate.html", "Campus to Corporate",
     "Graduates into a first role"),
    ("training-train-the-trainers", "training-train-the-trainers.html", "Train the Trainers",
     "Content design and delivery"),
]

MEDIA = [
    ("media-videos", "media-videos.html", "Videos", "Talks and event footage"),
    ("media-photos", "media-photos.html", "Photos", "From the programmes"),
    ("media-posh-trainers", "media-posh-trainers.html", "POSH Trainer Programme",
     "Trainee cohort gallery"),
]


# ── masthead ────────────────────────────────────────────────────────────
def _drop(items, extra=""):
    out = []
    for it in items:
        cls, href, name, desc = it
        out.append(
            '        <a class="%s" href="%s"><u></u><span><b>%s</b>\n'
            '          <i>%s</i></span></a>' % (cls, href, name, desc))
    return ('      <div class="drop%s">\n' % extra) + "\n".join(out) + "\n      </div>"


def nav(active):
    """active is a page key; the matching top-level item gets .on"""
    def on(*keys):
        return " on" if active in keys else ""

    cohort_items = [("d-biz" if k == "women-at-business" else
                     "d-work" if k == "women-at-work" else
                     "d-home" if k == "women-at-home" else "d-und",
                     f, n, d) + () for (k, f, n, _c, d) in COHORTS]
    cohort_items = [(c + (" on" if COHORTS[i][0] == active else ""), f, n, d)
                    for i, (c, f, n, d) in enumerate(cohort_items)]

    train_items = [(("on" if k == active else ""), f, n, d) for (k, f, n, d) in TRAINING]
    media_items = [(("on" if k == active else ""), f, n, d) for (k, f, n, d) in MEDIA]

    return """  <nav id="nav">
    <span class="nav-ind" aria-hidden="true"></span>

    <div class="nav-i%s"><a href="about-us.html">About</a></div>
    <div class="nav-i%s"><a href="our-activities.html">Activities</a></div>

    <div class="nav-i has%s"><a href="women-at-business.html">Beneficiaries</a>
%s
    </div>

    <div class="nav-i has%s"><a href="how-we-do.html">How We Do</a>
      <div class="drop">
        <a href="how-we-do.html#grant-wave"><u></u><span><b>Grant Wave</b>
          <i>Funding through grants, donors and CSR</i></span></a>
        <a href="how-we-do.html#skill-fund"><u></u><span><b>Skill Fund</b>
          <i>Funding through corporate training</i></span></a>
      </div>
    </div>

    <div class="nav-i%s"><a href="our-partners.html">Partners</a></div>
    <div class="nav-i%s"><a href="membership.html">Membership</a></div>

    <div class="nav-i has%s"><a href="how-we-do.html#training">Training</a>
%s
    </div>

    <div class="nav-i has%s"><a href="media-videos.html">Media</a>
%s
    </div>

    <div class="nav-i%s"><a href="events.html">Events</a></div>
    <a class="nav-mob-cta" href="#donate">Donate Now</a>
  </nav>""" % (
        on("about-us"), on("our-activities"),
        on(*[c[0] for c in COHORTS]), _drop(cohort_items),
        on("how-we-do"),
        on("our-partners"), on("membership"),
        on(*[t[0] for t in TRAINING]), _drop(train_items, " two"),
        on(*[m[0] for m in MEDIA]), _drop(media_items),
        on("events", "event-ubuntu-consortium", "event-femmforce"),
    )


def masthead(active):
    return """<header class="mast"><div class="wrap"><div class="bar">
  <a class="brand" href="index.html"><img src="brand/svg/mark-colour.svg" alt=""><b>FemmForce</b></a>

%s

  <a class="nav-cta" href="#donate"><span>Donate Now</span></a>

  <button class="burger" aria-expanded="false" aria-controls="nav" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</div></div></header>""" % nav(active)


FOOTER = """<footer><div class="wrap">
  <div class="fgrid">
    <div>
      <a class="brand" href="index.html" style="margin-bottom:1.4rem">
        <img src="brand/svg/mark-colour.svg" alt="" style="width:46px;height:46px">
        <b style="color:var(--tx)">FemmForce</b>
      </a>
      <p style="font-size:1rem;color:var(--tx-3)">#1, AECS Layout A Block,<br>Singasandra,
        Bangalore &ndash; 560 068</p>
    </div>
    <div><h4>Beneficiaries</h4><ul>
      <li><a href="women-at-business.html">Women at Business</a></li>
      <li><a href="women-at-work.html">Women at Work</a></li>
      <li><a href="women-at-home.html">Women at Home</a></li>
      <li><a href="underprivileged-women.html">Underprivileged Women</a></li>
    </ul></div>
    <div><h4>Organisation</h4><ul>
      <li><a href="about-us.html">About Us</a></li>
      <li><a href="our-activities.html">Our Activities</a></li>
      <li><a href="how-we-do.html">How We Do</a></li>
      <li><a href="how-we-do.html#training">Training Programmes</a></li>
      <li><a href="our-partners.html">Our Partners</a></li>
      <li><a href="membership.html">Membership</a></li>
      <li><a href="brochures-and-forms.html">Brochures &amp; Forms</a></li>
      <li><a href="events.html">Events</a></li>
      <li><a href="blog.html">Blog</a></li>
    </ul></div>
    <div><h4>Contact</h4><ul>
      <li><a href="mailto:info@femmforce.in">info@femmforce.in</a></li>
      <li><a href="tel:+919880438607">+91 98804 38607</a></li>
      <li><a href="https://www.instagram.com/femmforce_ngo/" rel="noopener">Instagram</a></li>
      <li><a href="https://www.facebook.com/profile.php?id=61550254960559" rel="noopener">Facebook</a></li>
      <li><a href="https://twitter.com/femmforceworld" rel="noopener">X / Twitter</a></li>
    </ul></div>
  </div>
  <div class="fbot">
    <span>&copy; 2026 FemmForce. All rights reserved.</span>
    <span>Registered trust &middot; Bangalore, India</span>
  </div>
</div></footer>"""


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="icon" href="brand/favicon/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<script>document.documentElement.className+=" js"</script>
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body%(bodycls)s>

<div class="prog" aria-hidden="true"></div>

"""


def document(slug, title, desc, active, body, bodycls=""):
    cls = ' class="%s"' % bodycls if bodycls else ""
    html = (HEAD % {"title": title, "desc": desc, "bodycls": cls}
            + masthead(active) + "\n\n" + body.strip() + "\n\n" + FOOTER
            + '\n\n<script src="assets/js/site.js" defer></script>\n</body>\n</html>\n')
    with io.open(os.path.join(ROOT, slug), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return slug


# ── section helpers ─────────────────────────────────────────────────────
def hero(crumb, lines, lede, auras=3):
    """crumb: list of (label, href|None). lines: the headline, one per line."""
    bits = []
    for i, (label, href) in enumerate(crumb):
        if i:
            bits.append("<i>/</i>")
        bits.append('<a href="%s">%s</a>' % (href, label) if href else "<span>%s</span>" % label)
    lns = "\n      ".join('<span class="ln"><i>%s</i></span>' % l for l in lines)
    return """<section class="hero page">
  <div class="aura" aria-hidden="true">%s</div>
  <div class="wrap">
    <p class="crumb">%s</p>
    <h1>
      %s
    </h1>
    <p class="lede">%s</p>
  </div>
</section>""" % ("<b></b>" * auras, "".join(bits), lns, lede)


def section(inner, ident="", style="", cls=""):
    a = ' id="%s"' % ident if ident else ""
    b = ' class="%s"' % cls if cls else ""
    c = ' style="%s"' % style if style else ""
    return "<section%s%s%s><div class=\"wrap\">\n%s\n</div></section>" % (a, b, c, inner)


def head2(kicker, heading, intro="", width="18ch"):
    out = '  <p class="lbl" data-rv="rise">%s</p>\n' % kicker
    out += '  <h2 data-rv="mask" style="margin-bottom:%s;max-width:%s">%s</h2>\n' % (
        "1.1rem" if intro else "2.8rem", width, heading)
    if intro:
        out += ('  <p data-rv="rise" style="margin-bottom:3rem;max-width:52ch;'
                'color:var(--tx-2);font-size:var(--t-lede)">%s</p>\n' % intro)
    return out


def cells(items, cls="", numbered=True):
    """items: (title, body_html[, extra_html[, href]]).
    With an href the cell becomes a link; the panel styling is identical."""
    out = ['  <div class="cells%s">' % (" " + cls if cls else "")]
    for i, it in enumerate(items):
        title, body = it[0], it[1]
        extra = it[2] if len(it) > 2 else ""
        href = it[3] if len(it) > 3 else None
        n = '<span class="n">%02d</span>' % (i + 1) if numbered else ""
        tag = ('<a href="%s" data-rv="rise">' % href) if href else '<div data-rv="rise">'
        out.append('    %s%s<h3>%s</h3>%s%s</%s>'
                   % (tag, n, title, body, extra, "a" if href else "div"))
    out.append("  </div>")
    return "\n".join(out)


def checks(items):
    lis = "\n".join("    <li>%s</li>" % i for i in items)
    return '  <ul class="checks" data-rv="rise">\n%s\n  </ul>' % lis


def bullets(items):
    return "<ul>\n" + "\n".join("      <li>%s</li>" % i for i in items) + "\n    </ul>"


def index_rows(rows):
    """rows: (href, title, desc) — the numbered list component"""
    out = ['  <div class="index">']
    for i, (href, title, desc) in enumerate(rows):
        out.append('    <a href="%s" data-rv="rise"><span class="n">%02d</span>'
                   '<span class="t">%s</span><span class="d">%s</span></a>'
                   % (href, i + 1, title, desc))
    out.append("  </div>")
    return "\n".join(out)


def pager(prev, nxt):
    """prev / nxt: (href, label) or None"""
    def cell(side, item, word):
        if not item:
            return ('  <div class="%s none"><span>%s</span><b>&mdash;</b></div>'
                    % (side, word))
        return ('  <a class="%s" href="%s"><span>%s</span><b>%s</b></a>'
                % (side, item[0], word, item[1]))
    return ('<section style="padding-top:0"><div class="wrap">\n'
            '  <div class="pager">\n%s\n%s\n  </div>\n</div></section>'
            % (cell("prev", prev, "Previous"), cell("next", nxt, "Next")))


def cta(heading, lede, buttons):
    btns = "\n".join(
        '      <a class="btn%s" href="%s"><span>%s</span></a>'
        % (" btn-solid" if i == 0 else "", href, label)
        for i, (href, label) in enumerate(buttons))
    return """<section class="cta">
  <div class="aura" aria-hidden="true" style="opacity:.45"><b></b><b></b></div>
  <div class="wrap">
    <p class="lbl" data-rv="rise">Get in touch</p>
    <h2 data-rv="mask">%s</h2>
    <p class="lede" data-rv="rise">%s</p>
    <div class="acts" data-rv="rise" style="opacity:1;transform:none">
%s
    </div>
  </div>
</section>""" % (heading, lede, btns)


GENERAL_CTA = cta(
    "Work with us.",
    "Train your organisation, partner with the trust, or fund a place for a woman "
    "who cannot pay for one.",
    [(mailto("FemmForce enquiry"), "Email the trust"),
     ("membership.html", "Become a member"),
     ("our-partners.html", "Partner with us")])


def training_cta(name):
    return cta(
        "Bring this to your team.",
        "%s is delivered on site, online, and in multiple languages, to corporates "
        "and institutions across India." % name,
        [(mailto("Training enquiry — " + re.sub("&amp;", "and", name)),
          "Register your interest"),
         ("how-we-do.html#training", "All nine programmes")])


# ══ PAGES ═══════════════════════════════════════════════════════════════
pages = []

# ── Home ────────────────────────────────────────────────────────────────
INDEX_BODY = """<section class="hero">
  <div class="aura" aria-hidden="true">
    <b></b><b></b><b></b><b></b><b></b><b></b>
  </div>
  <canvas class="field" aria-hidden="true"></canvas>
  <div class="wrap">
    <h1>
      <span class="ln"><i>A force</i></span>
      <span class="ln"><i>for women.</i></span>
      <span class="ln"><i><em>All</em> of them.</i></span>
    </h1>
    <p class="lede">FemmForce is a registered trust in Bangalore. We train women, fund
      them, place them into work, and make workplaces safe under the law &mdash; whoever she
      is, wherever she starts.</p>
    <div class="acts">
      <a class="btn btn-solid" href="#cohorts"><span>Find your programme</span></a>
      <a class="btn" href="#training"><span>Train your organisation</span></a>
    </div>
    <p class="cue">Scroll</p>
  </div>
</section>

<section class="band"><div class="wrap">
  <p class="lbl" data-rv="rise">About us</p>
  <div class="cols">
    <p class="stmt" data-rv="mask">A society where women thrive &mdash; and where the barriers
      that stop them are removed, not discussed.</p>
    <div class="body" data-rv="rise">
      <p>FemmForce empowers women with essential skills, leadership opportunities and the
        support to excel in diverse fields. By addressing barriers and promoting inclusion,
        we work toward a society where women achieve remarkable success.</p>
      <p>Our programmes develop talent, build confidence and create recognition &mdash; a more
        supportive environment, built deliberately rather than hoped for.</p>
      <p style="margin-bottom:0"><a class="sub-link" href="about-us.html"
        style="font-weight:600;color:var(--tx);border-bottom:1px solid var(--line-2)">Read
        more about the trust</a></p>
    </div>
  </div>
</div></section>

<section id="cohorts"><div class="wrap">
  <p class="lbl" data-rv="rise">Who we work with</p>
  <h2 data-rv="mask" style="margin-bottom:1rem;max-width:14ch">Wherever you are starting from.</h2>
  <p data-rv="rise" style="margin-bottom:3rem;max-width:46ch;color:var(--tx-2);font-size:var(--t-lede)">
    A founder, a graduate, a homemaker, a woman with nothing behind her &mdash; there is a
    programme for each.</p>

  <div class="cohorts">
    <a class="cohort c-biz" href="women-at-business.html" data-rv="rise"><div class="row">
      <span class="idx">01</span>
      <span class="shards" aria-hidden="true"><i></i><i></i><i></i></span>
      <div>
        <h3>Women at Business</h3>
        <p class="who">Startup Divas &middot; Maverick Divas &middot; Aspiring Divas</p>
      </div>
      <p class="desc">Workshops, mentoring, funding routes and supplier-diversity access
        for women who are building something of their own.</p>
      <span class="ring" aria-hidden="true"></span>
    </div></a>

    <a class="cohort c-work" href="women-at-work.html" data-rv="rise"><div class="row">
      <span class="idx">02</span>
      <span class="shards" aria-hidden="true"><i></i><i></i><i></i></span>
      <div>
        <h3>Women at Work</h3>
        <p class="who">Rising Stars &middot; Career Thrivers &middot; Career Re-entry</p>
      </div>
      <p class="desc">Finishing school for graduates, upskilling mid-career, and a way
        back in after a break or a sabbatical.</p>
      <span class="ring" aria-hidden="true"></span>
    </div></a>

    <a class="cohort c-home" href="women-at-home.html" data-rv="rise"><div class="row">
      <span class="idx">03</span>
      <span class="shards" aria-hidden="true"><i></i><i></i><i></i></span>
      <div>
        <h3>Women at Home</h3>
        <p class="who">Divas at Home</p>
      </div>
      <p class="desc">Financial independence, mental health, legal rights and healthcare
        access &mdash; plus a network that does not require an office to join.</p>
      <span class="ring" aria-hidden="true"></span>
    </div></a>

    <a class="cohort c-und" href="underprivileged-women.html" data-rv="rise"><div class="row">
      <span class="idx">04</span>
      <span class="shards" aria-hidden="true"><i></i><i></i><i></i></span>
      <div>
        <h3>Underprivileged Women</h3>
        <p class="who">Livelihood &amp; literacy</p>
      </div>
      <p class="desc">Financial literacy, community livelihood support, help navigating
        government schemes, and a route to economic independence.</p>
      <span class="ring" aria-hidden="true"></span>
    </div></a>
  </div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <div class="facts">
    <div data-count="300"><b>300<em>+</em></b><span>Qualified trainers in the network</span></div>
    <div data-count="20"><b>20<em>+</em></b><span>Organisations served under POSH</span></div>
    <div data-count="9"><b>9</b><span>Training programmes delivered</span></div>
    <div data-count="4"><b>4</b><span>Groups of women supported</span></div>
  </div>
</div></section>

<section style="background:var(--bg-1);border-top:1px solid var(--line)"><div class="wrap">
  <p class="lbl" data-rv="rise">How we do it</p>
  <h2 data-rv="mask" style="margin-bottom:2.8rem;max-width:15ch">The free work is paid for by the paid work.</h2>
  <div class="two">
    <div data-rv="rise">
      <h3>Grant Wave</h3>
      <p>Funds through grants and donations. We work with donors and the CSR heads of
        corporates, NGOs, consortiums and foundations who want to contribute directly to
        women&rsquo;s programmes.</p>
      <p style="margin:1.3rem 0 0"><a href="how-we-do.html#grant-wave"
        style="font-weight:600;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;
        border-bottom:1px solid var(--line-2)">Read more</a></p>
    </div>
    <div data-rv="rise" style="--d:130ms">
      <h3>Skill Fund</h3>
      <p>Funds through training. Industry experts contribute a portion of their earnings
        from corporate and institutional training back into the trust &mdash; which is what keeps
        the free programmes running.</p>
      <p style="margin:1.3rem 0 0"><a href="how-we-do.html#skill-fund"
        style="font-weight:600;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;
        border-bottom:1px solid var(--line-2)">Read more</a></p>
    </div>
  </div>
</div></section>

<section id="training"><div class="wrap">
  <p class="lbl" data-rv="rise">Training</p>
  <h2 data-rv="mask" style="margin-bottom:3rem;max-width:18ch">Nine programmes for companies and institutions.</h2>
%(training_index)s
</div></section>

<div class="marq" aria-label="Partner categories">
  <ul>
    <li>Corporate</li><li>Non-Profit &amp; Institutions</li><li>Government</li>
    <li>Knowledge Partners</li><li>Interns</li><li>Employment Partners</li>
    <li>NRI / HNI</li><li>Trade Bodies</li><li>Volunteers</li>
    <li aria-hidden="true">Corporate</li><li aria-hidden="true">Non-Profit &amp; Institutions</li>
    <li aria-hidden="true">Government</li><li aria-hidden="true">Knowledge Partners</li>
    <li aria-hidden="true">Interns</li><li aria-hidden="true">Employment Partners</li>
    <li aria-hidden="true">NRI / HNI</li><li aria-hidden="true">Trade Bodies</li>
    <li aria-hidden="true">Volunteers</li>
  </ul>
</div>

<section><div class="wrap">
  <p class="lbl" data-rv="rise">Trustees</p>
  <h2 data-rv="mask" style="margin-bottom:3rem;max-width:13ch">The people behind it.</h2>
  <div class="people">
    <article>
      <h3>Uma G Reddy</h3>
      <p class="role">Trustee &amp; Founder</p>
      <p>Serial entrepreneur, MBA in Marketing &amp; HR, twenty years in the corporate
        world and a decade in business. Founder CEO at Hiring Studios. Started FemmForce
        on the view that businesses want implementation, not commentary.</p>
    </article>
    <article style="--d:130ms">
      <h3>Narasimhan M.V</h3>
      <p class="role">Trustee</p>
      <p>Three decades in HR and management across manufacturing, hospitality, textiles,
        logistics and education. Builds the networks that put people into jobs.</p>
    </article>
    <article style="--d:260ms">
      <h3>Jaya Reddy</h3>
      <p class="role">Executive Director</p>
      <p>MBA (HR), fifteen years across corporates and NGOs, entrepreneur, and six years
        volunteering with Lions Clubs International across India.</p>
    </article>
  </div>
  <p style="margin-top:2.6rem" data-rv="rise"><a class="btn" href="about-us.html"
    ><span>More about the trust</span></a></p>
</div></section>

<section class="signup">
  <div class="aura" aria-hidden="true" style="opacity:.5"><b></b><b></b></div>
  <div class="wrap">
    <p class="lbl" data-rv="rise">Get in touch</p>
    <h2 data-rv="mask">Hear what we do next.</h2>
    <form onsubmit="return false">
      <input type="email" placeholder="Enter your email here" aria-label="Email address">
      <button type="submit">Subscribe</button>
    </form>
  </div>
</section>""" % {
    "training_index": index_rows([
        (TRAINING[0][1], "POSH Training",
         "External Internal-Committee members and full compliance under the 2013 Act. "
         "Delivered to more than 20 organisations across India."),
        (TRAINING[1][1], "Soft Skill Training",
         "Communication, teamwork, conflict resolution, time and stress management."),
        (TRAINING[2][1], "IT &amp; Technical",
         "Programming, networking, cyber security, and certification tracks."),
        (TRAINING[3][1], "Career Coaching",
         "Five-dimensional assessment, one-to-one counselling, and an execution plan."),
        (TRAINING[4][1], "Sales Training",
         "Gender-inclusive sales practice &mdash; goal setting, presentation, objection handling."),
        (TRAINING[5][1], "Leadership Training",
         "Conflict resolution, virtual leadership, and coaching for performance."),
        (TRAINING[6][1], "Customised Training",
         "Built to a specific organisation, department or industry."),
        (TRAINING[7][1], "Campus to Corporate",
         "Graduates into their first role &mdash; etiquette, interviews, presentation."),
        (TRAINING[8][1], "Train the Trainers",
         "Training-need analysis, content design, public speaking, and delivery."),
    ])
}

pages.append(document(
    "index.html", "FemmForce — A force for women.",
    "FemmForce is a registered trust in Bangalore. We train women, fund them, place them "
    "into work, and make workplaces safe under the law.",
    "home", INDEX_BODY))


# ── About Us ────────────────────────────────────────────────────────────
about = "\n\n".join([
    hero([("Home", "index.html"), ("About us", None)],
         ["A stepping stone", "for women who", "intend to rise."],
         "FemmForce empowers women with essential skills, leadership opportunities and the "
         "support to excel in diverse fields. By addressing barriers and promoting "
         "inclusion, we work toward a society where women achieve remarkable success."),

    """<section class="band"><div class="wrap">
  <p class="lbl" data-rv="rise">The vision</p>
  <div class="cols">
    <p class="stmt" data-rv="mask">To be the stepping stone that helps women break barriers
      and make impossible goals possible.</p>
    <div class="body" data-rv="rise">
      <p>FemmForce is a groundbreaking system designed to break free the conditioning and
        restrictions faced by women, and to empower them to meet the quality and corporate
        standards expected of them head-on.</p>
      <p>Our programmes foster talent development, boost confidence and facilitate
        recognition, creating a more supportive environment &mdash; one built deliberately
        rather than hoped for. The trust competes on efficiency and implementation rather
        than commentary, which is the reason it exists at all.</p>
    </div>
  </div>
</div></section>""",

    section(head2("What the trust runs", "Three things, and they pay for each other.",
                  "Programmes for women who need them, training for the organisations "
                  "that can pay for it, and the funding routes that connect the two.")
            + cells([
                ("Beneficiary programmes",
                 "<p>Four groups of women &mdash; at business, at work, at home, and "
                 "underprivileged &mdash; each with its own route through mentoring, "
                 "upskilling, funding and placement.</p>"),
                ("Corporate training",
                 "<p>Nine programmes delivered to corporates and institutions, from POSH "
                 "compliance to leadership, drawn from a network of more than 300 "
                 "qualified trainers.</p>"),
                ("Funding",
                 "<p>Grant Wave raises through donors and CSR. Skill Fund returns a share "
                 "of training earnings to the trust. Between them they keep the free "
                 "programmes running.</p>"),
            ]), ident="what"),

    section(head2("Trustees", "The people behind it.", width="13ch") + """  <div class="people">
    <article>
      <h3>Uma G Reddy</h3>
      <p class="role">Trustee &amp; Founder</p>
      <p>A Rotarian, dynamic serial entrepreneur and MBA graduate specialising in Marketing
        &amp; HR. With over 20 years in the corporate world and a decade in business, she has
        in-depth knowledge of the challenges women face at many levels. Founder CEO at Hiring
        Studios &mdash; HR Consulting &amp; Recruitment; Director at Primeworth Energia
        (solar, biogas, wind turbines); Director at Silverhive Realtors and Management LLP.</p>
      <p>Uma believes that businesses seek efficiency and implementation rather than talk
        about feminism. That is her primary objective in founding FemmForce.</p>
    </article>
    <article style="--d:130ms">
      <h3>Narasimhan M.V</h3>
      <p class="role">Trustee</p>
      <p>A Rotarian and seasoned HR professional with over three decades of experience in HR
        and management. He is passionate about networking and has created hundreds of WhatsApp
        and LinkedIn groups to help people find jobs, share knowledge and build business
        relationships.</p>
      <p>His background spans manufacturing, hospitality, winery, NGO, textiles, poultry,
        logistics, education and training &mdash; with organisations including WS Industries,
        ALSTOM, AREVA, Suguna Foods, Alpine Wineries, SPR Retail Chains, FSL, Zenith Textiles,
        Cheran Group, Rareminds, Royal Orchid Groups and Chancery Pavilion. He also mentors
        young students through the NHRWA Trust Student Chapters.</p>
    </article>
    <article style="--d:260ms">
      <h3>Jaya Reddy</h3>
      <p class="role">Executive Director</p>
      <p>An MBA (HR) graduate with over 15 years of diverse industry experience across the
        corporate world and NGOs. She is also an entrepreneur and Partner in Journey Breeze
        International, a tourism company, and has been an active member of Lions Clubs
        International for the last six years, volunteering in communities around India.</p>
      <p>Jaya believes in empowering women through upskilling, providing resources and
        creating opportunities for them to control their own lives, make informed decisions
        and participate in social, economic and political life.</p>
    </article>
  </div>""", ident="trustees"),

    section(head2("The trust", "Registered, and reachable.", width="14ch") + """  <div class="note" data-rv="rise">
    <dl class="kv">
      <dt>Registered</dt><dd>FemmForce &mdash; a registered trust in Bangalore, India</dd>
      <dt>Address</dt><dd>#1, AECS Layout A Block, Singasandra, Bangalore &ndash; 560 068</dd>
      <dt>E-mail</dt><dd><a href="mailto:info@femmforce.in">info@femmforce.in</a></dd>
      <dt>Phone</dt><dd><a href="tel:+919880438607">+91 98804 38607</a></dd>
    </dl>
  </div>""", style="background:var(--bg-1);border-top:1px solid var(--line)"),

    GENERAL_CTA,
])
pages.append(document("about-us.html", "About Us — FemmForce",
                      "FemmForce is a registered trust in Bangalore working to remove the "
                      "barriers that stop women, rather than discuss them. Vision, trustees "
                      "and registered details.",
                      "about-us", about))


# ── Our Activities ──────────────────────────────────────────────────────
# (title, description, where that activity lives on the site)
# The ten titles are verbatim from the original site; the descriptions are
# written for this build from the detail on the pages each row links to.
ACTIVITIES = [
    ("Mentorship Programs",
     "One-to-one mentoring across every cohort &mdash; founders, graduates, mid-career "
     "professionals and women returning after a break.",
     "women-at-work.html"),
    ("Networking Events",
     "Introductions that would not otherwise happen: peers, employers, buyers, and the "
     "institutions that hold the budgets.",
     "events.html"),
    ("Training / Skill Building Workshops",
     "Nine structured programmes for organisations, plus workshops run directly for the "
     "women in our beneficiary groups.",
     "how-we-do.html#training"),
    ("Access to Funding",
     "Routes to grants, donors and CSR budgets for women building a business, and funded "
     "places for women who cannot pay.",
     "how-we-do.html"),
    ("Leadership Development",
     "Decision-making, team building, emotional intelligence and the confidence to lead "
     "with integrity.",
     "training-leadership.html"),
    ("Recognition and Awards",
     "Visibility for women who are breaking barriers and challenging norms in their "
     "fields &mdash; the mavericks and the trailblazers.",
     "women-at-business.html"),
    ("Collaboration and Partnerships",
     "Nine categories of partner, from corporates and government to knowledge partners "
     "and volunteers, each contributing something different.",
     "our-partners.html"),
    ("Counseling and Support",
     "Career counselling, five-dimensional assessment, mental-health resources and legal "
     "guidance depending on what is needed.",
     "training-career-coaching.html"),
    ("Business Support / Vendor Empanelment",
     "Supplier diversity and vendor empanelment, so that women-led businesses reach the "
     "procurement lists they are usually missing from.",
     "women-at-business.html"),
    ("Community Building",
     "A network that keeps working after the programme ends &mdash; alumni, peer groups "
     "and the people who hire from them.",
     "membership.html"),
]
activities = "\n\n".join([
    hero([("Home", "index.html"), ("Our activities", None)],
         ["Ten things", "we actually do."],
         "FemmForce is always in action. These are the activities that carry the work, "
         "across all four groups of women the trust supports."),
    section(head2("Our activities", "From mentoring to empanelment.",
                  "Each activity runs across every cohort. Follow a row through to the "
                  "page where that work actually happens.")
            + index_rows([(h, t, d) for t, d, h in ACTIVITIES])),
    section(head2("Who it reaches", "Four groups, one set of activities.",
                  "What changes between the groups is the starting point, not the level "
                  "of support.", width="16ch")
            + cells([(name, "<p>%s</p>" % desc, "", slug)
                     for (_k, slug, name, _c, desc) in COHORTS], numbered=False),
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    GENERAL_CTA,
])
pages.append(document("our-activities.html", "Our Activities — FemmForce",
                      "Mentorship, networking, training, funding, leadership development, "
                      "recognition, partnerships, counselling, vendor empanelment and "
                      "community building.",
                      "our-activities", activities))


# ── Beneficiaries ───────────────────────────────────────────────────────
def cohort_page(idx, lines, lede, sections, title, desc):
    """sections: already-rendered <section> strings, placed between the page
    head and the prev/next pager."""
    key, slug, name, cls, _d = COHORTS[idx]
    prev = (COHORTS[idx - 1][1], COHORTS[idx - 1][2]) if idx > 0 else None
    nxt = (COHORTS[idx + 1][1], COHORTS[idx + 1][2]) if idx < len(COHORTS) - 1 else None
    parts = [hero([("Home", "index.html"), ("Beneficiaries", None), (name, None)],
                  lines, lede)]
    parts += sections
    parts += [pager(prev, nxt), GENERAL_CTA]
    return document(slug, title, desc, key, "\n\n".join(parts), bodycls=cls)


pages.append(cohort_page(
    0,
    ["Women", "at Business."],
    "FemmForce is a dynamic force that supports and empowers women in the startup and "
    "entrepreneurial ecosystem &mdash; those already building, those breaking the norms, "
    "and those on the verge of starting.",
    [section(head2("The three groups", "Empowering divas.",
                   "Startup Divas, Maverick Divas and Aspiring Divas &mdash; the same "
                   "trust, three different starting points.") + cells([
        ("Startup Divas",
         "<p>FemmForce empowers women in the startup and entrepreneurial ecosystem through "
         "valuable resources like workshops, mentoring programmes and funding initiatives, "
         "meeting the specific needs of women entrepreneurs and fostering a nurturing "
         "environment and meaningful connections. FemmForce also actively promotes supplier "
         "diversity and inclusive sourcing, contributing to a more equitable business "
         "landscape.</p>"),
        ("Maverick Divas",
         "<p>FemmForce focuses on empowering and celebrating women who are breaking barriers "
         "and challenging norms in various domains, highlighting and supporting the women "
         "who are considered mavericks, trailblazers and innovators in their respective "
         "fields.</p>"),
        ("Aspiring Divas",
         "<p>FemmForce helps women who are on the verge of diving into entrepreneurship. "
         "With a strong focus on empowerment, it provides the support and resources these "
         "aspiring women need to succeed and make a meaningful impact in their chosen "
         "fields &mdash; specific guidance, valuable opportunities, and a nurturing "
         "community in which to grow personally and professionally.</p>"),
     ])),
     section(head2("What you get", "Support that is practical.",
                   "Not a mailing list. Concrete access &mdash; the kind that changes "
                   "what a business can do next.", width="16ch")
             + checks(["Workshops and skill-building", "Mentoring programmes",
                       "Funding initiatives",
                       "Supplier diversity and inclusive sourcing", "Vendor empanelment",
                       "Networking events", "Recognition and awards",
                       "Business support and counselling"]),
             style="background:var(--bg-1);border-top:1px solid var(--line)")],
    "Women at Business — FemmForce",
    "Startup Divas, Maverick Divas and Aspiring Divas — workshops, mentoring, funding "
    "and supplier-diversity access for women building their own business."))

pages.append(cohort_page(
    1,
    ["Women", "at Work."],
    "From a first job to a return after a sabbatical &mdash; tailored programmes for female "
    "graduates, for professionals building a career, and for women coming back to the "
    "workforce.",
    [section(head2("The three groups", "Students, thrivers and returners.",
                   "Three points on the same career, and a different kind of help at "
                   "each.") + cells([
        ("Rising Stars &mdash; Students",
         "<p>We provide tailored finishing school programmes for female college graduates, "
         "ensuring a seamless transition into the professional world. Our industry-oriented "
         "training equips them with the skills needed in their chosen fields. We also foster "
         "a strong alumni network that offers mentoring, networking opportunities and job "
         "fairs to support their career launch and growth.</p>"),
        ("Career Thrivers",
         "<p>Women Career Thrivers celebrates women&rsquo;s resilience and success in achieving "
         "remarkable professional growth. Through upskilling, job fairs and job opportunities "
         "we propel their careers forward, supporting their personal and professional growth "
         "so they can thrive and contribute to their families and communities.</p>"),
        ("Career Re-entry",
         "<p>Our focus is also on upskilling, reskilling and assisting women who are returning "
         "to the workforce after a career break or sabbatical. We connect them with relevant "
         "peer professionals to bridge the knowledge gaps, offer mentoring, and provide job "
         "opportunities.</p>"),
     ])),
     section(head2("What you get", "A route back in, or a route up.",
                   "The gap between having the skill and being hired for it is the part "
                   "we work on.", width="16ch")
             + checks(["Finishing school programmes", "Industry-oriented training",
                       "Alumni network", "Mentoring", "Job fairs",
                       "Upskilling and reskilling", "Peer professional connections",
                       "Job opportunities"]),
             style="background:var(--bg-1);border-top:1px solid var(--line)")],
    "Women at Work — FemmForce",
    "Finishing school for graduates, upskilling for professionals, and a route back into "
    "work after a career break or sabbatical."))

home_page = "\n\n".join([
    hero([("Home", "index.html"), ("Beneficiaries", None), ("Women at Home", None)],
         ["Women", "at Home."],
         "FemmForce supports homemakers by offering financial literacy, mental health "
         "resources, parenting guidance and networking opportunities &mdash; independence "
         "that does not require leaving the house."),
    section(head2("Divas at Home", "Access, on eleven fronts.",
                  "FemmForce supports Divas at Home to get empowered by providing access to:")
            + checks([
                "Skill Development", "Financial Independence",
                "Emotional Support and Mental Health", "Work-Life Balance",
                "Gender Equality Awareness", "Access to Healthcare",
                "Networking and Mentorship", "Legal Support",
                "Hygiene and Personal Health", "Networking",
                "Legal rights and protection"])),
    section(head2("Why it matters", "Independence without an office.", "")
            + """  <div class="rich" data-rv="rise">
    <p>A woman running a household is doing skilled work that no payslip records. The
      barrier is rarely capability &mdash; it is access: to money in her own name, to a
      network that is not made of neighbours, to a lawyer who will explain her rights, and
      to a room where her own health is the subject.</p>
    <p>Divas at Home is built around that. Everything in it is designed to be taken up in
      the hours a homemaker actually has, and none of it assumes she can commit to an
      office.</p>
  </div>""",
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    pager((COHORTS[1][1], COHORTS[1][2]), (COHORTS[3][1], COHORTS[3][2])),
    GENERAL_CTA,
])
pages.append(document("women-at-home.html", "Women at Home — FemmForce",
                      "Financial independence, mental health, legal rights, healthcare "
                      "access and a network for homemakers — the Divas at Home "
                      "programme.",
                      "women-at-home", home_page, bodycls="acc-home"))

und_page = "\n\n".join([
    hero([("Home", "index.html"), ("Beneficiaries", None), ("Underprivileged Women", None)],
         ["Underprivileged", "Women."],
         "FemmForce supports underprivileged women, who often face socioeconomic "
         "disadvantages and lack access to basics and other resources."),
    section(head2("The programme", "Four points of leverage.",
                  "FemmForce aims to create a positive impact on the lives of "
                  "underprivileged women and promote their overall well-being and success.")
            + checks(["Financial literacy", "Community livelihood support",
                      "Government schemes", "Economic independence"])),
    section(head2("How it is funded", "Free at the point of use.", "")
            + """  <div class="rich" data-rv="rise">
    <p>Membership for underprivileged women is free. Nothing in this programme is charged
      for, and nothing about it is contingent on being able to pay later.</p>
    <p>That is only possible because the corporate side of the trust pays for it. Skill
      Fund returns a share of training earnings into FemmForce, and Grant Wave raises
      through donors and CSR budgets. The paid work funds the free work &mdash; deliberately,
      and by design.</p>
    <p style="margin-bottom:0"><a class="btn" href="how-we-do.html"><span>How the funding
      works</span></a></p>
  </div>""",
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    pager((COHORTS[2][1], COHORTS[2][2]), None),
    GENERAL_CTA,
])
pages.append(document("underprivileged-women.html",
                      "Underprivileged Women — FemmForce",
                      "Financial literacy, community livelihood support, help navigating "
                      "government schemes and a route to economic independence. Free at "
                      "the point of use.",
                      "underprivileged-women", und_page, bodycls="acc-und"))


# ── How We Do ───────────────────────────────────────────────────────────
how = "\n\n".join([
    hero([("Home", "index.html"), ("How we do", None)],
         ["The free work", "is paid for by", "the paid work."],
         "Two funding routes keep FemmForce running. Grant Wave raises through donors and "
         "CSR. Skill Fund returns a share of corporate training earnings to the trust."),

    """<section id="grant-wave"><div class="wrap">
  <p class="lbl" data-rv="rise">Route one</p>
  <h2 data-rv="mask" style="margin-bottom:2.8rem;max-width:16ch">Grant Wave &mdash; funds through grants and donations.</h2>
  <div class="rich" data-rv="rise">
    <p>FemmForce is always in action, continuously empowering women through various
      activities. We are reaching out to the kind-hearted donors and CSR heads of corporates,
      NGOs, consortiums, foundations and more, who are keen on joining hands and
      contributing. Your support will help us keep these empowering initiatives going
      strong. Let us collaborate and make a positive impact together.</p>
  </div>
</div></section>""",

    """<section id="skill-fund" style="background:var(--bg-1);border-top:1px solid var(--line)"><div class="wrap">
  <p class="lbl" data-rv="rise">Route two</p>
  <h2 data-rv="mask" style="margin-bottom:2.8rem;max-width:16ch">Skill Fund &mdash; funds through training.</h2>
  <div class="rich" data-rv="rise">
    <p>FemmForce emphasises sustainability and funding through corporate and institutional
      partnerships. Industry experts, contributing a portion of their earnings, enhance the
      training programmes. Collaborating with them ensures high-quality initiatives,
      empowering women and promoting equality.</p>
    <p>In practice this means the organisations that buy training from FemmForce are also
      the ones paying for the free programmes. A POSH engagement for a corporate funds
      financial-literacy work in a community that could never have commissioned it.</p>
  </div>
</div></section>""",

    """<section style="padding-top:0;padding-bottom:0"><div class="wrap">
  <div class="facts" style="margin-top:clamp(84px,10vw,180px)">
    <div data-count="300"><b>300<em>+</em></b><span>Qualified trainers in the network</span></div>
    <div data-count="20"><b>20<em>+</em></b><span>Organisations served under POSH</span></div>
    <div data-count="9"><b>9</b><span>Training programmes delivered</span></div>
    <div data-count="2"><b>2</b><span>Funding routes into the trust</span></div>
  </div>
</div></section>""",

    section(head2("Training", "Nine programmes for companies and institutions.",
                  "Here are the training services supported and facilitated by FemmForce "
                  "for corporates and institutions.")
            + index_rows([
                (TRAINING[0][1], "POSH Training",
                 "External Member for Prevention of Sexual Harassment training, in multiple "
                 "languages. Used by more than 20 organisations across India."),
                (TRAINING[1][1], "Soft Skill Training",
                 "Communication, teamwork, leadership and interpersonal abilities."),
                (TRAINING[2][1], "IT &amp; Technical Training",
                 "IT and technical skills, for both students and professionals."),
                (TRAINING[3][1], "Career Coaching and Counselling",
                 "Guidance, support and expert advice towards a clear professional path."),
                (TRAINING[4][1], "Sales Training",
                 "A gender-inclusive approach to sales, fostering equality and diversity "
                 "in the sales industry."),
                (TRAINING[5][1], "Leadership Training",
                 "Communication, decision-making, team building and emotional intelligence."),
                (TRAINING[6][1], "Customised Training",
                 "Programmes addressing the specific needs of one corporate client."),
                (TRAINING[7][1], "Campus to Corporate",
                 "Employability quotients, and training that prepares students for the "
                 "job market."),
                (TRAINING[8][1], "Train the Trainers",
                 "Training-need analysis, content design, public speaking and delivery, "
                 "drawing on a pool of more than 300 qualified trainers."),
            ]), ident="training"),

    cta("Work with the training side.",
        "Register as a trainer to join the network, or send an enquiry and we will come "
        "back with a scope and a date.",
        [(mailto("Training enquiry"), "Training enquiry"),
         (mailto("Trainer empanelment registration"), "Register for trainer empanelment")]),
])
pages.append(document("how-we-do.html", "How We Do — FemmForce",
                      "Grant Wave raises through donors and CSR. Skill Fund returns a share "
                      "of corporate training earnings to the trust. Nine training programmes "
                      "for companies and institutions.",
                      "how-we-do", how))


# ── Our Partners ────────────────────────────────────────────────────────
PARTNER_CATS = [
    ("Corporate Partners",
     "Corporate partners are essential allies for FemmForce, joining hands to support the "
     "organisation&rsquo;s initiatives, projects and programmes. Through collaboration these "
     "companies contribute financial resources, valuable expertise and necessary tools, "
     "creating a powerful force for positive change and driving progress towards a more "
     "inclusive and equitable society."),
    ("Non-Profit Organizations &amp; Institutions",
     "Our work is significantly supported by our foundation and institution partners, who "
     "provide crucial assistance through funding, capacity-building support, networking, "
     "recognition and credibility. With their support we are able to enhance our impact and "
     "fulfil our mission."),
    ("Government",
     "Government partnerships benefit NGOs like FemmForce through financial support, policy "
     "advocacy, resource access, collaborative projects, capacity-building programmes and "
     "data access &mdash; enhancing impact, credibility and the ability to achieve the "
     "mission."),
    ("Knowledge Partners",
     "Organisations, institutions or individuals that collaborate with FemmForce to provide "
     "expertise, specialised knowledge and valuable insights in specific domains. These "
     "partnerships are essential to enhancing our programmes, initiatives and research."),
    ("Interns",
     "Interning with FemmForce lets interns contribute to meaningful social causes, raises "
     "their awareness of societal issues, fosters personal growth, and provides "
     "opportunities for community engagement and collaboration with like-minded people."),
    ("Employment Partners",
     "Employment partners collaborate with FemmForce to provide job opportunities, skill "
     "alignment, networking, internships and apprenticeships for women. These partnerships "
     "bridge the gap between skill development and employment, leading to greater career "
     "opportunities and financial independence."),
    ("NRI / HNI",
     "Non-Resident Indian and High Net Worth Individual supporters offer significant "
     "financial resources, global networks and expertise &mdash; funding, networking "
     "opportunities and potential partnerships that advance the mission. Their involvement "
     "can ensure sustainability, foster corporate philanthropy and provide mentorship."),
    ("Trade Body &amp; Association",
     "Trade bodies and associations bring industry expertise, networking opportunities, job "
     "placement support, advocacy and skill development. The collaboration fosters knowledge "
     "sharing, increases visibility and enhances impact across sectors."),
    ("Volunteers",
     "Volunteers contribute their time, skills and effort to FemmForce initiatives. They "
     "bring diverse skills, increase outreach, reduce operational costs, engage with "
     "communities, provide emotional support, foster innovation and contribute to the "
     "sustainability of the trust."),
]
partners = "\n\n".join([
    hero([("Home", "index.html"), ("Our partners", None)],
         ["Partners who", "make the work", "possible."],
         "FemmForce values its strong partnerships with the organisations, institutions and "
         "individuals who share the vision of empowering women and promoting gender "
         "equality. Our partners play a crucial role in supporting our initiatives and "
         "expanding our impact."),
    section(head2("What partners can expect", "Eleven things you get back.",
                  "Partnership with FemmForce is not a logo exchange. This is what comes "
                  "back the other way.")
            + checks([
                "Expanded reach and visibility", "Enhanced impact", "Access to resources",
                "Networking and collaborations", "Shared expertise", "Supportive community",
                "Alignment with CSR objectives", "Buying partners", "Job fairs",
                "Personal fulfilment", "Diverse vendor network"])),
    """<div class="marq" aria-label="Partner categories">
  <ul>
    <li>Corporate</li><li>Non-Profit &amp; Institutions</li><li>Government</li>
    <li>Knowledge Partners</li><li>Interns</li><li>Employment Partners</li>
    <li>NRI / HNI</li><li>Trade Bodies</li><li>Volunteers</li>
    <li aria-hidden="true">Corporate</li><li aria-hidden="true">Non-Profit &amp; Institutions</li>
    <li aria-hidden="true">Government</li><li aria-hidden="true">Knowledge Partners</li>
    <li aria-hidden="true">Interns</li><li aria-hidden="true">Employment Partners</li>
    <li aria-hidden="true">NRI / HNI</li><li aria-hidden="true">Trade Bodies</li>
    <li aria-hidden="true">Volunteers</li>
  </ul>
</div>""",
    section(head2("The categories", "Nine kinds of partner.",
                  "Each contributes something the others cannot.")
            + cells([(t, "<p>%s</p>" % d) for t, d in PARTNER_CATS], cls="wide")),
    cta("Become a partner.",
        "Tell us which category fits and what you would want out of it, and we will send "
        "the partner registration form.",
        [(mailto("Partner registration — FemmForce"), "Partner registration"),
         ("membership.html", "Membership plans")]),
])
pages.append(document("our-partners.html", "Our Partners — FemmForce",
                      "Corporate, non-profit, government, knowledge, employment and trade "
                      "partners, interns, NRI/HNI supporters and volunteers — and what "
                      "each gets back.",
                      "our-partners", partners))


# ── Membership ──────────────────────────────────────────────────────────
PLANS = [
    ("Women at Business", "3,000/-", "var(--gold)", "women-at-business.html"),
    ("Women at Work", "2,000/-", "var(--orange)", "women-at-work.html"),
    ("Women at Home", "500/-", "var(--verm)", "women-at-home.html"),
    ("Underprivileged Women", "Free", "var(--red)", "underprivileged-women.html"),
    ("Institutions &amp; Corporates", "10,000/-", "var(--tx-2)", "our-partners.html"),
]
rows = "\n".join(
    '      <tr>\n'
    '        <td><a class="cat" style="--dot:%s" href="%s">%s</a></td>\n'
    '        <td class="plan">%s</td>\n'
    '        <td><a class="sub" href="%s">Subscribe</a></td>\n'
    '      </tr>' % (dot, href, name, plan, mailto("Membership — " +
                                                   re.sub("&amp;", "and", name)))
    for name, plan, dot, href in PLANS)

membership = "\n\n".join([
    hero([("Home", "index.html"), ("Membership", None)],
         ["Choose the plan", "that fits."],
         "Members of FemmForce have the flexibility to select a membership plan based on "
         "their desired category, entitling them to a range of benefits."),
    section(head2("Membership plan", "Five categories, per annum.",
                  "All figures are in Indian rupees, per annum. Membership for "
                  "underprivileged women is free and always will be.")
            + """  <div class="scroll" data-rv="rise">
    <table class="tbl">
      <thead><tr><th>Members Category</th><th>Plan / PA</th><th>Subscribe</th></tr></thead>
      <tbody>
%s
      </tbody>
    </table>
  </div>""" % rows),
    section(head2("What it entitles you to", "Six things, from the day you join.",
                  width="17ch")
            + checks(["Exclusive events", "Workshops", "Networking opportunities",
                      "Updates on FemmForce activities", "Chances to volunteer",
                      "Participation in the trust&rsquo;s initiatives"]),
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    section(head2("Payment", "Bank details.", width="12ch")
            + """  <div class="note" data-rv="rise">
    <dl class="kv">
      <dt>Name</dt><dd>FEMMFORCE</dd>
      <dt>Bank</dt><dd>The Karur Vysya Bank Limited, HSR Layout, Bangalore</dd>
      <dt>IFSC</dt><dd>KVBL0001333</dd>
      <dt>Account no.</dt><dd>1333135000006777</dd>
    </dl>
    <p style="margin-top:1.8rem;font-size:.92rem;color:var(--tx-3);max-width:46ch">
      Send the transfer reference to <a href="mailto:info@femmforce.in"
      style="border-bottom:1px solid var(--line-2)">info@femmforce.in</a> along with the
      category you are joining, and we will confirm your membership.</p>
  </div>"""),
    GENERAL_CTA,
])
pages.append(document("membership.html", "Membership — FemmForce",
                      "Five membership categories from free to Rs 10,000 per annum, the "
                      "benefits each carries, and the trust bank details.",
                      "membership", membership))


# ── Training pages ──────────────────────────────────────────────────────
def training_page(idx, lines, lede, sections, title, desc, extra_buttons=None):
    key, slug, name, _d = TRAINING[idx]
    prev = (TRAINING[idx - 1][1], TRAINING[idx - 1][2]) if idx > 0 else None
    nxt = (TRAINING[idx + 1][1], TRAINING[idx + 1][2]) if idx < len(TRAINING) - 1 else None
    parts = [hero([("Home", "index.html"), ("Training", "how-we-do.html#training"),
                   (name, None)], lines, lede)]
    parts += sections
    parts += [pager(prev, nxt), training_cta(name)]
    return document(slug, title, desc, key, "\n\n".join(parts))


# 1 — POSH
pages.append(training_page(
    0, ["POSH", "Training."],
    "In India, every establishment with ten or more employees must comply with the Sexual "
    "Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013. "
    "FemmForce deputes expert external members and runs the training that makes compliance "
    "real rather than filed.",
    [
        section(head2("The obligation", "Compliance is not optional.", "")
                + """  <div class="rich" data-rv="rise">
    <p>Companies falling under the Act are obligated to conduct regular POSH training for
      their employees. The Act aims to create a safe and respectful work environment and
      requires organisations to have policies and procedures in place to prevent and address
      incidents of sexual harassment effectively. Companies must ensure strict compliance
      with these legal requirements to protect the rights and well-being of their
      employees.</p>
    <p>Over the past few years FemmForce has been offering services to depute expert
      external members for Internal Committees under the POSH law. That expertise has been
      used by more than 20 organisations across India, helping to ensure the fair and
      effective handling of sexual harassment cases and contributing to the creation of safe
      and respectful work environments.</p>
  </div>"""),
        section(head2("The process", "Five steps to compliance.",
                      "What an engagement with FemmForce covers, in order.")
                + cells([
                    ("Formulation of POSH policy",
                     "<p>Defining the scope and applicability of the policy, clearly "
                     "outlining prohibited behaviours, and providing a confidential "
                     "procedure for reporting incidents. It establishes a robust "
                     "investigation process, outlines consequences for violations, and "
                     "emphasises protection against retaliation for complainants.</p>"),
                    ("Constitution of the Internal Committee",
                     "<p>Selecting diverse, qualified members, designating a capable "
                     "Chairperson, and providing comprehensive training. Clear roles, "
                     "confidentiality, accessible reporting and structured procedures are "
                     "crucial, alongside thorough record-keeping, support resources, regular "
                     "meetings and ongoing evaluation.</p>"),
                    ("Appointment as External Member",
                     "<p>As an External Member the individual serves as an impartial expert "
                     "on the Internal Complaints Committee, providing an outsider&rsquo;s "
                     "perspective during investigations and ensuring fair treatment. "
                     "Responsibilities include maintaining confidentiality and enhancing the "
                     "committee&rsquo;s effectiveness.</p>"),
                    ("Awareness sessions",
                     "<p>Periodic awareness sessions for employees and the Internal "
                     "Committee, covering policy specifics and reporting protocols, and "
                     "nurturing a secure and respectful workplace &mdash; a culture of "
                     "awareness and prevention rather than a one-off briefing.</p>"),
                    ("Display of POSH posters",
                     "<p>Displaying posters in prominent areas of the workplace, carrying "
                     "company policy, reporting procedures and the resources available. They "
                     "serve as a visible reminder of the organisation&rsquo;s commitment to "
                     "preventing harassment and supporting those affected by it.</p>"),
                ])),
        section(head2("The upside", "Nine things compliance buys you.",
                      "Beyond the legal requirement, the effect on an organisation is "
                      "measurable.", width="19ch")
                + checks([
                    "A safe and harassment-free work environment",
                    "Compliance with legal requirements", "Enhanced employee morale",
                    "Positive reputation and brand image",
                    "Reduced legal risks and liabilities", "Increased trust and transparency",
                    "Attraction of top talent", "Improved organisational culture",
                    "Better performance, less absenteeism and stress"]),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
    ],
    "POSH Training — FemmForce",
    "External Internal-Committee members and full compliance under the Sexual Harassment "
    "of Women at Workplace Act 2013. Delivered to more than 20 organisations across India."))

# 2 — Soft skills
pages.append(training_page(
    1, ["Soft Skill", "Training."],
    "Soft skills training enhances communication, teamwork, time management and leadership "
    "abilities, fostering the personal and professional development that career success "
    "actually rests on.",
    [section(head2("Topics covered", "Twelve areas.",
                   "Delivered as a full programme or picked individually to fit a team.")
             + cells([
                 ("Effective Communication",
                  "<p>Communicate clearly, listen actively and convey ideas with confidence. "
                  "Good communication fosters better relationships, reduces misunderstandings "
                  "and improves teamwork.</p>"),
                 ("Building Strong Relationships",
                  "<p>Empathy, emotional intelligence and cultural competence let people "
                  "connect on a deeper level, build trust and promote a positive work "
                  "environment.</p>"),
                 ("Conflict Resolution",
                  "<p>Handle disagreements constructively, find solutions and maintain a "
                  "harmonious atmosphere within teams and organisations.</p>"),
                 ("Leadership Development",
                  "<p>Decision-making, problem-solving and delegation &mdash; the skills that "
                  "let an individual guide and inspire others.</p>"),
                 ("Time Management",
                  "<p>Prioritise tasks, increase productivity and reduce stress, leading to "
                  "better work-life balance.</p>"),
                 ("Stress Management",
                  "<p>Coping mechanisms, resilience and mindfulness for handling pressure in "
                  "high-demand environments.</p>"),
                 ("Customer Service Excellence",
                  "<p>For customer-facing roles, empathy, patience and active listening are "
                  "what deliver exceptional service and retain satisfied clients.</p>"),
                 ("Adaptability and Flexibility",
                  "<p>Adapt to change, embrace new challenges and stay relevant in dynamic "
                  "work environments.</p>"),
                 ("Team Collaboration",
                  "<p>Cooperation, respect and open communication, leading to improved "
                  "efficiency and better problem-solving.</p>"),
                 ("Career Advancement",
                  "<p>Soft skills are often the differentiator in promotion decisions. Those "
                  "who have them are more likely to be considered for leadership roles.</p>"),
                 ("Workplace Culture",
                  "<p>A positive culture is built through good communication, empathy and "
                  "mutual respect &mdash; and shows up in satisfaction and retention.</p>"),
                 ("Customer Satisfaction",
                  "<p>In service industries, employees with excellent soft skills create "
                  "positive experiences, increasing loyalty and word-of-mouth referral.</p>"),
             ]))],
    "Soft Skill Training — FemmForce",
    "Communication, relationships, conflict resolution, leadership, time and stress "
    "management — twelve areas of soft skill training for teams."))

# 3 — IT & technical
pages.append(training_page(
    2, ["IT &amp; Technical", "Training."],
    "IT &amp; Technical Training equips individuals with essential skills in information "
    "technology and specialised technical areas &mdash; programming languages, software "
    "applications, hardware, networking and cyber security.",
    [section(head2("What it covers", "Eleven characteristics.",
                   "The training enhances proficiency in IT tools and prepares individuals "
                   "for careers in the tech industry, ensuring competitiveness in the job "
                   "market.")
             + cells([
                 ("Comprehensive Curriculum",
                  "<p>Programming, software development, system administration, networking, "
                  "cyber security and more.</p>"),
                 ("Hands-On Experience",
                  "<p>Practical exercises that reinforce theoretical knowledge, letting "
                  "learners apply concepts in real-world scenarios.</p>"),
                 ("Certification Programs",
                  "<p>Certifications from reputable organisations, validating proficiency in "
                  "specific technologies or platforms.</p>"),
                 ("Industry-Relevant Skills",
                  "<p>Skills that are directly applicable in the tech industry, so graduates "
                  "are job-ready and able to contribute effectively.</p>"),
                 ("Customized Tracks",
                  "<p>Specialised tracks based on areas of interest, letting learners focus "
                  "on specific technologies or domains.</p>"),
                 ("Qualified Instructors",
                  "<p>Experienced instructors with expertise in their fields provide guidance "
                  "and mentorship.</p>"),
                 ("Adaptability to Advancements",
                  "<p>Programmes are updated to reflect the latest trends and technologies, "
                  "keeping them relevant in a fast-moving industry.</p>"),
                 ("Problem-Solving and Critical Thinking",
                  "<p>Analytical thinking and problem-solving, crucial for troubleshooting "
                  "and innovation in IT roles.</p>"),
                 ("Soft Skills Integration",
                  "<p>Alongside technical skills, communication, teamwork and time "
                  "management.</p>"),
                 ("Career Advancement Opportunities",
                  "<p>Completion opens doors across technology-driven industries.</p>"),
                 ("Continuous Learning Culture",
                  "<p>Technology is dynamic; the programme builds the habit of staying "
                  "current with industry trends.</p>"),
             ]))],
    "IT &amp; Technical Training — FemmForce",
    "Programming, software development, system administration, networking, cyber security "
    "and certification tracks, for students and professionals."))

# 4 — Career coaching
pages.append(training_page(
    3, ["Career Coaching", "and Counselling."],
    "A personalised service that provides individuals with guidance and support in their "
    "professional development and decision-making &mdash; assessing strengths, interests "
    "and aspirations, then building the strategy to act on them.",
    [
        section(head2("What it is", "Guidance with an execution plan attached.", "")
                + """  <div class="rich" data-rv="rise">
    <p>Career coaching and counselling involves working with a trained coach or counsellor
      who helps clients assess their strengths, interests and aspirations, and then develop
      strategies to achieve their career goals. The process includes resume review,
      interview preparation, skill-building, and creating a tailored action plan for career
      advancement.</p>
  </div>"""),
        section(head2("The five parts", "How a session set is structured.", "",
                      width="17ch")
                + cells([
                    ("Finding the Most Suitable Career Option",
                     "<p>Career counselling in Bangalore assists individuals in identifying "
                     "the career path that aligns with their strengths, interests and "
                     "aspirations. A comprehensive assessment pinpoints suitable industries, "
                     "roles and opportunities for professional growth.</p>"),
                    ("5-Dimensional Career Assessment",
                     "<p>A specialised assessment evaluating personality traits, skills, "
                     "values, interests and aptitudes. Examining these together gives a "
                     "holistic understanding of potential and points towards fields where an "
                     "individual is likely to thrive.</p>"),
                    ("Personal One-on-One Counselling",
                     "<p>Personalised guidance through face-to-face sessions with experienced "
                     "career counsellors in Bangalore &mdash; in-depth discussion, tailored "
                     "advice, and a customised career roadmap built on the "
                     "individual&rsquo;s own circumstances.</p>"),
                    ("Execution Plan",
                     "<p>Not just the right career path but a concrete plan of action: "
                     "specific steps, milestones and the resources needed to progress, so the "
                     "professional journey can be navigated with confidence.</p>"),
                    ("All Support",
                     "<p>Ongoing assistance beyond the assessment &mdash; resume building, "
                     "interview preparation, skill development recommendations, and access to "
                     "networks or job opportunities.</p>"),
                ]),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
    ],
    "Career Coaching and Counselling — FemmForce",
    "Five-dimensional career assessment, one-to-one counselling in Bangalore, an execution "
    "plan, and support through resume, interview and placement."))

# 5 — Sales
pages.append(training_page(
    4, ["Sales", "Training."],
    "Effective sales training boosts a team&rsquo;s confidence, refines their performance "
    "and instils the drive to meet and exceed targets. FemmForce delivers it with a "
    "gender-inclusive approach, fostering equality and diversity in the sales industry.",
    [
        section(head2("The approach", "Choose the topics, then tailor the tools.", "")
                + """  <div class="rich" data-rv="rise">
    <p>Choosing the right training topics is key to optimising the impact of these efforts.
      It is crucial to identify specific areas of focus so that training tools can be
      tailored to a team&rsquo;s unique requirements.</p>
    <p>The topics below have been selected on their proven track record in empowering sales
      teams across diverse industries. Whether you are a seasoned trainer or new to the
      domain, they are where the productivity gain tends to come from.</p>
  </div>"""),
        section(head2("Topics", "Eleven areas of sales practice.", "", width="17ch")
                + cells([
                    ("Goal-setting and Achievement",
                     "<p>Establishing and reaching personal and professional objectives, "
                     "fostering motivation, accountability and continuous growth.</p>"),
                    ("Inner Power and Strength",
                     "<p>Cultivating mental fortitude, self-confidence and the resilience to "
                     "navigate challenges and thrive in diverse situations.</p>"),
                    ("First Impression Mastery",
                     "<p>Creating positive, memorable and influential initial interactions, "
                     "and establishing connections that last.</p>"),
                    ("Confident Interaction with Diverse Individuals",
                     "<p>Assertive communication, adaptability and cultural sensitivity when "
                     "engaging with people from various backgrounds and perspectives.</p>"),
                    ("Effective Communication and Results-oriented Messaging",
                     "<p>Delivering information with precision and persuasiveness, focused on "
                     "specific, measurable outcomes.</p>"),
                    ("Optimal Presentation Structure and Delivery",
                     "<p>Organising and presenting information with meticulous planning, "
                     "engaging content and techniques that captivate an audience.</p>"),
                    ("Improved Email Communication Proficiency",
                     "<p>Professional written communication with clarity, concision and "
                     "effective message delivery across workplace contexts.</p>"),
                    ("Stress Management Techniques",
                     "<p>Strategies to mitigate stress, promote well-being and sustain "
                     "productivity in demanding professional environments.</p>"),
                    ("Enhanced Active Listening Skills",
                     "<p>Attentively and empathetically absorbing information, promoting "
                     "effective interpersonal communication and mutual understanding.</p>"),
                    ("Conflict Resolution Strategies",
                     "<p>Constructive techniques to address and resolve conflict, fostering "
                     "collaboration and positive working relationships.</p>"),
                    ("Overcoming Communication Barriers",
                     "<p>Finding ways to communicate clearly and persuasively even in "
                     "challenging or complex situations.</p>"),
                ]),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
    ],
    "Sales Training — FemmForce",
    "A gender-inclusive approach to sales training: goal setting, first impressions, "
    "presentation, active listening, conflict resolution and results-oriented messaging."))

# 6 — Leadership
pages.append(training_page(
    5, ["Leadership", "Training."],
    "Leadership training hones the skills necessary to guide and inspire a team, and plays "
    "a pivotal role in retaining motivated, high-performing employees.",
    [
        section(head2("Why it matters", "Fresh perspective, faster decisions.", "")
                + """  <div class="rich" data-rv="rise">
    <p>Through targeted training topics, leaders gain fresh perspectives on their roles and
      sharpen their problem-solving. Leadership training also fosters a deep understanding of
      employee needs and organisational efficiency, ultimately boosting confidence and
      equipping leaders to make informed and swift decisions.</p>
  </div>"""),
        section(head2("Topics", "Twelve areas of leadership practice.", "", width="17ch")
                + cells([
                    ("Conflict Resolution",
                     "<p>Resolve workplace conflict promptly and effectively, fostering "
                     "cooperation, productivity and employee retention.</p>"),
                    ("Dealing with Change",
                     "<p>Tools to help employees navigate and leverage change, promoting "
                     "adaptability and resilience in the face of uncertainty.</p>"),
                    ("Problem-Solving",
                     "<p>Identify and address challenges in a positive and effective manner, "
                     "leading to smoother operations.</p>"),
                    ("Leading Innovation",
                     "<p>Cultivate a culture of innovation to stay competitive, boost employee "
                     "satisfaction and meet client needs effectively.</p>"),
                    ("Virtual Leadership",
                     "<p>Manage and lead remote teams, with emphasis on communication, "
                     "engagement and technical proficiency.</p>"),
                    ("Project Planning and Delegating",
                     "<p>Planning and delegation skills that ensure efficient task management "
                     "and accountability within the team.</p>"),
                    ("Building Trust and Respect",
                     "<p>Transparent communication and consistent leadership, which is what "
                     "trust and respect are actually made of.</p>"),
                    ("Coaching for Performance Improvement",
                     "<p>Coaching techniques that empower employees, recognise their "
                     "contributions and drive performance.</p>"),
                    ("Effective Meeting Management",
                     "<p>Strategies for productive and purposeful meetings, optimising time "
                     "and resources.</p>"),
                    ("Motivation and Encouragement",
                     "<p>Motivate employees to reach their full potential, boosting "
                     "performance and company success.</p>"),
                    ("Effective Communication Skills",
                     "<p>Communication techniques that build strong working relationships and "
                     "keep interactions clear and constructive.</p>"),
                    ("Time and Energy Management",
                     "<p>Treat time as an asset, prioritise effectively, and invest in "
                     "employee well-being for productivity and morale.</p>"),
                ]),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
    ],
    "Leadership Training — FemmForce",
    "Conflict resolution, change, innovation, virtual leadership, delegation, coaching for "
    "performance and meeting management — twelve leadership topics."))

# 7 — Customised
pages.append(training_page(
    6, ["Customised", "Training."],
    "Customised training topics are tailored to meet the specific needs and objectives of a "
    "particular group or organisation. They vary widely based on industry, roles and the "
    "goals of the participants.",
    [section(head2("Examples", "Fourteen starting points.",
                   "Bracketed terms are filled in with your industry, department, product "
                   "or job role. These are examples, not a catalogue &mdash; a customised "
                   "programme is scoped from your requirement.")
             + cells([
                 ("Entrepreneurs Development Program",
                  "<p>Business planning, marketing, finance and leadership skills for aspiring "
                  "business owners, fostering growth and success in their ventures.</p>"),
                 ("Import and Export",
                  "<p>Customs documentation, international trade laws, logistics, tariffs and "
                  "compliance for efficient global business operations.</p>"),
                 ("Sales Techniques for [Industry / Product]",
                  "<p>Specialised sales training for a particular industry or product line, "
                  "focused on unique selling points and customer pain points.</p>"),
                 ("Customer Service Excellence in [Industry]",
                  "<p>Customer service training tailored to industry-specific challenges and "
                  "customer expectations.</p>"),
                 ("Leadership Development for [Department / Team]",
                  "<p>Leadership training addressing the specific needs and dynamics of one "
                  "department or team.</p>"),
                 ("Digital Marketing Strategies for [Audience]",
                  "<p>Tactics and platforms most relevant to a specific target audience.</p>"),
                 ("Safety Protocols in [Industry / Environment]",
                  "<p>Modules addressing the safety concerns and regulations of a particular "
                  "industry or work environment.</p>"),
                 ("Compliance and Regulations for [Industry]",
                  "<p>Ensuring employees are well-versed in industry-specific compliance "
                  "requirements and regulations.</p>"),
                 ("Technical Skills for [Job Role]",
                  "<p>Hands-on technical training aligned to specific job roles and "
                  "responsibilities within an organisation.</p>"),
                 ("Team Building for [Department / Team]",
                  "<p>Exercises and workshops built for the dynamics and goals of a particular "
                  "team.</p>"),
                 ("Project Management for [Project Type]",
                  "<p>Project management training focused on the types of project an "
                  "organisation typically undertakes.</p>"),
                 ("Crisis Management and Response in [Industry]",
                  "<p>Industry-specific crisis scenarios and effective response "
                  "strategies.</p>"),
                 ("Innovation and Product Development",
                  "<p>Innovation processes and product development strategies relevant to a "
                  "specific industry.</p>"),
                 ("Diversity and Inclusion in [Workplace]",
                  "<p>Training addressing the specific challenges and opportunities within a "
                  "particular workplace culture.</p>"),
             ]))],
    "Customised Training — FemmForce",
    "Training programmes built to one organisation, department or industry — from "
    "entrepreneurship and import/export to compliance, crisis management and inclusion."))

# 8 — Campus to Corporate
c2c_topics = [
    ("Communication Skills", ["Verbal", "Non-verbal", "Listening skills", "Writing skills",
                              "Questioning skills"]),
    ("Presentation Skills", ["Fundamentals of an effective presentation",
                             "The 5 P&rsquo;s of an effective presentation",
                             "Importance of visual aids",
                             "Understanding and overcoming fear", "Public speaking",
                             "Managing voice and language",
                             "Managing the question and answer session"]),
    ("Goal Setting", ["Importance of a mission statement", "Establishing SMART goals",
                      "Procrastination", "Formulation of goals", "Visualisation of goals"]),
    ("Time Management", ["Prioritisation", "Dealing with difficult tasks",
                         "Getting organised", "Getting away from distractions",
                         "Work-life balance"]),
    ("Business Etiquette", ["Making the first impression", "Importance of handshakes",
                            "Business card etiquette", "Grooming and personal hygiene",
                            "Body language", "Telephone and email etiquette"]),
    ("Conflict Management", ["Creating a win-win situation", "Negotiation and persuasion",
                             "Dealing with aggressive behaviour",
                             "Different styles of handling conflict",
                             "Dealing with emotions", "Conflict resolution strategies",
                             "Tools and techniques for conflict management"]),
    ("Role of Attitude", ["Positive mental attitude", "Career planning",
                          "Stress management", "Anger management"]),
    ("Facing Interviews", ["Preparing to face interviews", "Group discussion",
                           "Resume building", "Body language, grooming and dressing"]),
    ("Interpersonal and Team Skills", ["Initiating small talk", "Managing relationships",
                                       "Understanding cultural diversity",
                                       "Team-building process and techniques",
                                       "Coordination in teams",
                                       "Assertive communication with teams",
                                       "Balancing team and individual needs"]),
]
pages.append(training_page(
    7, ["Campus to", "Corporate."],
    "A specialised programme that helps students move from academic life into the "
    "professional world &mdash; the soft skills, the mindset shift, and the confidence to "
    "start a career rather than just a job.",
    [
        section(head2("Objectives", "Six things the programme sets out to do.",
                      "It focuses on effective communication, time management and the "
                      "necessary mindset shift, with tools for goal setting, teamwork and "
                      "stress management.", width="19ch")
                + checks([
                    "Enhancing spoken, written and presentation skills",
                    "Practical career guidance and corporate expectations",
                    "Equipping students for a seamless transition into corporate environments",
                    "Guidance on resume writing, interview skills and corporate etiquette",
                    "Fostering confidence, self-esteem and a positive attitude",
                    "Addressing personal development through interactive Q&amp;A sessions"])),
        section(head2("Curriculum", "Nine modules.",
                      "Delivered over a programme sized to the institution.", width="14ch")
                + cells([(t, "", bullets(items)) for t, items in c2c_topics], cls="tight"),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
        section(head2("Outcomes", "What a graduate leaves able to do.", "", width="19ch")
                + checks([
                    "Goal-setting and achievement", "Inner strength development",
                    "First impression mastery",
                    "Confident interaction with diverse individuals",
                    "Effective communication and results-oriented messaging",
                    "Optimal presentation structure and delivery",
                    "Improved email communication proficiency",
                    "Stress management techniques for the workplace",
                    "Enhanced active listening", "Conflict resolution strategies",
                    "Overcoming communication barriers"])),
    ],
    "Campus to Corporate Training — FemmForce",
    "Communication, presentation, goal setting, time management, business etiquette, "
    "conflict management and interview skills — taking graduates into a first role."))

# 9 — Train the trainers
pages.append(training_page(
    8, ["Train the", "Trainers."],
    "FemmForce holds an extensive network of highly qualified trainers &mdash; more than "
    "300 of them. This programme is how that network is built and kept to standard.",
    [
        section(head2("The network", "Expertise, then range.", "")
                + """  <div class="rich" data-rv="rise">
    <p>The pool ensures a diverse range of specialised knowledge and tailored programmes,
      enabling impactful training solutions for individuals and organisations. Clients can
      expect high-quality, customised training experiences &mdash; which is only true if the
      trainers themselves are trained.</p>
  </div>"""),
        section(head2("The programme", "Six areas.", "", width="12ch")
                + cells([
                    ("Training Need Analysis",
                     "<p>Evaluating the specific learning requirements of individuals or "
                     "groups so that programmes are customised to their needs and maximise "
                     "effectiveness.</p>"),
                    ("Public Speaking",
                     "<p>Communicating confidently and effectively in front of an audience "
                     "&mdash; a crucial skill for trainers and trainees alike.</p>"),
                    ("Presentation Skills",
                     "<p>Techniques for creating and delivering engaging, informative "
                     "presentations that transfer knowledge and hold a room.</p>"),
                    ("Writing Content, Objectives and Outcomes",
                     "<p>Crafting training materials with clear objectives and desired "
                     "learning outcomes, well-structured and aligned to the training "
                     "goals.</p>"),
                    ("Time Management",
                     "<p>Prioritising tasks and using time efficiently &mdash; critical for "
                     "trainers and trainees to maximise productivity during sessions.</p>"),
                    ("Goal Setting, Delegation &amp; Teamwork",
                     "<p>Establishing clear objectives for sessions, assigning tasks "
                     "effectively, and promoting collaboration among participants.</p>"),
                ]),
                style="background:var(--bg-1);border-top:1px solid var(--line)"),
    ],
    "Train the Trainers — FemmForce",
    "Training-need analysis, public speaking, presentation skills, content design, time "
    "management and delivery — for the network of 300+ FemmForce trainers."))


# ── Media ───────────────────────────────────────────────────────────────
def holds(n, caption):
    return "\n".join(
        '    <figure class="hold"><figcaption>%s</figcaption></figure>' % caption
        for _ in range(n))


GALLERY_NOTE = """  <div class="empty" data-rv="rise" style="margin-top:2.4rem;max-width:62ch">
    <p style="margin-bottom:0">The frames above are placeholders. FemmForce holds
      photography from its programmes and events; it has not yet been added to this site.
      Stock imagery of beneficiaries was ruled out deliberately &mdash; the real pictures
      are worth waiting for. To add them, drop an
      <code>&lt;img&gt;</code> into each <code>&lt;figure&gt;</code> and remove the
      <code>hold</code> class.</p>
  </div>"""

videos = "\n\n".join([
    hero([("Home", "index.html"), ("Media", None), ("Videos", None)],
         ["Videos."],
         "Talks, event footage and recordings from the FemmForce programme."),
    section(head2("Footage", "One event, so far.", "", width="14ch")
            + """  <div class="gal">
    <figure class="hold"><figcaption>Ubuntu Consortium &mdash; Together we grow &middot; 18 Nov 2023</figcaption></figure>
  </div>
  <p style="margin-top:2rem" data-rv="rise"><a class="btn"
    href="event-ubuntu-consortium.html"><span>About the event</span></a></p>"""
            + GALLERY_NOTE),
    GENERAL_CTA,
])
pages.append(document("media-videos.html", "Videos — FemmForce",
                      "Talks and event footage from FemmForce, including the Ubuntu "
                      "Consortium day in Bengaluru.",
                      "media-videos", videos))

photos = "\n\n".join([
    hero([("Home", "index.html"), ("Media", None), ("Photos", None)],
         ["Photos."],
         "From the programmes, the training rooms and the events."),
    section(head2("Gallery", "From the programmes.", "", width="14ch")
            + '  <div class="gal">\n%s\n  </div>' % holds(8, "FemmForce programme")
            + GALLERY_NOTE),
    GENERAL_CTA,
])
pages.append(document("media-photos.html", "Photos — FemmForce",
                      "Photographs from FemmForce programmes, training sessions and events.",
                      "media-photos", photos))

ptt = "\n\n".join([
    hero([("Home", "index.html"), ("Media", None), ("POSH Trainer Programme", None)],
         ["POSH Trainers", "Trainee Programme."],
         "The cohort that trains to become external Internal-Committee members and POSH "
         "trainers."),
    section(head2("Gallery", "The trainee cohort.", "", width="14ch")
            + '  <div class="gal">\n%s\n  </div>' % holds(6, "POSH Trainers Trainee Programme")
            + GALLERY_NOTE),
    section(head2("The programme", "Where these trainers end up.", "", width="16ch")
            + """  <div class="rich" data-rv="rise">
    <p>Trainees from this programme join the FemmForce network of more than 300 qualified
      trainers, and are deputed as external members to Internal Committees under the POSH
      Act &mdash; the role the trust has now filled for more than 20 organisations across
      India.</p>
    <p style="margin-bottom:0"><a class="btn" href="training-posh.html"><span>POSH
      Training</span></a></p>
  </div>""",
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    GENERAL_CTA,
])
pages.append(document("media-posh-trainers.html",
                      "POSH Trainers Trainee Programme — FemmForce",
                      "The FemmForce POSH Trainers Trainee Programme cohort — the "
                      "trainees who become external Internal-Committee members.",
                      "media-posh-trainers", ptt))


# ── Brochures and Forms ─────────────────────────────────────────────────
BROCHURES = [
    ("FemmForce Brochure", "The whole trust in one document.",
     "https://1cc2f8ee-b8e2-4dcc-84ff-6b742b537c52.filesusr.com/ugd/fe689e_efe521b2848f46c181270b17823403f9.pdf"),
    ("Women at Business Brochure", "The three Diva groups, and what each one gets.",
     "https://1cc2f8ee-b8e2-4dcc-84ff-6b742b537c52.filesusr.com/ugd/fe689e_8e7293cf45204ce7a5de556cee8b129d.pdf"),
    ("Women at Work Brochure", "Finishing school, upskilling and career re-entry.",
     "https://1cc2f8ee-b8e2-4dcc-84ff-6b742b537c52.filesusr.com/ugd/fe689e_d0266e0671bd40b9b167db492f6c1d56.pdf"),
    ("POSH Training Brochure", "Compliance under the 2013 Act, and what an engagement covers.",
     "https://1cc2f8ee-b8e2-4dcc-84ff-6b742b537c52.filesusr.com/ugd/fe689e_b846486eb1b64b24b255890f84c75553.pdf"),
    ("Campus to Corporate Brochure", "The programme that takes graduates into a first role.",
     "https://1cc2f8ee-b8e2-4dcc-84ff-6b742b537c52.filesusr.com/ugd/fe689e_0e6290809c284319a317d5639f8e3df7.pdf"),
]
broch_rows = "\n".join(
    '    <a href="%s" target="_blank" rel="noopener" data-rv="rise">'
    '<span class="n">%02d</span><span class="t">%s</span>'
    '<span class="d">%s &middot; PDF</span></a>' % (url, i + 1, name, desc)
    for i, (name, desc, url) in enumerate(BROCHURES))

brochures = "\n\n".join([
    hero([("Home", "index.html"), ("Brochures &amp; forms", None)],
         ["Brochures", "and forms."],
         "Five downloadable brochures covering the trust and its main programmes."),
    section(head2("Brochures", "Five PDFs.", "", width="12ch")
            + '  <div class="index">\n%s\n  </div>' % broch_rows
            + """
  <div class="empty" data-rv="rise" style="margin-top:2.6rem;max-width:62ch">
    <p style="margin-bottom:0">These files are still hosted on the previous website&rsquo;s
      file store and open in a new tab. Move the PDFs into this repository and point the
      links at local paths before that host is retired.</p>
  </div>"""),
    section(head2("Forms", "Registration goes by email, for now.",
                  "This site is static and has no form backend. Each of these opens a "
                  "pre-addressed email; a form service or payment link can replace them "
                  "later.", width="19ch")
            + cells([
                ("Training enquiry",
                 "<p>For corporates and institutions commissioning any of the nine "
                 "programmes.</p>",
                 '<p style="margin-top:1.5rem"><a class="btn" href="%s"><span>Send an '
                 'enquiry</span></a></p>' % mailto("Training enquiry")),
                ("Trainer empanelment",
                 "<p>For trainers who want to join the network of 300+.</p>",
                 '<p style="margin-top:1.5rem"><a class="btn" href="%s"><span>Register as a '
                 'trainer</span></a></p>' % mailto("Trainer empanelment registration")),
                ("Partner registration",
                 "<p>For corporates, institutions, government bodies, trade associations "
                 "and volunteers.</p>",
                 '<p style="margin-top:1.5rem"><a class="btn" href="%s"><span>Partner with '
                 'us</span></a></p>' % mailto("Partner registration — FemmForce")),
            ], numbered=False),
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    GENERAL_CTA,
])
pages.append(document("brochures-and-forms.html", "Brochures &amp; Forms — FemmForce",
                      "Downloadable FemmForce brochures for the trust, Women at Business, "
                      "Women at Work, POSH Training and Campus to Corporate, plus enquiry "
                      "and registration routes.",
                      "brochures-and-forms", brochures))


# ── Events ──────────────────────────────────────────────────────────────
EVENTS = [
    ("event-ubuntu-consortium.html", "Ubuntu Consortium &mdash; Together We Grow",
     "Sat 18 Nov 2023", "9:30 am &ndash; 5:00 pm",
     "1 Palace Road, Ambedkar Veedhi, Bengaluru, Karnataka 560001, India"),
    ("event-femmforce.html", "FemmForce",
     "Thu 19 Oct 2023", "3:00 pm &ndash; 5:30 pm",
     "#1341/A, 8th C Cross, 9th Main Road, 1st Phase Girinagar, 2nd Phase Banashankari, "
     "Bengaluru, Karnataka 560085, India"),
]
event_rows = "\n".join(
    '    <a href="%s" data-rv="rise">\n'
    '      <span class="date">%s<br>%s</span>\n'
    '      <div><h3>%s</h3><p class="loc">%s</p></div>\n'
    '      <span class="ring" aria-hidden="true"></span>\n'
    '    </a>' % (href, date, time, name, loc)
    for href, name, date, time, loc in EVENTS)

events = "\n\n".join([
    hero([("Home", "index.html"), ("Events", None)],
         ["Events."],
         "Days FemmForce runs or takes part in &mdash; consortium meetings, recognition "
         "events and the programmes that come out of them."),
    section(head2("Upcoming", "Nothing scheduled.", "", width="14ch")
            + """  <div class="empty" data-rv="rise" style="max-width:62ch">
    <p>No events at the moment.</p>
    <p style="margin-bottom:0">Subscribe on the home page, or
      <a href="mailto:info@femmforce.in" style="border-bottom:1px solid var(--line-2)">email
      the trust</a>, and you will hear about the next one before it is announced.</p>
  </div>"""),
    section(head2("Past events", "What has already happened.", "", width="14ch")
            + '  <div class="events">\n%s\n  </div>' % event_rows,
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    GENERAL_CTA,
])
pages.append(document("events.html", "Events — FemmForce",
                      "FemmForce events in Bengaluru, including the Ubuntu Consortium "
                      "“Together We Grow” day in November 2023.",
                      "events", events))

ubuntu = "\n\n".join([
    hero([("Home", "index.html"), ("Events", "events.html"), ("Ubuntu Consortium", None)],
         ["Ubuntu Consortium", "Together We Grow."],
         "A day connecting women entrepreneurs to public sector undertakings, and putting "
         "policy and institutional support in front of the people who need it."),
    section(head2("Details", "When and where.", "", width="12ch")
            + """  <div class="note" data-rv="rise">
    <dl class="kv">
      <dt>Date</dt><dd>Saturday 18 November 2023</dd>
      <dt>Time</dt><dd>9:30 am &ndash; 5:00 pm</dd>
      <dt>Location</dt><dd>1 Palace Road, Ambedkar Veedhi, Bengaluru, Karnataka 560001, India</dd>
      <dt>Contact</dt><dd><a href="tel:+919880438607">+91 98804 38607</a></dd>
    </dl>
  </div>"""),
    section(head2("About the event", "Four things it set out to do.", "", width="17ch")
            + checks([
                "Exploring global business opportunities",
                "Connecting women entrepreneurs to PSUs",
                "Awareness of policies and institutional support",
                "Recognition of hidden gems &mdash; women entrepreneurs"])
            + """
  <p style="margin-top:2.6rem" data-rv="rise">
    <a class="btn btn-solid" href="https://www.femmforce.in/event-details/ubuntu-consortium-together-we-grow"
      target="_blank" rel="noopener"><span>Registration page</span></a>
    <a class="btn" href="media-videos.html" style="margin-left:.6rem"><span>Event footage</span></a>
  </p>""",
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    pager(None, ("event-femmforce.html", "FemmForce &middot; 19 Oct 2023")),
    GENERAL_CTA,
])
pages.append(document("event-ubuntu-consortium.html",
                      "Ubuntu Consortium: Together We Grow — FemmForce",
                      "18 November 2023 in Bengaluru — connecting women entrepreneurs "
                      "to PSUs, global business opportunities, policy awareness and "
                      "recognition.",
                      "event-ubuntu-consortium", ubuntu))

ff_event = "\n\n".join([
    hero([("Home", "index.html"), ("Events", "events.html"), ("FemmForce", None)],
         ["FemmForce", "October 2023."],
         "An afternoon session in Banashankari, Bengaluru."),
    section(head2("Details", "When and where.", "", width="12ch")
            + """  <div class="note" data-rv="rise">
    <dl class="kv">
      <dt>Date</dt><dd>Thursday 19 October 2023</dd>
      <dt>Time</dt><dd>3:00 pm &ndash; 5:30 pm</dd>
      <dt>Location</dt><dd>#1341/A, 8th C Cross, 9th Main Road, 1st Phase Girinagar,
        2nd Phase Banashankari, Bengaluru, Karnataka 560085, India</dd>
      <dt>Contact</dt><dd><a href="tel:+919880438607">+91 98804 38607</a></dd>
    </dl>
  </div>"""),
    section(head2("About the event", "No description was published.", "", width="18ch")
            + """  <div class="empty" data-rv="rise" style="max-width:62ch">
    <p style="margin-bottom:0">The original listing for this event carried only a date and a
      location &mdash; no description was published for it. If you have notes or photographs
      from the day, <a href="mailto:info@femmforce.in"
      style="border-bottom:1px solid var(--line-2)">send them over</a> and this page can be
      filled in properly.</p>
  </div>""",
            style="background:var(--bg-1);border-top:1px solid var(--line)"),
    pager(("event-ubuntu-consortium.html", "Ubuntu Consortium &middot; 18 Nov 2023"), None),
    GENERAL_CTA,
])
pages.append(document("event-femmforce.html", "FemmForce, October 2023 — Events",
                      "FemmForce event on 19 October 2023 in Banashankari, Bengaluru.",
                      "event-femmforce", ff_event))


# ── Blog ────────────────────────────────────────────────────────────────
blog = "\n\n".join([
    hero([("Home", "index.html"), ("Blog", None)],
         ["Blog."],
         "Writing from the trust &mdash; currently open to members only."),
    section(head2("Members only", "Behind a login.",
                  "The blog was set up as a members-only section, and it stayed that way "
                  "through the move to this site.", width="12ch")
            + """  <div class="empty" data-rv="rise" style="max-width:62ch">
    <p>There is no member login on this site yet. It is served as static files with no
      backend, so a login would need a third-party service &mdash; or the blog could simply
      be opened to everyone, which is the better answer for an organisation that wants to be
      found.</p>
    <p style="margin-bottom:0">Until then: join as a member for the mailing list and event
      invitations, or email the trust directly.</p>
  </div>
  <p style="margin-top:2.6rem" data-rv="rise">
    <a class="btn btn-solid" href="membership.html"><span>Become a member</span></a>
    <a class="btn" href="mailto:info@femmforce.in" style="margin-left:.6rem"><span>Email the
      trust</span></a>
  </p>"""),
    GENERAL_CTA,
])
pages.append(document("blog.html", "Blog — FemmForce",
                      "The FemmForce blog is a members-only section. Join as a member or "
                      "contact the trust directly.",
                      "blog", blog))


# ── page-template.html ──────────────────────────────────────────────────
# Kept in sync with the real pages so that hand-authoring a new one starts
# from the current masthead and footer rather than a stale copy.
TEMPLATE_BODY = """<!-- PAGE HEAD. No <canvas class="field"> here: the drifting form field is
     the home hero's one orchestrated moment and stays there. Three <b> in
     the aura is the house amount for a page head. -->
%(hero)s

<!-- CONTENT. Use the components already in assets/css/site.css — .cells,
     .checks, .index, .two, .rich, .tbl, .note, .gal, .events, .pager.
     Do not invent a parallel one without adding it to the stylesheet and
     to DESIGN.md §5. -->
%(body)s

<!-- PREV / NEXT, only where the page belongs to a set (cohorts, training,
     events). Delete otherwise. -->
%(pager)s

%(cta)s""" % {
    "hero": hero([("Home", "index.html"), ("Section", None), ("Page title", None)],
                 ["Page headline", "on two lines."],
                 "One or two sentences of standfirst, in the organisation&rsquo;s own "
                 "words wherever possible."),
    "body": section(head2("Kicker", "Section heading.",
                          "An optional standfirst under the heading.")
                    + cells([("Column one", "<p>Body copy.</p>"),
                             ("Column two", "<p>Body copy.</p>"),
                             ("Column three", "<p>Body copy.</p>")])),
    "pager": pager(("index.html", "Previous page"), ("index.html", "Next page")),
    "cta": GENERAL_CTA,
}

_tpl = (HEAD % {"title": "PAGE TITLE — FemmForce",
                "desc": "ONE SENTENCE DESCRIBING THIS PAGE.",
                "bodycls": ""}
        ).replace('<link rel="icon"',
                  '<!-- remove the next line once this becomes a real page -->\n'
                  '<meta name="robots" content="noindex">\n<link rel="icon"')
with io.open(os.path.join(ROOT, "page-template.html"), "w",
             encoding="utf-8", newline="\n") as _f:
    _f.write(_tpl + masthead("") + "\n\n" + TEMPLATE_BODY.strip() + "\n\n" + FOOTER
             + '\n\n<script src="assets/js/site.js" defer></script>\n</body>\n</html>\n')
pages.append("page-template.html")


if __name__ == "__main__":
    for p in sorted(pages):
        print(p)
    print("\n%d pages written." % len(pages))
