# AZSOS Package Format

Current format: `azsos.v1`

A `.azsos` file is a ZIP archive. The extension is part of the user-facing format, but ZIP keeps the package easy to inspect and copy.

## Required files

```text
manifest.json
hashes.json
signature.ed25519
```

## Common files

```text
search.sqlite
content/
  index.html
  pages/
  assets/
```

## `manifest.json`

```json
{
  "format": "azsos.v1",
  "id": "first-aid.fa.demo",
  "title": "First Aid Demo",
  "language": "fa",
  "version": "0.1.0",
  "created_at": "2026-05-03T00:00:00+00:00",
  "publisher": {
    "name": "AZSOS Demo Publisher",
    "public_key": "base64-ed25519-public-key",
    "fingerprint": "ABCD 1234 ..."
  },
  "entry": "content/index.html",
  "search_index": "search.sqlite",
  "size_bytes": 123456,
  "min_app_version": "0.1.0"
}
```

## Hashing

`hashes.json` maps package-relative file paths to SHA-256 hex digests. `manifest.json` is included in the hash map. `hashes.json` and `signature.ed25519` are not included in the hash map.

## Signing

`signature.ed25519` signs the canonical JSON payload:

```json
{
  "manifest": { "...": "..." },
  "hashes": { "...": "..." }
}
```

Canonical JSON uses UTF-8, sorted keys, and compact separators.

## Path safety

Package paths must be relative and must not contain absolute paths, empty path parts, `.` path parts, or `..` path parts.
