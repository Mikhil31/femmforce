# FemmForce — design system & build notes

Status: **all 27 pages built and deployable.** Home, About, Activities, the four
beneficiary pages, How We Do, Partners, Membership, the nine training pages, three
media pages, Brochures & Forms, Events plus two event details, and Blog.

Still missing content rather than design: photography (§10).

---

## 1. Canonical files

| Path | What it is |
|---|---|
| `tools/build.py` | **Generates every page.** The masthead, footer and all page copy live here, once. See §8. |
| `index.html` | The home page, and the only HTML file at the repo root. |
| `<name>/index.html` | Every other page. A directory per page, so the URL is `/about-us/` and not `/about-us.html`. |
| `assets/css/site.css` | Every style for the whole site. One file, shared by all pages. |
| `assets/js/site.js` | Every behaviour for the whole site. One file, shared by all pages. |
| `assets/img/select/` | Temporary. Thumbnails for the client photo picker (§11). |
| `.nojekyll` | Required. See §3. |
| `brand/` | Logo, favicons, social images. Generated — see `brand/README.md`. |
| `tools/page-template.html` | A blank page in the current house style. Generated; carries `noindex`. |

**Gitignored working folders** — on disk, deliberately not in the repo:

| Path | What it is |
|---|---|
| `docs/` | `FemmForce-Website-Content.docx` (the copy source for all 26 original pages), `_design/` (superseded early versions), and `tools/` (the one-off image-sourcing scripts). |
| `candidates/` | The 43MB photo review set. |
| `.env.local` | The Pexels API key. Never commit it. |

### URL layout

Every page is a directory with an `index.html`. That gives clean URLs (`/training/posh/`
rather than `/training-posh.html`) and leaves one HTML file at the repo root instead of
twenty-nine.

The generator still speaks flat slugs internally — `"training-posh.html"` everywhere in
`build.py`. The mapping to a directory lives in one place, `ROUTES`, and `document()`
rewrites every `href` and `src` at write time into the right number of `../` hops. So a
link is written once, plainly, and comes out correct whether the page sits at the root
or two levels down. **Nothing else in the file needs to know how deep a page is** — which
is the whole point, because getting that wrong by hand is how a nav breaks.

Add a page: add it to `ROUTES`, and the rest follows.

**Edit the HTML or edit the generator — but know which.** Page copy and structure
live in `tools/build.py`; running it overwrites every root `.html`. If you hand-edit
a page and then someone runs the build, your edit is gone. Either put the change in
`build.py`, or delete `build.py` and own the 27 copies of the nav by hand. The
deployed site does not care: it is the same static files either way.

## 2. Running it locally

```bash
python -m http.server 5173
```

Then open `http://localhost:5173/`. It must be served over HTTP, not opened as
`file://` — the logo and stylesheet are root-relative and won't resolve otherwise.

## 3. Deploying to GitHub Pages

It is pure static HTML/CSS/JS. No build step, no bundler, no backend. Push the
repo, set Pages to serve from the branch root, done.

Two things that will silently break it:

- **`.nojekyll` must exist at the repo root.** GitHub Pages runs Jekyll by
  default, and Jekyll refuses to publish any file or folder whose name starts
  with `_`. Without this file, `_design/` disappears. It's an empty file; don't
  delete it.
- **Asset paths are root-relative** (`assets/…`, `brand/…`). Every page must sit
  at the repo root, not in a subfolder. If you ever nest a page one level deep,
  every path in it needs a `../`.

The only third-party request is Google Fonts. Self-hosting the single
`Familjen Grotesk` woff2 would remove it — faster in India, and sidesteps the
GDPR objections some organisations have to Google Fonts. Not done yet.

---

## 4. Design tokens

All in `:root` at the top of `site.css`. Never hard-code a colour or a size.

### Colour

The five brand values are **measured from the logo artwork** and documented in
`brand/README.md`. Do not invent new brand colours.

```
--red    #C81E14     --verm  #EC4008   ← primary brand colour
--orange #F0731A     --gold  #DBA22E
```
Each has a `-lift` variant for use on dark grounds.

