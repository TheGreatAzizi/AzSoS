# AZSOS package format

> Language: **English** | [فارسی](../fa/FORMAT.md)


## Overview

An `.azsos` file is a ZIP archive with a strict internal structure. The current format identifier is:

```text
azsos.v1
```

## Required files

```text
manifest.json
hashes.json
signature.ed25519
content/
```

Optional file:

```text
search.sqlite
```

## Example structure

```text
first-aid.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
    index.html
    pages/
      burns.html
```

## manifest.json

The manifest describes the package.

```json
{
  "format": "azsos.v1",
  "id": "first-aid.fa.demo",
  "title": "First Aid Demo",
  "version": "0.1.0",
  "language": "fa",
  "publisher": {
    "name": "AZSOS Demo Publisher",
    "public_key": "base64-ed25519-public-key"
  },
  "entry": "content/index.html"
}
```

## hashes.json

The hashes file stores SHA-256 hashes for package files.

```json
{
  "content/index.html": "sha256-...",
  "search.sqlite": "sha256-..."
}
```

## signature.ed25519

The signature proves that the manifest and hash list were signed by the publisher key.

## Safety rules

- Do not allow files to extract outside the install directory.
- Do not execute JavaScript from package content.
- Do not make network requests from package content.
- Treat every package as untrusted until verification succeeds.
