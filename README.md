# FemmForce

The website for FemmForce, a registered trust in Bangalore that trains women, funds
them, places them into work, and makes workplaces safe under the POSH Act.

Pure static HTML, CSS and JavaScript. No bundler, no framework, no backend.

## Run it

```bash
python -m http.server 5173
```

Then open <http://localhost:5173/>. It must be served over HTTP — the stylesheet and
logo paths are root-relative and will not resolve from `file://`.

## Build the pages

The 28 root `.html` files are generated so that the masthead and footer exist in one
place rather than 28:

```bash
python tools/build.py
```

The output is committed and is what gets served. There is no build step at deploy
time.

## Deploy

Push, and point GitHub Pages at the branch root. Keep `.nojekyll` — without it Jekyll
refuses to publish `_design/`.

## Read this before changing anything

**[DESIGN.md](DESIGN.md)** — the design tokens, the component list, the motion rules,
and a list of the things that have already gone wrong here and should not be
reintroduced. `brand/README.md` covers the logo and favicon assets.
