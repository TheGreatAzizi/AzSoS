# Registry format

> Language: **English** | [فارسی](../fa/REGISTRY.md)


## Purpose

`packages.index.json` helps AZSOS discover packages quickly and avoid expensive GitHub API calls.

## Example

```json
{
  "format": "azsos.registry.v1",
  "source_name": "azsos-ir-packages",
  "generated_at": "2026-05-03T12:00:00Z",
  "packages": [
    {
      "id": "first-aid.fa.basic",
      "title": "First Aid Basic",
      "version": "0.1.0",
      "language": "fa",
      "url": "packages/first-aid.azsos",
      "sha256": "..."
    }
  ]
}
```

## Relative URLs

A package URL may be relative to the registry location. This makes the branch easier to mirror.

## Registry trust

The registry helps discovery, but package verification still happens after download.
