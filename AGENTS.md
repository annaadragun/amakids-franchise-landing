# Project instructions

## Source of truth

- `ready-for-develop/` is the canonical source for the franchise landing page and the only folder published by GitHub Pages.
- Make all page, style, script, copy, and asset changes in `ready-for-develop/`.
- `amakids-local/` is an archive of the downloaded source site and previous working files. Do not edit it as the primary implementation. If the user points to a file there, apply the requested change to the corresponding implementation in `ready-for-develop/`.
- Keep the page self-contained: use local, relative asset paths and put every required production asset inside `ready-for-develop/`.
- Preserve editable source files for designed assets (for example SVG cover artwork) alongside the production files when available.

## Before finishing a page change

- Confirm that every local image, video, stylesheet, script, font, and download referenced by `ready-for-develop/index.html` or its CSS exists inside `ready-for-develop/`.
- Keep `ready-for-develop/README.md` and `ready-for-develop/CONTENT-PLAN.md` in sync when the handoff structure or page content changes.
- GitHub Pages deployment is configured in `.github/workflows/deploy-pages.yml` to publish `ready-for-develop/`. Do not change that path unless the user asks to change the deployment source.