Grounds and text:
```
--bg   #F3F1ED  warm porcelain   --bg-1 #EAE7E1   --bg-2 #E1DED7
--tx   #171412  ink              --tx-2 #585149   --tx-3 #8B8279
--line rgba(23,20,18,.13)        --line-2 rgba(23,20,18,.28)
```

**The single most important colour rule on this site: colour is a light source,
not a surface.** The brand hues are hot and analogous — all red-to-gold, no cool
note — so used as fills they shout and cheapen fast. They appear as soft
gradient wash, as hairlines, and as small accents. They never fill a block. An
earlier revision flooded whole rows with gold on hover and it looked terrible.

There is no cream anywhere. Cream `#F4F1EA` with a terracotta accent is a
recognisable generic-template pairing and the ground is deliberately greyer.

### Cohort colour code

The four beneficiary groups each own one hue, **on every page of the site**:

| Group | Hue |
|---|---|
| Women at Business | `--gold` |
| Women at Work | `--orange` |
| Women at Home | `--verm` |
| Underprivileged Women | `--red` |

This is information, not decoration. Keep it consistent or drop it entirely.

### Type

**One family: Familjen Grotesk.** Hierarchy comes from size and case only.
Do not add a second typeface — two reference sites studied for this project
(Age of Union, Surfers Against Sewage) each run a single grotesque across their
entire site, and it is what stops a content-heavy page fragmenting.

```
--t-hero clamp(2.6rem, 8.2vw, 7.4rem)   --t-h2 clamp(2rem, 5.4vw, 4.8rem)
--t-lede clamp(1.02rem, 1.45vw, 1.28rem)
```
Headings are uppercase with tight negative tracking (`-.05em` at hero size).
Body copy is capped at ~62ch.

### Motion easing

```
--ease cubic-bezier(.16,.84,.28,1)    general
--wipe cubic-bezier(.72,0,.16,1)      reveals, wipes, the nav capsule
```

---

## 5. Components

All already styled in `site.css`. Reuse them; don't invent parallel ones.

| Class | Use |
|---|---|
| `.wrap` | Page gutter + max width. Every section needs one. |
| `.lbl` | Small tracked kicker above a heading, with a facet marker. |
| `.mast` / `.bar` | Sticky masthead. Detaches into a floating capsule on scroll. |
| `.nav-i` / `.drop` | Nav item and its content panel. Add `.has` for a chevron + hover bridge. |
| `.nav-cta` | The Donate pill. |
| `.btn` / `.btn-solid` | Buttons. Fill wipes up from the bottom on hover. |
| `.cohort` | The four beneficiary rows. Colour-coded, hairline bar + soft bloom on hover. |
| `.ring` | The circular arrow affordance. Monochrome at every state — deliberately. |
| `.facts` | The counting statistics grid. |
| `.two` | Two-column bordered panel pair. |
| `.index` | Numbered list rows (used for the nine training programmes). |
| `.marq` | The looping partner-category ticker. |
| `.people` | Trustee cards. |
| `.aura` | Drifting gradient wash. Drop 2–3 `<b>` children inside. |
| `.field` | The canvas form field. **Home hero only.** |

Added in rev.5, for the inner pages:

| Class | Use |
|---|---|
| `.hero.page` | The page head. The hero without the canvas and without the full-height hold. Its aura carries a fade mask — see §7. |
| `.crumb` | Breadcrumb above the `h1`. Last item is a `<span>`, not a link. |
| `.cells` | The bordered panel grid — `.two` generalised to N columns. Add `.wide` or `.tight` to change the column floor. A cell may be an `<a>`. |
| `.checks` | Grid of short items with a facet marker. No descriptions; use `.cells` if you need them. |
| `.rich` | Long-form body copy, capped at 66ch. |
| `.tbl` | Data table. Wrap it in `.scroll` — it has a `min-width` and must scroll rather than squash. |
| `.note` + `.kv` | Bordered callout with a key/value list. Bank details, event details, registered details. |
| `.gal` | Gallery grid. `figure.hold` is the empty placeholder state (§10). |
| `.events` | Event rows: date, title + location, `.ring`. |
| `.empty` | Dashed empty state. Say what is missing and why, not "coming soon". |
| `.pager` | Previous / next within a set. `.none` for an absent end. |
| `.cta` | The closing band on an inner page. |

