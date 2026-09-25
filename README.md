# 6g-rupa-website

Website for 6G-RUPA, published at <https://6grupa.com>.

Built with [Hugo](https://gohugo.io) (extended, 0.146 or newer; CI uses 0.149.0)
and its own templates in `layouts/`. There is no external theme.

## Run locally

```sh
hugo server
```

## Where things live

```
content/                 Markdown pages: about, research, contact, news/, posts/ (articles)
content/_index.md        Home page hero text (deck in front matter, intro in the body)
data/publications.yaml   Papers, preprints, posters and talks (home page and /research/)
data/software.yaml       Software and datasets, listed on /research/
assets/img/research/     Publication pages, logos and screenshots used by those two files
layouts/                 Page templates, partials, shortcodes and Markdown render hooks
layouts/_partials/layer-diagram.html   The recursive layer diagram on the home page
assets/css/main.css      All styles; colour tokens for light and dark at the top
assets/img/og.png        Link-preview image for social cards
static/fonts/            Self-hosted Archivo and Source Serif 4 (SIL OFL)
```

## Writing

- **News**: add a page bundle under `content/news/` with `title`, `description`
  and `date`. The description is shown in lists and under the title.
- **Articles**: add a page bundle under `content/posts/` with
  `categories: ["Article"]`; the articles list only shows that category.
- **Publications**: add an entry to `data/publications.yaml` with `kind` set
  to `paper`, `preprint`, `poster` or `talk`. On a page, list them with
  `{{< publications >}}` or filter: `{{< publications kind="poster,talk" >}}`.
- **Software and data**: add an entry to `data/software.yaml`; `{{< software >}}`
  lists them.
- **Pictures**: put the image in `assets/img/research/` and reference it with
  `image:` in either file (see the comments at the top of each for `visual`,
  `logo`, `video` and `fit`). To make a page thumbnail from a PDF:
  `pdftoppm -f 1 -l 1 -r 100 -png -singlefile paper.pdf assets/img/research/name`.

Shortcodes: `pdf` (embedded PDF with open/download buttons), `publications`,
`software`, and `alert` (a highlighted note).

Terminology: the site names the architecture's layers "N Layer" and
"N−1 Layer", as in the papers; avoid "DIF".
