# GeoLab Library

Source for the EarthScope Community Library at
[docs.earthscope.org/library](https://docs.earthscope.org/library): a
searchable gallery of notebooks and images that run in GeoLab.

Each project is one YAML file in [`projects/`](projects/). The site is built
with [MyST](https://mystmd.org) and deployed by Netlify.

## Add a project

Copy [`template.yml`](template.yml) into `projects/`, fill it in, and open a
pull request. See [`welcome.md`](welcome.md) for contributor instructions.

| Field | Used for |
|-------|----------|
| `title` | Card title |
| `author` | Author names (clickable filter) |
| `summary` | Card description (searched) |
| `tags` | Tag chips (clickable filters) |
| `thumbnail` | Card image: a full URL, or a path in the `github` repo |
| `nbgitpuller` | Where the card and "Open in GeoLab" link to |
| `github` | "Source" link, and base for a relative `thumbnail` |

The remaining template fields (`recommended_image`, `citation`, …) are not
shown on the card yet.

## Run locally

Needs Node (for MyST) and Python 3. The only Python dependency is PyYAML,
pinned to 6.x in [`requirements.txt`](requirements.txt). It's used by the
build plugin and both scripts; Netlify installs it automatically. Install
it into the `python3` on your PATH, since MyST runs `library_listing.py`
with that interpreter.

```bash
pip install -r requirements.txt
npx mystmd@~1.10.1 start        # http://localhost:3000/project-tiles
```

`~1.10.1` matches what Netlify installs (see
[`build-docs.sh`](https://github.com/EarthScope/docs.earthscope.org/blob/main/scripts/build-docs.sh)).
Restart `myst start` after adding or editing files in `projects/`.

`npx mystmd@~1.10.1 build --html` writes a static site to `_build/html/`.

## Test with many projects

[`scripts/make_dummy_projects.py`](scripts/make_dummy_projects.py) writes fake
projects, plus copies of the real ones, to `.dummy-projects/` (git-ignored).
Point the build at that folder with `GEOLAB_PROJECTS_DIR`:

```bash
python scripts/make_dummy_projects.py --count 1000
GEOLAB_PROJECTS_DIR=.dummy-projects npx mystmd@~1.10.1 start
```

Options: `--count N` (default 1000), `--seed N` (same seed, same data),
`--out DIR`. Re-running replaces the folder.

About 70% of dummy projects get a real image from picsum.photos (to see lazy
loading), 20% none, and 10% a broken URL (to see the fallback letter).

## Audit tags

[`scripts/audit_tags.py`](scripts/audit_tags.py) lists every tag with its
count and the files using it, and suggests merges. Run it when reviewing a
new project PR:

```bash
python scripts/audit_tags.py                  # tags in projects/
python scripts/audit_tags.py --field author   # same checks for author names
```

It reports:

- **Variants**: tags that differ only in case, spaces, `-` or `_`
  (`earthscope_sdk` / `EarthScope SDK`).
- **Plurals**: `earthquake` / `earthquakes`.
- **Similar**: likely typos (`seismolgy` / `seismology`). These are fuzzy
  matches, so check them first. `--cutoff` (default 0.85) sets how close two
  tags must be.
- **Used once**: tags on a single project that weren't flagged above. They
  may be too specific.

For each group it suggests the most-used spelling and says "tie: pick one"
when the counts are equal. It never edits files: fix the tags in the project
YAML by hand. It does not match initials against full names (`S. Parafina` /
`Sophia Parafina`).

## How it works

```
projects/*.yml ──► library_listing.py ──► {geolab-library} widget ──► browser
                   (MyST transform:        (plugins/geolab-library.mjs:
                    YAML → item list)       search, filters, paging)
```

1. [`project_tiles.md`](project_tiles.md) contains a `{geolab-library}`
   directive. The directive, defined in
   [`plugins/geolab-library.mjs`](plugins/geolab-library.mjs), outputs an
   empty [anywidget](https://mystmd.org/guide/widgets) node.
2. [`library_listing.py`](library_listing.py) is a MyST executable plugin.
   At build time it reads every project YAML file and puts the list into
   that widget's `model.items`.
3. In the browser, the `render` function in `geolab-library.mjs` draws the
   gallery from that list:
   - ranked text search over title, summary, authors and tags
   - tag and author filters (click any chip or author name)
   - 24 cards at a time with "Show more"; only those cards are in the DOM
   - thumbnails with `loading="lazy"`, and a letter placeholder if missing
   - filter state in the URL (`?q=…&tag=…&author=…`) for sharing links
   - light/dark colors that follow the site theme

Both plugins are in this repo, so the build has no plugin downloads.

The whole project list is embedded in the page: about 460 KB (42 KB
gzipped) for 1000 projects. That's fine up to several thousand. Beyond that,
move the list into a separate JSON file the widget fetches. MyST only copies
a widget's `esm` and `css` files into the site, so that would need its own
build step.

## History

1. **`generate_tiles.py`** (up to `4d79449`). A pre-build script wrote
   `project_tiles.md` as raw HTML cards. It relied on a `tiles.js` injected
   by patching the theme's `server.js` for search and tag clicks. That never
   worked: the file didn't exist, and the static Netlify build doesn't use
   `server.js`. MyST also strips inputs and event handlers from raw HTML.
2. **myst-listing + searchfilter** (`ef5af25`). The same approach as the
   [Pythia cookbook gallery](https://github.com/ProjectPythia/cookbook-gallery):
   `library_listing.py` fed the
   [myst-listing](https://github.com/myst-contrib/myst-listing) gallery, and
   [searchfilter](https://github.com/jupyter-book/myst-plugins/tree/main/plugins/searchfilter)
   filtered it. Search worked, but every card was rendered up front, with
   no paging, no lazy images and no tag filters. We also vendored both
   plugins, which have no declared license.
3. **Custom widget** (current). Replaces both plugins with
   `plugins/geolab-library.mjs`, built to handle thousands of projects.
   Tested with 1000 dummy projects.
