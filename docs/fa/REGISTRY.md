# فرمت Registry

> زبان: **فارسی** | [English](../en/REGISTRY.md)


## هدف

`packages.index.json` به AZSOS کمک می‌کند بسته‌ها را سریع پیدا کند و کمتر به GitHub API وابسته شود.

## نمونه

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

## URL نسبی

URL بسته می‌تواند نسبت به محل registry نسبی باشد. این کار mirror کردن branch را ساده‌تر می‌کند.

## اعتماد به registry

registry برای کشف بسته است، اما verify اصلی بعد از دانلود خود بسته انجام می‌شود.