**Accent.** `--accent` / `--accent-lift` carry the cohort colour code through every
one of these. Set it once with a body class — `.acc-biz`, `.acc-work`, `.acc-home`,
`.acc-und` — and the label markers, hairlines, hover states and the nav underline
all follow. The default is vermilion, so pages with no cohort look exactly as before.

---

## 6. Motion system

Four rules:

1. **Transform and opacity only.** Never animate layout properties. The one
   exception is the canvas, which is discussed below.
2. **One orchestrated moment.** The home hero sequence is it. Everything else is
   a small response to scroll or hover.
3. **Every from-state is gated on `html.js`.** If JavaScript fails, nothing is
   hidden. Check this whenever you add a reveal.
4. **`prefers-reduced-motion` is honoured properly** — content still arrives, it
   just doesn't move. Test it.

Reveals: put `data-rv="rise"` or `data-rv="mask"` on an element. `site.js`
handles the rest. Stagger a group with `style="--d:130ms"`.

---

## 7. Things that already went wrong — don't repeat them

These cost real debugging time. All are fixed; all are easy to reintroduce.

**IntersectionObserver cannot see a clip-path-hidden element.**
`clip-path: inset(0 100% 0 0)` gives an element zero *visible* area, and IO
measures visible area — so a masked element can never trigger its own reveal.
Measured `intersectionRatio: 0` on an element sitting 207px down a 940px
viewport. Every heading on the page was invisible. `site.js` works around it by
observing the **parent** of any `data-rv="mask"` node. Keep that.

**IntersectionObserver misses fast scrolling.** It samples once per frame; flick
hard enough and an element is below the fold on one sample and above it on the
next, so it never fires and stays invisible *permanently*. Five training rows
did this on mobile. There's a debounced `sweep()` in `site.js` that reveals
anything already past the fold. Keep that too.

**`filter: blur()` on large animated elements destroys performance.** The
original hero used four 46vw elements with `blur(90px)` animating `scale`. Blur
is not composited, so every frame re-rasterised a huge surface — twice. The soft
look now comes from **radial gradients**, which are soft by nature and free.
Never reintroduce animated blur.

**Gradient end-stops must be `rgba(…, 0)`, not `transparent`.** `transparent`
interpolates through transparent-*black* and leaves a grey fringe on a light
ground.

**Canvas rasterisation is the one real cost on the page.** Measured: canvas off
59.9fps / 0 dropped frames, canvas on (15 stroked blobs at full res) 53.1fps /
14 dropped. Fixed by rendering into a **0.62-scale buffer** (`RES` in `site.js`)
and upscaling via CSS — invisible on out-of-focus shapes, ~60% fewer pixels
rasterised. Now ~58–60fps. If you add to the canvas, re-measure.

**The mobile menu button can be pushed off-screen.** At 360px the logo wordmark
+ Donate pill + burger did not fit, and the burger landed at x=390 in a 360px
viewport — masked by `overflow-x: clip`, so it produced no scrollbar and looked
fine while being completely unusable. The wordmark now hides below 560px and the
CTA below 400px. **Test every new header change at 360px.**

**Don't animate `border-radius` on many elements.** It's a paint operation, not
composited. That's why the form field moved to canvas.

**The Training mega-menu opened off the right edge of the screen.** The rule
`.nav-i:nth-last-child(-n+3) .drop{right:-.5rem}` was meant to right-align the last
menus. But `nav`'s children, counted from the end, are `.nav-mob-cta`, Events, Media,
*then* Training — so Training sat outside the selector, stayed left-aligned, and its
`min-width:640px` panel ran past the viewport at every width up to about 1750px.
`overflow-x: clip` swallowed the scrollbar, so it looked fine and was unusable. It is
`-n+4` now. **If you add or remove anything inside `nav`, recount.**

