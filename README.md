# My Professional Blog — Quarto Project

A clean, modern, responsive personal blog built with [Quarto](https://quarto.org).

---

## Required Assets (add before first render)

Place these files before running `quarto preview`:

| Path | Description |
|------|-------------|
| `assets/images/favicon.ico` | Site favicon (32×32 px recommended) |
| `assets/images/logo.png` | Navbar logo (height rendered at 36 px) |
| `assets/images/profile.jpg` | Your photo for the About page |
| `articles/operating-systems/post-1/thumbnail.png` | Cover image for Post 1 (16:9 ratio) |
| `articles/python-ds/post-2/thumbnail.png` | Cover image for Post 2 (16:9 ratio) |

Quick placeholder generation (requires ImageMagick):

```bash
# Favicon placeholder
convert -size 32x32 xc:#3B82F6 assets/images/favicon.ico

# Logo placeholder
convert -size 120x36 xc:#3B82F6 assets/images/logo.png

# Profile photo placeholder
convert -size 400x400 xc:#10B981 assets/images/profile.jpg

# Post thumbnails
convert -size 800x450 xc:#F59E0B articles/operating-systems/post-1/thumbnail.png
convert -size 800x450 xc:#EF4444 articles/python-ds/post-2/thumbnail.png
```

---

## Setup & Deploy

### Prerequisites

```bash
quarto --version   # Must be >= 1.4.0
```

Download Quarto from <https://quarto.org/docs/get-started/>.

### Install Python dependencies

```bash
pip install jupyter pandas matplotlib
```

### Local preview

```bash
quarto preview
```

Quarto starts a live-reload server at `http://localhost:4848` (port may vary).

### Full render

```bash
quarto render
```

Output lands in `_site/`. Open `_site/index.html` in a browser to verify locally.

### Deploy to Quarto Pub

```bash
quarto publish quarto-pub
```

Free hosting at `https://YOUR_USERNAME.quarto.pub/my-blog`.

### Deploy to GitHub Pages

```bash
quarto publish gh-pages
```

Pushes the rendered site to the `gh-pages` branch of your repository. Enable Pages in your
repo settings → Pages → Source: `gh-pages` branch.

### Deploy to Netlify

```bash
quarto publish netlify
```

Connects to your Netlify account and deploys automatically.

---

## Customisation Quick Reference

| What to change | Where |
|---|---|
| Site title / description | `_quarto.yml` → `website.title` / `website.description` |
| Social links | `_quarto.yml` → `website.navbar.right` and `website.page-footer` |
| Brand colours | `styles/variables.scss` → `$primary`, `$secondary`, `$accent` |
| Fonts | `styles/variables.scss` → `$font-heading`, `$font-body` |
| Analytics | `_quarto.yml` → uncomment `google-analytics` |
| New post | Create `articles/TOPIC/post-X/index.qmd` |

---

## Project Structure

```
my-blog/
├── _quarto.yml              # Site-wide configuration
├── index.qmd                # Home page
├── about.qmd                # About page
├── articles/
│   ├── index.qmd            # Blog listing (auto-generated grid)
│   ├── operating-systems/
│   │   ├── index.qmd
│   │   └── post-1/
│   ├── python-ds/
│   │   ├── index.qmd
│   │   └── post-2/
│   └── career-writing/
│       ├── index.qmd
│       └── post-3/
├── styles/
│   ├── variables.scss       # Design tokens (colours, type, spacing)
│   └── main.scss            # All component styles
└── assets/
    └── images/
        ├── favicon.ico
        ├── logo.png
        └── profile.jpg
```
