# AMAkids franchise website

This folder is the handoff package and canonical source for the static AMAkids franchise website. GitHub Pages publishes it from `main`. The website is intentionally framework-free so another development team can open, inspect and migrate each module without a build step.

## Local preview

Serve `ready-for-develop/` as the web root. For example, with Ruby already available on macOS:

```sh
ruby -run -e httpd ready-for-develop -p 4173
```

Then open `http://localhost:4173/`. Opening HTML files directly is possible, but a local server mirrors routing more accurately.

## Architecture

```text
ready-for-develop/
├── index.html                         # homepage
├── partnership-models/index.html      # route placeholder
├── programs/index.html                # route placeholder
├── platform/index.html                # route placeholder
├── partnership-proposal/index.html    # route placeholder
├── shared/                            # site-wide shell and assets
│   ├── assets/brand/
│   ├── fonts/
│   ├── scripts/site-shell.js          # shared header and route map
│   └── styles/
└── modules/
    └── franchise-landing/             # homepage-owned implementation
        ├── downloads/
        ├── images/
        ├── scripts/
        ├── styles/
        └── videos/
```

Use `shared/` only for reusable website-wide code and assets. Give every substantial new page or feature its own directory under `modules/`. Routes remain at the web root and load their shared and module-specific resources with relative paths.

The header is rendered from `shared/scripts/site-shell.js`. Its route list is the single navigation source for the current static prototype. Every route identifies its active item with `data-route` and supplies a relative `data-base`, so the same source works under both the latest URL and a versioned preview.

## Current routes

- `/` — full franchise landing page.
- `/partnership-models/` — future partnership-model detail page.
- `/programs/` — future program catalogue.
- `/platform/` — future platform and CRM page.
- `/partnership-proposal/` — future commercial proposal page.

The four secondary routes are deliberate design placeholders. They establish navigation and ownership boundaries without inventing approved copy.

## Lead form

The homepage form is a prototype flow: it prepares an email draft and downloads the presentation after submission. It does not save leads to a server or CRM. Connect an approved endpoint before production lead capture.

## Deployment and versioning

- Pushes to `main` publish the latest site at `https://annaadragun.github.io/amakids-franchise-landing/`.
- Tags matching `v*` create a GitHub Release and publish that exact source under `https://annaadragun.github.io/amakids-franchise-landing/versions/<tag>/`.
- GitHub automatically attaches ZIP and TAR source archives to every release.
- Published tags are permanent snapshots. Make changes on `main`, then create a new semantic version tag such as `v0.2.0`.
- Release automation records the new tag in `.github/published-version-tags.txt`; that small `main` commit triggers the Pages rebuild without committing generated site copies.

The workflows are `.github/workflows/deploy-pages.yml` and `.github/workflows/release.yml`. No Python, Node, package manager or generated build output is required.
