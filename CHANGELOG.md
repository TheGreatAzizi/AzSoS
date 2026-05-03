# Changelog

## 0.3.5

- Improved the in-app Docs tab with Markdown-style rendering.
- Added styled headings, lists, code blocks, inline code, links, checklists, and callouts.
- Rewrote the in-app English manual to be friendlier and easier to scan.
- Added a Copy Markdown action for documentation topics.

## 0.3.4

- Changed in-app Docs content to English.
- Added bilingual GitHub documentation indexes.
- Added English user, publishing, GitHub publishing, and update docs.
- Updated README with English and Persian sections.

## 0.3.3

- Added an in-app **Docs / راهنما** tab with a full Persian manual.
- Added searchable documentation topics inside the desktop UI.
- Added copy/save/open-docs actions for the manual.
- Added `docs/IN_APP_MANUAL_FA.md` for the same guide in repository form.


## 0.3.2

### Changed
- Default package source changed to `https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages`.
- Existing configs that still point to the old `AzSoS-` repo are migrated to the new default source when loaded.

### Added
- Added **Check updates** button in the desktop app.
- Default app update source: `https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE`.
- App update discovery supports `update.index.json`, direct `.exe` / `.msi` / `.zip` files on the UPDATE branch, and GitHub Releases as best-effort fallback.
- App update files are downloaded to `~/AZSOS/updates/` and are not auto-run.
- Added `docs/UPDATES_FA.md` and `publish-template/UPDATE/`.

## 0.3.1

- Avoid GitHub API rate-limit failures by trying branch `packages.index.json` first.
- Add non-API GitHub HTML tree scanner for public `.azsos` files.
- Make GitHub Releases discovery best-effort so one rate-limited API endpoint does not block branch packages.
- Support `AZSOS_GITHUB_TOKEN` / `GITHUB_TOKEN` for authenticated GitHub API calls.
- Support relative package URLs inside `packages.index.json`.
- Add Persian GitHub publishing guide.

## 0.3.0

- Added multi-source content discovery in the desktop app.
- Added support for direct `.azsos` URLs, local folders, registry JSON, GitHub trees, and GitHub Releases.
- Added remote package inspection before install.
- Added multi-select remote install.
- Added installed package export.
- Added local trusted publisher fingerprints.
- Added CLI catalog commands and registry generation.
- Added Persian user and publishing guides.

## 0.2.0 - 2026-05-03

### Added
- Default GitHub content source for IR packages.
- Desktop catalog panel for fetching remote `.azsos` packages.
- Support for GitHub branch/tree `.azsos` discovery and GitHub Release asset discovery.
- Support for custom GitHub/registry source URLs saved in `~/AZSOS/config.json`.
- Remote download, verify, and install flow from inside the app.
- Delete installed package action in the desktop app.
- `azsos_core.catalog` module and content discovery documentation.
- Copy/paste context menus and keyboard shortcuts for desktop fields.
- Read-only copyable Local Share URL field and Copy URL button.
- Get content dialog explaining package distribution flows.
- Content-source and registry documentation plus an example package index.

## 0.1.0 - Initial alpha

- Windows desktop MVP.
- `.azsos` package format.
- CLI: keygen, pack, verify, install, list, search, serve.
- SHA-256 hash verification.
- Ed25519 package signatures.
- SQLite FTS5 offline search.
- Local Wi-Fi/hotspot share server.
- QR code for local share URL.
- Sample first-aid package.
