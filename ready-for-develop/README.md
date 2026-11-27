# AMAkids franchise website

This folder is the handoff package and canonical source for the static AMAkids franchise website. GitHub Pages publishes it from `main`. The website is intentionally framework-free so another development team can open, inspect and migrate each module without a build step.

## Local preview

Run `make dev` from the repository root or run **AMAkids: Start local site** in VS Code (`⌘⇧B` on macOS). The server uses `ready-for-develop/` as the web root.

Open the [homepage](http://127.0.0.1:4173/) or [Mental Arithmetic page](http://127.0.0.1:4173/programs/mental-arithmetic/). Refresh after edits. Use `make dev PORT=4174` for a different port.

## Architecture

```text
ready-for-develop/
├── index.html                         # homepage
├── partnership-models/index.html      # route placeholder
├── programs/index.html                # program catalogue
├── programs/mental-arithmetic/        # first complete program subroute
├── resources/index.html               # franchise guide library
├── platform/index.html                # route placeholder
├── partnership-proposal/index.html    # route placeholder
├── shared/                            # site-wide shell and assets
│   ├── assets/brand/
│   ├── fonts/
│   ├── scripts/site-shell.js          # shared header and route map
│   └── styles/
└── modules/
    ├── franchise-landing/             # homepage-owned implementation
    │   ├── downloads/
    │   ├── images/
    │   ├── scripts/
    │   ├── styles/
    │   └── videos/
    └── mental-arithmetic/             # program-page images, styles and behavior
```

Use `shared/` only for reusable website-wide code and assets. Give every substantial new page or feature its own directory under `modules/`. Routes remain at the web root and load their shared and module-specific resources with relative paths.

The header is rendered from `shared/scripts/site-shell.js`. Its route list is the single navigation source for the current static prototype. Every route identifies its active item with `data-route` and supplies a relative `data-base`, so the same source works under both the latest URL and a versioned preview.

## Current routes

- `/` — full franchise landing page.
- `/partnership-models/` — future partnership-model detail page.
- `/programs/` — program catalogue and parent route.
- `/programs/mental-arithmetic/` — Mental Arithmetic program page for partners, teachers and families.
- `/resources/` — dedicated Franchise Guides & Resources library, linked from the homepage and shared navigation.
- `/platform/` — future platform and CRM page.
- `/partnership-proposal/` — future commercial proposal page.

The partnership-model, platform and partnership-proposal routes remain deliberate design placeholders. The program catalogue now exposes the first completed child route without inventing content for the remaining program pages.

## Lead form

The homepage franchise form is a prototype flow: it asks for name, email, phone/WhatsApp, country and partnership model, prepares an email draft and downloads the presentation after submission. It does not save leads to a server or CRM. The B2C trial-lesson CTA opens the original `data-open-form="offline"` handler when present; without the Yii form in this local preview, it opens a demo dialog that does not submit or store a request. Keep the existing Yii booking form connected on the live franchise branch.

The franchise landing page mirrors the current visible structure of [amakids.com/franchise](https://amakids.com/franchise/), including its network figures and program age ranges. `Franchise Guides & Resources` is a separate route; article thumbnails are hosted locally and article links open the original AMAkids posts. Recheck live copy and figures before publishing, as the source page can change.

The Programs dropdown currently lists only the ready Mental Arithmetic page. English and Memorika will be added after their partner-facing pages are prepared. The homepage hero and partnership-format cards use locally stored 1536×1024 WebP illustrative images in `modules/franchise-landing/images/partnership/`; they are generated representations, not documentary photos of actual AMAkids partners or students.

The Mental Arithmetic page links to the AMAkids platform demo and the partnership models on the homepage.

The homepage Mental Arithmetic card and the shared Programs dropdown both open `/programs/mental-arithmetic/`. The course page's Franchise navigation returns to the homepage, so visitors can move between the program details and the partner offer.

## Mental Arithmetic program page

The course page uses its original program header, with dedicated assets and styles in `modules/mental-arithmetic/`. It covers the soroban method, skills, Junior and Senior tracks, age groups, the roadmap, what the program offers and frequently asked questions. The hero uses an illustrative classroom image. Photos of partner classrooms and AMAkids events appear below the learning materials. The materials section includes locally hosted Workbooks & Augmented Reality and Inside the AMAkids Platform videos. The two materials videos play on click. The method section has a silent, looping digital abacus animation with a still image for visitors who prefer reduced motion. See [CONTENT-PLAN.md](CONTENT-PLAN.md#страница-mental-arithmetic) for the editorial plan.

## Deployment and versioning

- Pushes to `main` publish the latest site at `https://annaadragun.github.io/amakids-franchise-landing/`.
- Annotated tags matching `v*` create a GitHub Release and publish that exact source under `https://annaadragun.github.io/amakids-franchise-landing/versions/<tag>/`.
- GitHub automatically attaches ZIP and TAR source archives to every release.
- Published tags are permanent snapshots. Make changes on `main`, then create a new semantic version tag such as `v0.2.0`.
- Release automation records the tag in `.github/published-version-tags.txt` on `main` and explicitly starts the Pages deployment.
- The Pages deployment adds `noindex, noimageindex` to the HTML it serves at the latest and versioned URLs. This keeps the pages accessible by direct link while opting out of search indexing.

To publish a version, push the release commit to `main`, then create and push an annotated tag on that commit. Use the next semantic version and put the release summary in the body of the tag annotation. The release workflow includes it in the GitHub Release notes. After both workflows finish, check the latest site and the versioned link from the release.

The workflows are `.github/workflows/deploy-pages.yml` and `.github/workflows/release.yml`. Local preview requires no Python, Node, package manager or generated build output.
