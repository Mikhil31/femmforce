# FemmForce

Website for FemmForce, a registered trust in Bangalore that trains women, funds them,
places them into work, and makes workplaces safe under the POSH Act.

**Live: <https://mikhil31.github.io/femmforce/>**

Static HTML, CSS and JavaScript — no framework, no backend. 29 pages: the four
beneficiary groups, nine training programmes, partners, membership, media, events.

`index.html` is the home page; every other page is a folder with an `index.html`.
`assets/` holds the stylesheet, script and images. `brand/` holds the logo and
favicons. `tools/build.py` generates the pages.

Push to `main` and GitHub Pages redeploys it. Keep `.nojekyll`.

Design tokens, components and house rules are in [DESIGN.md](DESIGN.md).