**A clipped aura reads as a filled block.** The page head is about a third the height
of the home hero, so the radial blobs get cut off by the hero box and the wash ends in
a straight horizontal edge across the page — colour behaving as a surface, which §4
forbids. `.hero.page .aura` and `.cta .aura` carry a static `mask-image` fade for this.
A mask is fine here: it is set once, the blobs inside still animate on transform alone,
and nothing re-rasterises per frame. Do not solve it with `filter: blur()`.

**An inline `style="--cols:2"` beats your media query.** Inline styles out-specify any
selector, so a custom property set inline cannot be overridden at a breakpoint — the
grid silently keeps its desktop column count on a phone. `.cells` uses
`repeat(auto-fit, minmax(min(100%, var(--min)), 1fr))` with `--min` set by a *class*
instead, which reflows on its own and needs no breakpoint at all. Prefer that shape.

**Reveal stagger has to be counted per container.** `site.js` used to number every
match of a selector across the whole document and cap the delay at 540ms. On a page
with three `.cells` blocks, every group after the first inherited the cap, so those
panels sat visibly waiting after they had already scrolled into view. It now counts
children within each container.

---

## 8. Adding or editing a page

Content and structure live in `tools/build.py`. Add an entry there and run:

```bash
python tools/build.py
```

It rewrites every root `.html` and prints what it wrote. There is no build step at
*deploy* time — the output is committed and served directly. The generator exists for
one reason: the masthead and footer are duplicated across 28 files, and hand-editing
28 copies of a nav is how a nav goes out of sync.

To add a page:

1. Add its slug, label and description to the relevant list at the top of `build.py`
   (`COHORTS`, `TRAINING`, `MEDIA`) if it belongs to a set — that wires up the nav
   drop-down and the prev/next pager automatically.
2. Build the body from the helpers: `hero`, `section`, `head2`, `cells`, `checks`,
   `index_rows`, `pager`, `cta`. They emit the §5 components with the right
   `data-rv` attributes already attached.
3. `pages.append(document(slug, title, description, nav_key, body))`.
4. Take copy from `FemmForce-Website-Content.docx` — it has the full verbatim text of
   all 26 original pages. Anything written for this build rather than lifted from the
   document is marked `# authored` in `build.py`.
5. Run the build. Check at **360px** and 1440px, and with reduced motion on.

If you would rather not run Python, delete `tools/build.py` and edit the HTML
directly. The pages stand alone — but then every nav change is 28 edits.

### Forms and buttons

Static hosting has no backend, so every "Register for…" button is a `mailto:` with a
pre-filled subject. That is honest and it works today. Replace them with a form
service or a payment link when there is one; the Donate button is still inert.

## 9. Site map

All 27 pages are built. Slugs are clean, not the Wix `copy-of-…` originals (Sales
Training used to live at `/copy-of-career-coaching-and-counselli`). If the old URLs
carry traffic, set up redirects — GitHub Pages needs a third-party service or meta
refresh stubs for that.

| Page | Slug |
|---|---|
| Home | `index.html` |
| About Us | `about-us.html` |
| Our Activities | `our-activities.html` |
| Women at Business / Work / Home / Underprivileged | `women-at-business.html`, `women-at-work.html`, `women-at-home.html`, `underprivileged-women.html` |
| How We Do (Grant Wave `#grant-wave`, Skill Fund `#skill-fund`, training list `#training`) | `how-we-do.html` |
| Our Partners | `our-partners.html` |
| Membership | `membership.html` |
| Training ×9 | `training-posh`, `-soft-skills`, `-it-technical`, `-career-coaching`, `-sales`, `-leadership`, `-customised`, `-campus-to-corporate`, `-train-the-trainers` |
| Media ×3 | `media-videos.html`, `media-photos.html`, `media-posh-trainers.html` |
| Brochures & Forms | `brochures-and-forms.html` |
| Events + 2 details | `events.html`, `event-ubuntu-consortium.html`, `event-femmforce.html` |
| Blog | `blog.html` |

There is no standalone Training index page; `how-we-do.html#training` is it, which
matches the original site where the Training menu items were the only route in.

