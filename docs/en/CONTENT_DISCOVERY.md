# Content discovery

> Language: **English** | [فارسی](../fa/CONTENT_DISCOVERY.md)


## Goal

Content discovery lets AZSOS find `.azsos` packages without requiring a central server. A source can be a GitHub branch, a release page, a direct file, a local folder, or a registry JSON file.

## Default source

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

AZSOS tries the lightweight methods first:

1. Look for `packages.index.json`.
2. Parse GitHub tree pages when possible.
3. Use GitHub API only as a fallback.
4. Try GitHub Releases as a best-effort fallback.

## Source types

### GitHub tree

Example:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Best layout:

```text
packages.index.json
packages/
  first-aid.azsos
  digital-safety.azsos
```

### Direct `.azsos` link

A URL that ends in `.azsos` can be installed directly after verification.

### Registry JSON

A `packages.index.json` file lists package metadata and download URLs. It is the most reliable discovery method.

### Local folder

A folder source lets AZSOS scan `.azsos` files from disk, USB, or an extracted archive.

## Discovery is not trust

A package found in a catalog is not automatically trusted. AZSOS verifies the file before installing it.
