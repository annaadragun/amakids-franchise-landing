# Project instructions

## Source of truth

- `ready-for-develop/` is the canonical source for the complete franchise website and the only source folder published by GitHub Pages.
- Make all page, style, script, copy, and asset changes in `ready-for-develop/`.
- `amakids-local/` is an archive of the downloaded source site and previous working files. Do not edit it as the primary implementation. If the user points to a file there, apply the requested change to the corresponding implementation in `ready-for-develop/`.
- Keep the page self-contained: use local, relative asset paths and put every required production asset inside `ready-for-develop/`.
- Preserve editable source files for designed assets (for example SVG cover artwork) alongside the production files when available.

## Website architecture

- `ready-for-develop/index.html` is the homepage route.
- Each top-level route has its own directory and `index.html`, for example `ready-for-develop/programs/index.html`. Keep routes clean and extension-free in navigation links.
- `ready-for-develop/shared/` contains website-wide styles, scripts, fonts, logos, and reusable UI. The shared header and route map live in `shared/scripts/site-shell.js`; update it when navigation changes.
- `ready-for-develop/modules/<module-name>/` contains assets and behavior owned by one page or feature. The existing homepage implementation lives in `modules/franchise-landing/`.
- New substantial pages should get their own module. Do not place page-specific code in `shared/`.
- All URLs must remain relative so the site works both at the latest Pages URL and below `/versions/<tag>/`.

## Publishing and versions

- A push to `main` republishes the latest site at the root GitHub Pages URL.
- A tag matching `v*` creates a GitHub Release, registers the tag on `main`, and publishes an immutable live preview at `/versions/<tag>/`.
- Never move, replace, or recreate a published version tag. Create the next semantic version instead.
- Keep the Pages assembly rooted at `ready-for-develop/`; the workflow-generated `public/` directory must not be committed.
- `.github/published-version-tags.txt` is the small automation registry that gives every release-triggered Pages deployment a unique `main` commit. Do not remove released tags from it.

## Before finishing a page change

- Confirm that every local image, video, stylesheet, script, font, and download referenced by every route or its CSS exists inside `ready-for-develop/`.
- Keep `ready-for-develop/README.md` and `ready-for-develop/CONTENT-PLAN.md` in sync when the handoff structure or page content changes.
- Verify the homepage and every top-level route locally before finishing.
- GitHub Pages deployment is configured in `.github/workflows/deploy-pages.yml`; releases are configured in `.github/workflows/release.yml`.
