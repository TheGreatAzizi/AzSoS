# Package authoring

> Language: **English** | [فارسی](../fa/PACKAGE_AUTHORING.md)


## Content folder

A package content folder should contain static files:

```text
content/
  index.html
  pages/
    intro.html
  assets/
    image.webp
```

The entry file is usually `content/index.html`.

## Writing content

Good AZSOS content is:

- short
- source-aware
- offline-friendly
- readable on small screens
- useful without external links

## Avoid

- remote scripts
- remote fonts
- tracking pixels
- huge images
- content without attribution

## Search

The packer can include a SQLite FTS5 index. Keep page titles clear because search results often show the title first.

## Metadata

Where possible, include review dates and sources inside the content itself:

```text
Reviewed: 2026-05-03
Source: Example public guide
```