## 10. Open items

- **Photography — decision reversed, deliberately.** The earlier note here said no
  stock imagery, on the grounds that stock photographs of beneficiaries are the
  NGO-site cliché. That still holds for *generic* stock. It does not hold for what is
  actually available: Pexels returns thousands of photographs of Indian women —
  founders, textile workers, graduates, farmers, women in training rooms in Delhi —
  and a real photograph of an Indian woman at work is not the cliché the original
  note was guarding against. A site about women that shows no women was the worse
  failure of the two.

  `python tools/fetch_images.py` pulls candidates into `candidates/` (gitignored) and
  builds `candidates/index.html` to pick from. Chosen files move into `assets/img/`.
  See §11.

  **Real photography still beats all of it.** The moment there are pictures of an
  actual FemmForce training session or the Ubuntu Consortium day, they replace the
  stock and the site improves. The three media pages are built and waiting:
  `.gal figure.hold` is the empty frame — drop an `<img>` in, remove the `hold`
  class, nothing else changes.
- The newsletter form and the **Donate button are inert**. Every other action on the
  site is now a `mailto:`, which works. Donate needs a real payment link.
- **Brochure PDFs still point at the old Wix file host**
  (`filesusr.com/ugd/…`). Move the five PDFs into the repo and repoint
  `brochures-and-forms.html` before that host is retired, or those links die.
- **No LinkedIn URL.** The content document lists `linkedin.com` with no profile
  path, so LinkedIn is omitted from the footer. Add it when someone has the real one.
- The **blog is members-only** and there is no member login on a static site. Either
  wire a third-party auth/newsletter service, or — better for an organisation that
  wants to be found — open it to everyone. `blog.html` currently explains the state
  honestly and routes to membership.
- The **wordmark typeface in the logo files is a stand-in** (Arial Black). See
  `brand/README.md` §"Two things still open".
- **Google Fonts is still the only third-party request.** Self-hosting the single
  `Familjen Grotesk` woff2 would remove it — faster in India, and it sidesteps the
  GDPR objection. Now that there are 28 pages, this is worth more than it was.

---

## 11. Photography

### Licence

Everything currently in `candidates/` is from **Pexels**: free for commercial use,
modification allowed, **no attribution required**. That is the reason it was chosen
over Wikimedia Commons, where most usable Indian material is CC BY-SA — which
requires credit *and* puts a share-alike obligation on any crop you make.

A credits page is still planned (§10), but with Pexels it is a courtesy, not a
licence condition. Photographer name, profile URL and source page are recorded in
each slot's `meta.json` so it can be generated rather than typed.

If you ever add a CC BY or CC BY-SA image, the credits page stops being optional and
**must be linked from every page's footer**. A credits page nothing links to does not
satisfy the licence.

### Pulling candidates

```bash
python tools/fetch_images.py                    # all 13 slots
python tools/fetch_images.py 03-women-at-work   # one slot
python tools/fetch_images.py --sheet            # rebuild the picker only
```

Needs `PEXELS_API_KEY` in `.env.local`. **That file is gitignored and must stay that
way.** `candidates/` is gitignored too — it is a 40MB review set, not site content.
Only the chosen files, once processed into `assets/img/`, belong in git.

Two traps, both already handled in the script, both worth knowing:

- **Pexels is behind Cloudflare and 403s Python's default user-agent** (error 1010).
  A browser `User-Agent` header is mandatory. This is not a bad key — a bad key
  returns 401.
- **`total_results` caps at 8000** on nearly every query, so it tells you nothing
  about whether a query is good. Judge by the pictures.

### Writing queries

Say "indian" and say the *situation*, not the mood. Asking for feeling gets stock
feeling: `women support group circle` returned wine toasts, wedding selfies and women
holding hands in a meadow. `indian women group meeting` returned the actual room.
Likewise `award ceremony india` returns military and police decorations — not the
kind of recognition this trust gives out.

Slots are ordered best-query-first and results are interleaved, so the top hit of
every query survives the per-slot cap. One broad query cannot fill a folder.
