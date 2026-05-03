# GitHub Publishing Guide

## Content packages branch

Default content source:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Recommended layout:

```text
IR-packages/
  packages.index.json
  packages/
    first-aid.azsos
    digital-safety.azsos
```

The best discovery path is `packages.index.json`. It is faster and avoids GitHub API rate limits.

## Raw download URLs

For files under `packages/`, use raw URLs like:

```text
https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages/first-aid.azsos
```

## Build the registry

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## GitHub API rate limits

AZSOS tries `packages.index.json` and GitHub HTML pages before using the GitHub API. If GitHub returns `403 rate limit exceeded`, publish a registry file or set `AZSOS_GITHUB_TOKEN` while running the app.
