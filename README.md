# AMAkids franchise site

Open this repository folder in VS Code and press `⌘⇧B` on macOS to run **AMAkids: Start local site**. From a terminal in the repository root, run `make dev`. The preview uses Ruby and Make.

- [Local homepage](http://127.0.0.1:4173/)
- [Local Mental Arithmetic page](http://127.0.0.1:4173/programs/mental-arithmetic/)
- [Latest published site](https://annaadragun.github.io/amakids-franchise-landing/)
- [GitHub Releases and versioned previews](https://github.com/annaadragun/amakids-franchise-landing/releases)

Refresh the browser after editing. Stop the server with `Ctrl+C` in its terminal. If port 4173 is busy, run `make dev PORT=4174` and use the URLs printed in the terminal.

Site files live in [`ready-for-develop/`](ready-for-develop/). See the [site documentation](ready-for-develop/README.md) for routes, source layout and release steps.
