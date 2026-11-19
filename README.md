# resume.hanskruse.eu

The resume of Hans Kruse. GitHub Pages builds it with its own Jekyll from the YAML in `_data/data.yml`; there is no
hand-written page. Edit the text in `_data/data.yml`, the links to the other sites in `_data/links.yml`.

## Layout

* `_layouts/default.html` and `_includes/`: Liquid templates that turn the data into HTML (one include per section).
* `style.css`, `menu.js`, `hero-bg.svg` and `favicon.svg`: shared with the playbook sites and hanskruse.eu (bar with
  hamburger menu, wave banner, light and dark scheme). `assets/css/resume.css` holds the resume additions.
* No third-party scripts, styles or fonts are loaded at runtime.

## Building locally

```bash
jekyll serve          # http://127.0.0.1:4000
jekyll build --strict_front_matter --destination /tmp/resume-site
```

`jekyll` is installed on kos by `dev-setup.yml` of the kos playbook repository.

## Linting and hooks

Run `./githooks-setup.sh` once per checkout. Never bypass the hooks with `--no-verify`. The hooks refuse to run when a
tool is missing (`gitleaks`, `yamllint`, `actionlint`, `jekyll`, `trufflehog`, `osv-scanner`).

* `pre-commit`:
  * `gitleaks` on the staged changes;
  * `yamllint` (`.yamllint`; `_data/data.yml` only has to be valid YAML) and `actionlint` for the workflows;
  * a strict test build with Jekyll into a temporary directory (a warning fails the commit);
  * the third-party policy `.githooks/check-third-party.py`, which works offline. It fails on vendored libraries in the
    source (`assets/plugins`, `vendor/`, `node_modules/`, `*.min.js`, `*.min.css`) and on any script, stylesheet, font,
    image, media or frame in the built site that is not same-origin. `mailto:`, `tel:` and plain links are allowed.
* `pre-push`: `trufflehog` on the commits being pushed and `osv-scanner scan source --recursive .` for known
  vulnerabilities in dependencies (needs network; exit code 128, "no package sources", is accepted).

`markdownlint-cli2` checks this README (`.markdownlint-cli2.yaml`). `.github/dependabot.yml` updates the pinned GitHub
Actions monthly; the site has no other dependencies.

## Deploying

`.github/workflows/pages.yml` builds the site with `actions/jekyll-build-pages` and deploys it on every push to `main`
(Settings > Pages > Source: GitHub Actions). `CNAME` keeps the domain `resume.hanskruse.eu`.

## Credits and licence

Based on Orbit by Xiaoying Riley at [3rd Wave Media](https://themes.3rdwavemedia.com/), released under
[Creative Commons Attribution 3.0](https://creativecommons.org/licenses/by/3.0/), as a Jekyll theme by
[webjeda](https://github.com/sharu725/online-cv) under the [MIT licence](LICENSE.txt). The styling is now the style of
the other sites of the author; the section structure of the templates is still derived from that theme.
