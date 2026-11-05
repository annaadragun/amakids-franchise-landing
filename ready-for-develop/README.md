# AMAkids franchise landing page

This folder is the handoff package and the canonical source for the static landing page. Make page and asset changes here. GitHub Pages deploys this folder from the `main` branch.

The hero now summarizes the launch toolkit (methodology, team training, platform and CRM). Repeated advantage cards and the duplicate partnership steps have been removed; the page keeps one three-step path to a conversation.

## Preview locally

Open `ready-for-develop/index.html` with VS Code Live Server, or serve this folder as the web root. All page assets use relative paths, so the package also works under a project subpath.

## Structure

- `index.html` — landing page markup.
- `assets/css/franchise.css` — page styles; custom fonts are in `assets/fonts/`.
- `assets/js/franchise.js` — navigation, lead form and presentation download behavior.
- `assets/images/` — logos, page photography, event photos and video covers. Editable cover artwork is in `posters/covers/*.svg`; the page uses matching JPG files.
- `assets/videos/` — the five videos used on the page.
- `assets/downloads/` — production partnership presentation PDF and its editable PPTX source.
- `CONTENT-PLAN.md` — current page structure, content boundaries and FAQ notes.

## Lead form note

The current form is a local-preview flow: it prepares an email draft and downloads the presentation after submission. It does not save leads to a server or CRM. Connect an approved form endpoint before using it for production lead capture.

## Deployment

The GitHub Actions workflow at `.github/workflows/deploy-pages.yml` publishes this folder on pushes to `main`. Keep production page changes and required assets inside `ready-for-develop`.
