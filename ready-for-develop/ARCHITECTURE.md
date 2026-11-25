# Static website architecture

## Ownership rule

Every file should have one clear scope:

- **Route:** a top-level directory containing the HTML entry point for a public URL.
- **Shared:** website-wide presentation or behavior used by several routes.
- **Module:** code and assets owned by one page or feature.

The route is intentionally thin: it composes shared UI with one or more modules. This makes the current static prototype easy to hand off and gives a future framework implementation explicit component boundaries.

## Adding a page

1. Create `<route>/index.html` at the website root.
2. Create `modules/<feature>/` for that page's styles, scripts and media.
3. Use existing resources from `shared/`; do not duplicate the header, fonts or logos.
4. Add the route once to `shared/scripts/site-shell.js`.
5. Keep all asset and navigation paths relative.
6. Verify the route at the latest path and at `/versions/<tag>/<route>/` before releasing.

Program detail pages are nested under `/programs/<program-name>/` and keep their page-owned implementation in `modules/<program-name>/`. The Programs item in the shared shell exposes these detail pages as subroutes.

## URL behavior

GitHub Pages serves directory indexes, giving clean URLs such as `/programs/`. The same tree is copied beneath each version directory. Relative `data-base` values make shared navigation independent of the repository subpath and the selected version.

## Release behavior

`main` is the editable latest site. A `v*` tag captures an immutable commit. The release workflow creates a matching GitHub Release, records the tag in `.github/published-version-tags.txt` on `main` and explicitly starts the Pages deployment. The deployment copies the latest source to the site root and extracts every version tag's `ready-for-develop/` tree into `/versions/<tag>/`.

The registry gives the release deployment a distinct commit SHA. This matters when the tag and the latest branch initially share a commit. The explicit dispatch starts Pages after the registry update because the automation's push cannot trigger another push workflow.
