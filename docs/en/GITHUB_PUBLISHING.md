# GitHub publishing

> Language: **English** | [فارسی](../fa/GITHUB_PUBLISHING.md)


## Branches

AZSOS uses two public branches by default:

```text
IR-packages  package catalog and .azsos files
UPDATE       software update files
```

## Package branch

The package branch should contain:

```text
packages.index.json
packages/
  first-aid.azsos
```

AZSOS can fetch from:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

## Why registry JSON matters

A registry avoids GitHub API rate limits and gives AZSOS a stable list of packages. The app tries to read `packages.index.json` before falling back to heavier discovery methods.

## GitHub Releases

GitHub Releases can be used as a fallback publishing channel, especially for stable package collections. Branch-based registry discovery is still recommended for the default source.

## Private keys

Do not commit signing private keys. Keep keys out of the repository and out of release assets.
