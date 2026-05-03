# Content sources

> Language: **English** | [فارسی](../fa/CONTENT_SOURCES.md)


## Recommended publishing channels

Use more than one channel so users can still get content when one path fails.

Recommended channels:

- GitHub branch `IR-packages`
- GitHub Releases
- Self-hosted Git mirror
- Telegram channel announcements
- Local share between users
- USB or LAN file transfer

## What belongs in a package source

A package source should contain:

```text
packages.index.json
packages/
  package-name.azsos
```

The registry gives AZSOS metadata before download. The `.azsos` file remains the source of truth for verification.

## Versioning packages

Use clear package versions such as:

```text
0.1.0
2026.05.03
2026.05.03-1
```

Update the registry whenever packages change.

## Source hygiene

- Do not publish private signing keys.
- Keep package names stable.
- Prefer small focused packages.
- Add source and review metadata inside each package when possible.
